#!/usr/bin/env python3
import os
import pathlib
import json


def init_path(path, root):
    os.makedirs(os.path.expanduser(f'{root}/{path}'), exist_ok=True)
    pathlib.Path(os.path.expanduser(f'{root}/{path}/backend.tf')).touch()


def init_config(path, root, workspace='default'):
    init_path(path, root)
    config_path = f'{os.path.expanduser(f"{root}/{path}")}/{workspace}.tfvars.json'
    if not os.path.exists(config_path):
        with open(config_path, 'w') as config_file:
            config_file.write('{}\n')


def write_backend(path, root, backend):
    init_path(path, root)

    with open(f'{os.path.expanduser(f"{root}/{path}")}/backend.tf', 'w') as config_file:
        config_file.write(backend + '\n')


def write_config(path, root, id, config):
    init_path(path, root)

    with open(f'{os.path.expanduser(f"{root}/{path}")}/{id}.tfvars.json', 'w') as config_file:
        config_file.write(f'{json.dumps(config, indent=2)}\n')


def read_blueprints(root='~/.bedrock'):
    try:
        with open(f'{os.path.expanduser(f"{root}")}/blueprints.json', 'r') as blueprint_file:
            return json.load(blueprint_file)
    except IOError:
        return {}


def save_blueprints(blueprints, root='~/.bedrock'):
    with open(f'{os.path.expanduser(f"{root}")}/blueprints.json', 'w') as blueprint_file:
        blueprint_file.write(f'{json.dumps(blueprints, indent=2)}\n')


def current_workspace(path, root):
    try:
        with open(f'{os.path.expanduser(f"{root}/{path}")}/.terraform/environment', 'r') as env_file:
            return env_file.readline()
    except IOError:
        return 'default'


def append_env(environment, env_var, warn_missing=False):
    if env_var in os.environ:
        environment.append(f'{env_var}={os.environ[env_var]}')
        return True
    elif warn_missing:
        print(f'** WARNING - Missing environment variable: {env_var}')

    return False


# def assume_role(role_arn, role_session_name, role_duration):
#     sts = boto3.client('sts')
#     response = sts.assume_role(RoleArn=role_arn, RoleSessionName=role_session_name, DurationSeconds=role_duration)
#     credentials = response['Credentials']
#
#     os.putenv('AWS_ACCESS_KEY_ID', credentials['AccessKeyId'])
#     os.putenv('AWS_SECRET_ACCESS_KEY', credentials['SecretAccessKey'])
#     os.putenv('AWS_SESSION_TOKEN', credentials['SessionToken'])
#

class ANSIColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
