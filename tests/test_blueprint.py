import bedrock.blueprint


class TestBlueprintSpec:

    def test_init(self):
        spec = bedrock.blueprint.BlueprintSpec('1', 'bedrock/test-blueprint')
        assert spec.blueprint_id == '1'
