#!/usr/bin/env python3

"""
Export Terraform blueprints to the local filesystem.
"""
import docker
import docker.errors
import dockerpty
from .utils import *


class ExportSpec:

    def __init__(self, blueprint_id, instance_name, pull_image=False, dry_run=False, verbose=False):
        # Docker image
        self.image = 'hashicorp/terraform'
        self.image_tag = None
        self.image_registry = None

        # Pull image prior to run
        self.pull_image = pull_image

        # Enable dry run (skip container creation)
        self.dry_run = dry_run

        # Enable verbose logging
        self.verbose = verbose

        # Blueprint home directory
        self.blueprint_home = '.'

        # Blueprint identifier
        self.blueprint_id = blueprint_id

        # Name of blueprint instance
        self.instance_name = instance_name

    def run(self):

        if self.dry_run:
            print("Dry run enabled. No changes will be made.")

        # Configure variables..
        workspace = current_workspace(self.blueprint_id, self.blueprint_home)

        run_command = ["cp","-R","/blueprint/.","/work"]

        # Initialise working directory
        if self.verbose:
            print(f"Initialising current workspace: {workspace}\n")

        init_config(self.blueprint_id, self.blueprint_home, workspace)

        # Configure container volumes..
        volumes = {
            os.path.expanduser(f'{self.blueprint_home}/{self.blueprint_id}'): {
                'bind': '/work',
                'mode': 'rw'
            },
        }

        # Run container..
        if not self.dry_run:
            container = None
            try:
                print("Initialising Docker..")

                client = docker.from_env()

                if self.image_registry is not None:
                    image_ref = self.image_registry + "/" + self.image
                else:
                    image_ref = self.image

                if self.pull_image:
                    client.api.pull(image_ref, self.image_tag)

                if self.image_tag is not None:
                    image_ref += ":" + self.image_tag

                print(f"Running export command: {run_command}")

                if self.verbose:
                    print(f"Creating container from image: {image_ref}\n")

                container = client.api.create_container(image_ref, run_command, self.instance_name,
                                                        entrypoint=[],
                                                        working_dir='/work',
                                                        host_config=client.api.create_host_config(binds=volumes,
                                                                                                  network_mode='host'),
                                                        stdin_open=True, tty=True)

                dockerpty.start(client.api, container)

            except KeyboardInterrupt:
                print(f"Aborting {self.blueprint_id}..")
                if container is not None:
                    container.stop()
            except docker.errors.ImageNotFound:
                print(f"Blueprint image not found {image_ref}.. did you run with --pull option?")
