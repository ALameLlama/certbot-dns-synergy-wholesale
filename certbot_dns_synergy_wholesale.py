import logging
from typing import Any, Callable, Optional, Union

from certbot import errors
from certbot.plugins import dns_common
from certbot.plugins.dns_common import CredentialsConfiguration
from zeep import Client, Settings

logger = logging.getLogger(__name__)


class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for Synergy Wholesale (using DNS Hosting)."""

    description = "Obtain certificates using a DNS TXT record (if you are using Synergy Wholesale for DNS)."

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.credentials: Optional[CredentialsConfiguration] = None

    @classmethod
    def add_parser_arguments(
        cls, add: Callable[..., None], default_propagation_seconds: int = 30
    ) -> None:
        super().add_parser_arguments(add, default_propagation_seconds)
        add("credentials", help="Synergy Wholesale credentials INI file.")

    def more_info(self) -> str:
        return (
            "This plugin configures a DNS TXT record to respond to a dns-01 challenge using "
            + "the Synergy Wholesale API."
        )

    @property
    def _provider_name(self) -> str:
        return "synergy_wholesale"

    def _validate(self, credentials) -> None:
        if not credentials.conf("api_key"):
            raise errors.PluginError(
                "Missing property in credentials configuration file {0}: {1}".format(
                    credentials.confobj.filename, "synergy_wholesale_api_key"
                )
            )

        if not credentials.conf("reseller_id"):
            raise errors.PluginError(
                "Missing property in credentials configuration file {0}: {1}".format(
                    credentials.confobj.filename, "synergy_wholesale_reseller_id"
                )
            )

    def _setup_credentials(self) -> None:
        self.credentials = self._configure_credentials(
            "credentials",
            "Synergy Wholesale credentials INI file",
            {
                "reseller_id": "Synergy Wholesale Reseller ID",
                "api_key": "Synergy Wholesale API key",
            },
            self._validate,
        )

    def _perform(self, domain, validation_name, validation) -> None:
        error = self._get_synergy_wholesale_client().add_txt_record(
            domain,
            validation_name,
            validation,
        )

        if error is not None:
            raise errors.PluginError(
                "An error occurred adding the DNS TXT record: {0}".format(error)
            )

    def _cleanup(self, domain, validation_name, validation) -> None:
        error = self._get_synergy_wholesale_client().del_txt_record(
            domain,
            validation,
        )

        if error is not None:
            logger.warn("Unable to find or delete the DNS TXT record: %s", error)

    def _get_synergy_wholesale_client(self) -> "_SynergyWholesale":
        if not self.credentials:
            raise errors.Error("Plugin has not been configured.")
        return _SynergyWholesale(
            self.credentials.conf("reseller_id"), self.credentials.conf("api_key")
        )


class _SynergyWholesale:
    """
    Encapsulates all communication with the Synergy Wholesale API.
    """

    def __init__(self, reseller_id, api_key) -> None:
        self.client = Client(
            "https://api.synergywholesale.com/?wsdl", settings=Settings()
        )

        self.base_request = {
            "resellerID": reseller_id,
            "apiKey": api_key,
        }

    def add_txt_record(self, domain, validation_name, validation) -> Union[str, None]:
        request_data = {
            "domainName": domain,
            "recordName": validation_name,
            "recordType": "TXT",
            "recordContent": validation,
            "recordTTL": 300,
            "recordPrio": 0,
        }

        request_data.update(self.base_request)

        response = self.client.service.addDNSRecord(request_data)

        return None if response["status"] == "OK" else response["errorMessage"]

    def del_txt_record(self, domain, validation) -> Union[str, None]:
        id = self.find_txt_record_id(domain, validation)

        # If we failed to get id, return early
        if id is None:
            return "Failed to find record"

        request_data = {
            "domainName": domain,
            "recordID": id,
        }

        request_data.update(self.base_request)
        response = self.client.service.deleteDNSRecord(request_data)

        return None if response["status"] == "OK" else response["errorMessage"]

    def find_txt_record_id(self, domain, validation) -> Union[str, None]:
        request_data = {"domainName": domain}

        request_data.update(self.base_request)

        response = self.client.service.listDNSZone(request_data)

        # If we failed to get the zone, return early
        if response["status"] != "OK":
            return None

        for record in response["records"]:
            if record["type"] == "TXT" and record["content"] == validation:
                return record["id"]
        return None
