import bedrock.config


class TestConfigSpec:

    def test_init(self):
        spec = bedrock.config.ConfigSpec('1')
        assert spec.blueprint_id == '1'
