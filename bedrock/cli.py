#!/usr/bin/env python3
import argparse
import sys
import os

from simple_term_menu import TerminalMenu

from .terraform import TerraformSpec
from .backend import BackendSpec
from .config import ConfigSpec
from .blueprint import BlueprintSpec
from .export import ExportSpec
from .utils import read_blueprints, ANSIColors


class BedrockCli(object):

    def __init__(self):
        parser = argparse.ArgumentParser(description='', usage=f'''bedrock <command> [<args>]
         Available commands:
            apply
            {ANSIColors.BOLD}backend{ANSIColors.ENDC} - configure the backend
            {ANSIColors.BOLD}blueprint{ANSIColors.ENDC} - configure available blueprints
            {ANSIColors.BOLD}config{ANSIColors.ENDC} - configure instance variable overrides
            destroy
            {ANSIColors.BOLD}export{ANSIColors.ENDC} - export blueprint configuration
            graph
            import
            init
            output
            plan
            providers
            refresh
            show
            state
            taint
            untaint
            version
            workspace
        ''')

        parser.add_argument('-t', '--blueprint', metavar='<blueprint_id>',
                            help='optional blueprint identifier (bypass selection mode)')
        parser.add_argument('--pull', action='store_true', help='pull blueprint image prior to command execution')
        parser.add_argument('--dryrun', action='store_true', help='simulate execution without making any changes')
        parser.add_argument('-v', '--verbose', action='store_true', help='output additional logs to stdout')
        parser.add_argument('-q', '--quiet', action='store_true', help='suppress execution output to stdout')
        parser.add_argument('-var-file', metavar='<var_file>', help='override default config')
        parser.add_argument('command', help='Subcommand to run', choices=['apply', 'destroy', 'force-unlock', 'graph', 'import', 'init', 'output', 'plan', 'providers', 'refresh', 'show',
                                                                          'state', 'taint', 'untaint', 'version', 'workspace'] + ['blueprint', 'backend', 'config', 'export'])
        parser.add_argument('cmd_args', metavar='<cmd_args>',
                            help='additional arguments for sub-commands', nargs='*')

        args, unknown = parser.parse_known_args(sys.argv[1:])

        for arg in unknown:
            if arg.startswith(("-", "--")):
                # store true for args without assignment
                if "=" not in arg:
                    parser.add_argument(arg, action='store_true')
                else:
                    parser.add_argument(arg)

        args = parser.parse_args()
        self.blueprint_id = args.blueprint
        self.pull_image = args.pull
        self.dryrun = args.dryrun
        self.verbose = args.verbose

        if args.command in TerraformSpec.tf_commands:
            self.terraform(sys.argv[sys.argv.index(args.command):], var_file=args.var_file)
        elif args.command == 'backend':
            self.backend(sys.argv[sys.argv.index(args.command) + 1:])
        elif args.command == 'config':
            self.config(sys.argv[sys.argv.index(args.command) + 1:])
        elif args.command == 'blueprint':
            self.blueprint(sys.argv[sys.argv.index(args.command) + 1:])
        elif args.command == 'export':
            self.export(sys.argv[sys.argv.index(args.command) + 1:])

        sys.exit()

    def get_blueprint(self):
        blueprints = {**BlueprintSpec.default_blueprints, **read_blueprints()}

        if self.blueprint_id in blueprints.keys():
            return [self.blueprint_id, blueprints[self.blueprint_id]]
        else:
            blueprint_ids = list(blueprints.keys())
            blueprint_menu = TerminalMenu(blueprint_ids, title="Select blueprint:", show_search_hint=True)
            blueprint_index = blueprint_menu.show()
            blueprint_id = blueprint_ids[blueprint_index]
            return [blueprint_id, blueprints[blueprint_id]]

    def get_backend_type(self):
        backends = BackendSpec.tf_backends

        if self.backend in backends:
            return self.backend
        else:
            backend_menu = TerminalMenu(backends, show_search_hint=True)
            backend_index = backend_menu.show()

            return backends[backend_index]

    def terraform(self, args, var_file=None):
        spec = TerraformSpec(None, None, pull_image=self.pull_image, dry_run=self.dryrun, verbose=self.verbose)
        blueprint_home = BlueprintSpec.get_blueprint_home()
        blueprint = self.get_blueprint()
        spec.blueprint_home = blueprint_home
        spec.blueprint_id = blueprint[0]
        spec.image = blueprint[1]['image']
        spec.image_registry = BlueprintSpec.get_blueprint_registry()
        spec.image_tag = BlueprintSpec.get_blueprint_tag()
        spec.var_file = var_file

        # instance_name = input("Instance name: ")
        spec.instance_name = 'tf_run'

        # spec.command = f"workspace new {spec.instance_name}"
        spec.args = args
        # if args[0] not in ['import', 'output', 'state', 'taint', 'untaint', 'version', 'workspace']:
        #     spec.command = ' '.join(args) + ' /blueprint'
        # else:
        #     spec.command = ' '.join(args)

        spec.run()

    def backend(self, args):
        parser = argparse.ArgumentParser(description='', usage='backend [<args>]')
        parser.add_argument('--aws-account', metavar='<aws_account_id>',
                            help='optional account identifier (for S3 backend storage)')
        parser.add_argument('--organization', metavar='organization>',
                            help='optional organization identifier (for remote storage via Terraform Cloud)')

        spec = BackendSpec(None, dry_run=self.dryrun, verbose=self.verbose)
        blueprint_home = BlueprintSpec.get_blueprint_home()
        spec.blueprint_home = blueprint_home
        spec.blueprint_id = self.get_blueprint()[0]
        spec.backend_type = self.get_backend_type()

        if spec.backend_type == 's3':
            spec.s3_bucket = input("S3 Bucket Name: ")
        elif spec.backend_type == 'remote':
            spec.organization = input("Organization ID: ")

        spec.run()

    def config(self, args):
        spec = ConfigSpec(None, dry_run=self.dryrun, verbose=self.verbose)
        blueprint_home = BlueprintSpec.get_blueprint_home()
        spec.blueprint_home = blueprint_home
        spec.blueprint_id = self.get_blueprint()[0]
        spec.cvars = {}
        for cnf in args:
            cvar = cnf.split('=')
            spec.cvars[cvar[0]] = cvar[1]

        spec.run()

    def blueprint(self, args):
        spec = BlueprintSpec(None, None, dry_run=self.dryrun, verbose=self.verbose)
        if len(args) > 0 and args[0] == 'add':
            spec.blueprint_id = input("Blueprint ID: ")
            spec.blueprint_image = input("Blueprint Image: ")

        spec.run()

    def export(self, args):
        spec = ExportSpec(None, None, pull_image=self.pull_image, dry_run=self.dryrun, verbose=self.verbose)
        blueprint_home = BlueprintSpec.get_blueprint_home()
        blueprint = self.get_blueprint()
        spec.blueprint_home = blueprint_home
        spec.blueprint_id = blueprint[0]
        spec.image = blueprint[1]['image']
        spec.image_registry = BlueprintSpec.get_blueprint_registry()
        spec.image_tag = BlueprintSpec.get_blueprint_tag()

        spec.instance_name = 'tf_export'

        spec.run()


if __name__ == "__main__":
    BedrockCli()
