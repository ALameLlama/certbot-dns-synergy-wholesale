import pytest
from certbot import errors
from tests.conftest import FakeClient


def test_parse_domain_basic(patch_module):
    mod = patch_module
    client = mod._SynergyWholesale("RID", "API")
    root, sub = client._parse_domain("sub.example.com")
    assert root == "example.com"
    assert sub == "sub"


def test_parse_domain_multilabel_tld(patch_module):
    mod = patch_module
    client = mod._SynergyWholesale("RID", "API")
    root, sub = client._parse_domain("a.b.example.co.uk")
    assert root == "example.co.uk"
    assert sub == "a.b"


def test_parse_domain_invalid_raises(patch_module):
    mod = patch_module
    client = mod._SynergyWholesale("RID", "API")
    with pytest.raises(errors.PluginError):
        client._parse_domain("localhost")


def test_add_txt_record_success(monkeypatch, patch_module):
    mod = patch_module
    client = mod._SynergyWholesale("1234", "KEY")

    service = client.client.service
    service._add_response = {"status": "OK"}

    err = client.add_txt_record("_acme-challenge.sub.example.com", "val")

    assert err is None
    # verify request composition
    req = service.last_add_request
    assert req["domainName"] == "example.com"
    assert req["recordName"] == "_acme-challenge.sub.example.com"
    assert req["recordType"] == "TXT"
    assert req["recordContent"] == "val"
    assert req["recordTTL"] == 300
    assert req["resellerID"] == "1234"
    assert req["apiKey"] == "KEY"


def test_add_txt_record_failure(monkeypatch, patch_module):
    mod = patch_module
    client = mod._SynergyWholesale("1234", "KEY")
    service = client.client.service
    service._add_response = {"status": "ERR", "errorMessage": "boom"}

    err = client.add_txt_record("_acme.example.com", "val")
    assert err == "boom"


def test_del_txt_record_happy_path(monkeypatch, patch_module):
    mod = patch_module
    client = mod._SynergyWholesale("1234", "KEY")
    service = client.client.service
    # discovery returns a TXT with matching content
    service._zone_response = {
        "status": "OK",
        "records": [
            {"id": "42", "type": "TXT", "content": "val"},
            {"id": "99", "type": "A", "content": "1.2.3.4"},
        ],
    }
    service._delete_response = {"status": "OK"}

    err = client.del_txt_record("_acme.example.com", "val")
    assert err is None

    # verify both list and delete got the right requests
    zone_req = service.last_zone_request
    assert zone_req["domainName"] == "example.com"
    assert zone_req["resellerID"] == "1234"

    del_req = service.last_delete_request
    assert del_req["domainName"] == "example.com"
    assert del_req["recordID"] == "42"


def test_del_txt_record_not_found(monkeypatch, patch_module):
    mod = patch_module
    client = mod._SynergyWholesale("1234", "KEY")
    service = client.client.service
    service._zone_response = {"status": "OK", "records": []}

    err = client.del_txt_record("_acme.example.com", "val")
    assert err == "Failed to find record"


def test_find_txt_record_id_error(monkeypatch, patch_module):
    mod = patch_module
    client = mod._SynergyWholesale("1234", "KEY")
    service = client.client.service
    service._zone_response = {"status": "ERR", "errorMessage": "nope"}

    rid = client._find_txt_record_id("example.com", "val")
    assert rid is None


def test_authenticator_validate_missing(creds_missing_field):
    from certbot_dns_synergy_wholesale import Authenticator

    auth = Authenticator(config=object(), name="dns-synergy-wholesale")
    with pytest.raises(errors.PluginError):
        auth._validate(creds_missing_field)


def test_authenticator_validate_ok(creds_ok):
    from certbot_dns_synergy_wholesale import Authenticator

    auth = Authenticator(config=object(), name="dns-synergy-wholesale")
    # should not raise
    auth._validate(creds_ok)


def test_get_client_uses_credentials(creds_ok, monkeypatch):
    import certbot_dns_synergy_wholesale as mod

    # patch Client to our fake to avoid network

    monkeypatch.setattr(mod, "Client", FakeClient)

    auth = mod.Authenticator(config=object(), name="dns-synergy-wholesale")
    auth.credentials = creds_ok
    client = auth._get_synergy_wholesale_client()
    # Ensure base_request contains values from credentials
    assert client.base_request["resellerID"] == creds_ok.conf("reseller_id")
    assert client.base_request["apiKey"] == creds_ok.conf("api_key")


# --------- Helpers / fixtures for Authenticator ---------
class DummyConfObj:
    def __init__(self, filename):
        self.filename = filename


class DummyCreds:
    def __init__(self, data):
        self._data = data
        self.confobj = DummyConfObj("creds.ini")

    def conf(self, key):
        return self._data.get(key)


@pytest.fixture
def creds_missing_field():
    # missing api_key
    return DummyCreds({"reseller_id": "RID"})


@pytest.fixture
def creds_ok():
    return DummyCreds({"reseller_id": "RID", "api_key": "KEY"})
