#!/usr/bin/env python3
import os
import pathlib
import boto3
import json


def init_path(path):
    os.makedirs(os.path.expanduser(f'~/.bedrock/{path}'), exist_ok=True)
    pathlib.Path(os.path.expanduser(f'~/.bedrock/{path}/backend.tf')).touch()


def init_config(path, workspace='default'):
    init_path(path)
    config_path = f'{os.path.expanduser(f"~/.bedrock/{path}")}/{workspace}.tfvars.json'
    if not os.path.exists(config_path):
        with open(config_path, 'w') as config_file:
            config_file.write('{}\n')


def write_backend(path, backend):
    init_path(path)

    with open(f'{os.path.expanduser(f"~/.bedrock/{path}")}/backend.tf', 'w') as config_file:
        config_file.write(backend + '\n')


def write_config(path, id, config):
    init_path(path)

    with open(f'{os.path.expanduser(f"~/.bedrock/{path}")}/{id}.tfvars.json', 'w') as config_file:
        config_file.write(f'{json.dumps(config, indent=2)}\n')


def current_workspace(path):
    try:
        with open(f'{os.path.expanduser(f"~/.bedrock/{path}")}/.terraform/environment', 'r') as env_file:
            return env_file.readline()
    except IOError:
        return 'default'


def append_env(environment, env_var, warn_missing=False):
    if env_var in os.environ:
        environment.append(f'{env_var}={os.environ[env_var]}')
    elif warn_missing:
        print(f'** WARNING - Missing environment variable: {env_var}')


def assume_role(role_arn, role_session_name, role_duration):
    sts = boto3.client('sts')
    response = sts.assume_role(RoleArn=role_arn, RoleSessionName=role_session_name, DurationSeconds=role_duration)
    credentials = response['Credentials']

    os.putenv('AWS_ACCESS_KEY_ID', credentials['AccessKeyId'])
    os.putenv('AWS_SECRET_ACCESS_KEY', credentials['SecretAccessKey'])
    os.putenv('AWS_SESSION_TOKEN', credentials['SessionToken'])

