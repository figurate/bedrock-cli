#!/usr/bin/env python3
import argparse
import sys

from simple_term_menu import TerminalMenu

from .terraform import TerraformSpec
from .backend import BackendSpec
from .config import ConfigSpec


class BedrockCli(object):

    def __init__(self):
        parser = argparse.ArgumentParser(description='', usage='''bedrock <command> [<args>]
         Available commands:
            apply
            backend - configure the backend
            config - configure instance variable overrides
            destroy
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
        parser.add_argument('--dryrun', action='store_true', help='simulate execution without making any changes')
        parser.add_argument('-q', '--quiet', action='store_true', help='suppress execution output to stdout')
        parser.add_argument('command', help='Subcommand to run', choices=['apply', 'destroy', 'force-unlock', 'graph', 'import', 'init', 'output', 'plan', 'providers', 'refresh', 'show',
                                                                          'state', 'taint', 'untaint', 'version', 'workspace'] + ['backend', 'config'])
        parser.add_argument('cmd_args', metavar='<cmd_args>',
                            help='additional arguments for sub-commands', nargs='*')

        args = parser.parse_args(sys.argv[1:])

        self.blueprint = args.blueprint
        self.dryrun = args.dryrun

        if args.command in TerraformSpec.tf_commands:
            self.terraform(sys.argv[sys.argv.index(args.command):])
        elif args.command == 'backend':
            self.backend(sys.argv[sys.argv.index(args.command) + 1:])
        elif args.command == 'config':
            self.config(sys.argv[sys.argv.index(args.command) + 1:])

    def get_blueprint_id(self):
        blueprints = ["ecr-repository", "ecs-task-definition", "ecs-service"]

        if self.blueprint in blueprints:
            return self.blueprint
        else:
            blueprint_menu = TerminalMenu(blueprints, show_search_hint=True)
            blueprint_index = blueprint_menu.show()

            return blueprints[blueprint_index]

    def get_backend_type(self):
        backends = BackendSpec.tf_backends

        if self.backend in backends:
            return self.backend
        else:
            backend_menu = TerminalMenu(backends, show_search_hint=True)
            backend_index = backend_menu.show()

            return backends[backend_index]

    def terraform(self, args):
        spec = TerraformSpec(None, None, dry_run=self.dryrun)
        spec.blueprint_id = self.get_blueprint_id()
        spec.image = f"figurate/{spec.blueprint_id}"

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

        spec = BackendSpec(None, dry_run=self.dryrun)
        spec.blueprint_id = self.get_blueprint_id()
        spec.backend_type = self.get_backend_type()
        spec.aws_account_id = '976651329757'
        spec.organization = 'micronode'

        spec.run()

    def config(self, args):
        spec = ConfigSpec(None, None, dry_run=self.dryrun)
        spec.blueprint_id = self.get_blueprint_id()
        spec.cvars = {}
        for cnf in args:
            cvar = cnf.split('=')
            spec.cvars[cvar[0]] = cvar[1]

        spec.run()


if __name__ == "__main__":
    BedrockCli()
