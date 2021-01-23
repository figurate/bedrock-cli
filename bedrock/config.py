from .utils import *


class ConfigSpec:

    def __init__(self, blueprint_id, dry_run=False, verbose=False):

        # Enable dry run (skip backend configuration)
        self.dry_run = dry_run

        # Enable verbose logging
        self.verbose = verbose

        # Blueprint home directory
        self.blueprint_home = '.'

        # Blueprint identifier
        self.blueprint_id = blueprint_id

        # Command-line variables
        self.cvars = {}

    def run(self):
        if self.dry_run:
            print("Dry run enabled. No changes will be made.")

        if not self.dry_run:
            workspace = current_workspace(self.blueprint_id, self.blueprint_home)

            if self.verbose:
                print(f"Writing config changes to: {self.blueprint_home}/{self.blueprint_id}/{workspace}.tfvars.json\n")

            write_config(self.blueprint_id, self.blueprint_home, workspace, self.cvars)
