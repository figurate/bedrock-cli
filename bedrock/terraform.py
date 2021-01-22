#!/usr/bin/env python3

"""
Execute Terraform blueprints as Docker containers.
"""
import docker
import docker.errors
import dockerpty
from .utils import *


class TerraformSpec:

    tf_commands = ['apply', 'destroy', 'force-unlock', 'graph', 'import', 'init', 'output', 'plan', 'providers', 'refresh', 'show',
                   'state', 'taint', 'untaint', 'version', 'workspace']

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

        # Type of backend (e.g. s3, remote, etc.)
        self.backend_type = 's3'

        # Environment variables to import to container
        self.evars = ['AWS_DEFAULT_REGION']

        # Override default var file location..
        self.var_file = None

        # Command-line variables
        self.cvars = []

        # Command string passed to the container
        self.args = ['workspace', 'new']

    def run(self):

        if self.dry_run:
            print("Dry run enabled. No changes will be made.")

        # Configure container environment..
        if self.verbose:
            print(f"Importing environment variables: {self.evars}\n")

        imported_vars = []
        environment = []
        for env_var in self.evars:
            if append_env(environment, env_var, True):
                imported_vars.append(env_var)

        # Append optional environment variables..
        for env_var in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN', 'AWS_PROFILE', 'TF_ARGS',
                        'http_proxy', 'https_proxy', 'no_proxy']:
            if append_env(environment, env_var):
                imported_vars.append(env_var)

        if self.verbose:
            print(f"Imported environment variables: {imported_vars}\n")

        # Configure command line config
        if self.verbose:
            print(f"Configuring variable overrides: {self.cvars}\n")

        for cnf in self.cvars:
            cvar = cnf.split('=')
            environment.append(f'TF_VAR_{cvar[0]}={cvar[1]}')

        # Configure variables..
        workspace = current_workspace(self.blueprint_id, self.blueprint_home)

        if self.args[0] in ['plan', 'apply', 'refresh', 'destroy']:
            if self.var_file is not None:
                run_command = ' '.join(self.args) + f' -var-file="{os.path.basename(self.var_file)}" /blueprint'
            else:
                run_command = ' '.join(self.args) + f' -var-file="{workspace}.tfvars.json" /blueprint'

        elif self.args[0] in ['import']:
            if self.var_file is not None:
                run_command = self.args[0] + f' -config=/blueprint -var-file="{os.path.basename(self.var_file)}" ' + ' '.join(self.args[1:])
            else:
                run_command = self.args[0] + f' -config=/blueprint -var-file="{workspace}.tfvars.json" ' + ' '.join(self.args[1:])
        elif self.args[0] not in ['output', 'show', 'state', 'taint', 'untaint', 'version', 'workspace']:
            run_command = ' '.join(self.args) + ' /blueprint'
        else:
            run_command = ' '.join(self.args)

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
            os.path.expanduser(f'~/'): {
                'bind': '/root',
                'mode': 'ro'
            },
            # backend config must be in same directory as rest of configuration..
            os.path.expanduser(f'{self.blueprint_home}/{self.blueprint_id}/backend.tf'): {
                'bind': '/blueprint/backend.tf',
                'mode': 'ro'
            },
            # bind-mount docker socket to support blueprints that use docker..
            '/var/run/docker.sock': {
                'bind': '/var/run/docker.sock',
                'mode': 'ro'
            }
        }
        if self.var_file is not None:
            # var file override also needs to be mounted..
            volumes[os.path.abspath(self.var_file)] = {
                'bind': f'/work/{os.path.basename(self.var_file)}',
                'mode': 'ro'
            }

        # Run container..
        if not self.dry_run:
            container = None
            try:
                print("Initialising Docker..")

                client = docker.from_env()

                # container = client.containers.run(spec.image, spec.command, privileged=True, network_mode='host',
                #                   remove=True, environment=environment, volumes=volumes, stdin_open=True, tty=True, detach=True)

                if self.image_registry is not None:
                    image_ref = self.image_registry + "/" + self.image
                else:
                    image_ref = self.image

                if self.pull_image:
                    client.api.pull(image_ref, self.image_tag)

                if self.image_tag is not None:
                    image_ref += ":" + self.image_tag

                print(f"Running Terraform command: {run_command}")

                if self.verbose:
                    print(f"Creating container from image: {image_ref}\n")

                container = client.api.create_container(image_ref, run_command, self.instance_name,
                                                        working_dir='/work',
                                                        host_config=client.api.create_host_config(binds=volumes,
                                                                                                  network_mode='host'),
                                                        stdin_open=True, tty=True, environment=environment)

                dockerpty.start(client.api, container)

                # logs = container.logs(stream=True)
                # for log in logs:
                #     try:
                #         print(log.decode('utf-8'), end='')
                #     except UnicodeDecodeError:
                #         print(log)

            except KeyboardInterrupt:
                print(f"Aborting {self.blueprint_id}..")
                if container is not None:
                    container.stop()
            except docker.errors.ImageNotFound:
                print(f"Blueprint image not found {image_ref}.. did you run with --pull option?")
