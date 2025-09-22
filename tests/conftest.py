import pytest


class FakeService:
    def __init__(self):
        # allow tests to set behavior
        self._add_response = {"status": "OK"}
        self._delete_response = {"status": "OK"}
        self._zone_response = {"status": "OK", "records": []}

    def addDNSRecord(self, request):
        # store last request for assertions
        self.last_add_request = request
        return self._add_response

    def deleteDNSRecord(self, request):
        self.last_delete_request = request
        return self._delete_response

    def listDNSZone(self, request):
        self.last_zone_request = request
        return self._zone_response


class FakeClient:
    def __init__(self, wsdl, settings=None):
        self.wsdl = wsdl
        self.settings = settings
        self.service = FakeService()


@pytest.fixture
def fake_client_class():
    return FakeClient


@pytest.fixture
def fake_psl():
    class _PSL:
        def __init__(self):
            pass

        def privatesuffix(self, domain):
            # naive heuristic for tests; override in tests when necessary
            parts = domain.split(".")
            if len(parts) < 2:
                return None
            # handle a common multi-label TLD like co.uk for tests
            if domain.endswith(".co.uk"):
                base = ".".join(parts[-3:])
                return base
            return ".".join(parts[-2:])

    return _PSL


@pytest.fixture
def patch_module(monkeypatch, fake_client_class, fake_psl):
    """Patch external classes used by the module under test."""
    import certbot_dns_synergy_wholesale as mod

    monkeypatch.setattr(mod, "Client", fake_client_class)
    monkeypatch.setattr(mod, "PublicSuffixList", fake_psl)
    return mod
