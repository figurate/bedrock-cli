from .utils import *


class BlueprintSpec:

    default_blueprints = {
        "aws/ecr-repository": {
            "image": "bedrock/aws-ecr-repository"
        },
        "aws/ecs-task-definition": {
            "image": "bedrock/aws-ecs-task-definition"
        }
    }

    @staticmethod
    def get_blueprint_home():
        return os.environ.get('BLUEPRINT_HOME') if os.environ.get('BLUEPRINT_HOME') is not None else '~/.bedrock'

    @staticmethod
    def get_blueprint_registry():
        return os.environ.get('BLUEPRINT_REGISTRY')

    @staticmethod
    def get_blueprint_tag():
        return os.environ.get('BLUEPRINT_TAG')

    def __init__(self, blueprint_id, blueprint_image, dry_run=False, verbose=False):

        # Enable dry run (skip backend configuration)
        self.dry_run = dry_run

        # Enable verbose logging
        self.verbose = verbose

        # Blueprint home directory
        self.blueprint_home = '~/.bedrock'

        self.blueprint_id = blueprint_id
        self.blueprint_image = blueprint_image

    def run(self):
        if self.dry_run:
            print("Dry run enabled. No changes will be made.")

        blueprints = read_blueprints(self.blueprint_home)

        if self.blueprint_id is not None:
            blueprints[self.blueprint_id] = {
                'image': self.blueprint_image
            }

            if not self.dry_run:
                save_blueprints(blueprints, self.blueprint_home)
        else:
            print(json.dumps(blueprints, indent=2))
