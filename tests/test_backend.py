import bedrock.backend


class TestBackendSpec:

    def test_init(self):
        spec = bedrock.backend.BackendSpec('1')
        assert spec.blueprint_id == '1'
