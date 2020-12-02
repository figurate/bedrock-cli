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

    def __init__(self, blueprint_id, blueprint_image, dry_run=False, verbose=False):

        # Enable dry run (skip backend configuration)
        self.dry_run = dry_run

        # Enable verbose logging
        self.verbose = verbose

        self.blueprint_id = blueprint_id
        self.blueprint_image = blueprint_image

    def run(self):
        if self.dry_run:
            print("Dry run enabled. No changes will be made.")

        blueprints = read_blueprints()
        blueprints[self.blueprint_id] = {
            'image': self.blueprint_image
        }

        if not self.dry_run:
            save_blueprints(blueprints)
