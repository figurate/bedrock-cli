from .utils import *


class BackendSpec:

    tf_backends = ['local', 's3', 'remote']

    def __init__(self, blueprint_id, s3_bucket=None, organization=None, dry_run=False, verbose=False):
        self.backend_type = 's3'

        # Enable dry run (skip backend configuration)
        self.dry_run = dry_run

        # Enable verbose logging
        self.verbose = verbose

        # Blueprint home directory
        self.blueprint_home = '.'

        # Blueprint identifier
        self.blueprint_id = blueprint_id

        self.s3_bucket = s3_bucket
        self.organization = organization

    def run(self):
        if self.dry_run:
            print("Dry run enabled. No changes will be made.")

        if self.backend_type == 's3':
            backend = """terraform {
  backend "s3" {
    bucket = "%s"
    dynamodb_table = "terraform-lock"
    key = "blueprint/%s/terraform.tfstate"
  }
}
            """ % (self.s3_bucket, self.blueprint_id)
        elif self.backend_type == 'remote':
            backend = """terraform {
  backend "remote" {
    organization="%s"
    workspaces {
      prefix = "%s-"
    }
  }
}
            """ % (self.organization, self.blueprint_id)
        else:
            backend = """terraform {
  backend "local" {
    #path = "relative/path/to/terraform.tfstate"
  }
}
"""

        if not self.dry_run:
            write_backend(self.blueprint_id, self.blueprint_home, backend)
