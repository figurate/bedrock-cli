import bedrock.terraform


class TestTerraformSpec:

    def test_init(self):
        spec = bedrock.terraform.TerraformSpec('1', 'test')
        assert spec.blueprint_id == '1'
        assert spec.instance_name == 'test'
