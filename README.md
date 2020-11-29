# Bedrock Command-line Interface (CLI)

A command line tool for managing Terraform blueprints.

## Introduction

The bedrock CLI is a simple tool to help manage the execution of Terraform blueprints.

You may manage a collection of blueprints that you use across multiple environments, which becomes difficult to 
manage as the collection grows larger.

Bedrock makes it easy to provision blueprints from anywhere so you can focus on building rather than configuring 
your environments.

For bedrock to manage your blueprints all you need is a Docker image (one for each blueprint), with the blueprint 
configuration in the `/blueprint` path. The image should also include a Terraform runtime as the default entry point
(see the official Terraform Docker image for example).

Bedrock will manage the backend configuration, inputs and provider configuration in a central location, such that 
your blueprint instances are accessible and easily managed from anywhere.


## Projects

As it is likely that you work with more than one Cloud environment, Bedrock supports multiple projects each with
different backend configurations. This allows you to isolate the state management for different environments as
required.


## Commands

Bedrock commands are grouped by three primary sub-commands: project, blueprint and instance. Project commands
relate to managing active project configurations; blueprint commands are for managing registered blueprints; and
instance commands are used to provision blueprint instances.

### Project

Manage project configurations.

Subcommands:

* list - show available project configurations
* switch <config> - switch to a named project
* new <config> - create a new project
* set-backend - update the project configuration backend

### Blueprint

Manage registered blueprints.

Subcommands:

* list - show available blueprints
* add - register a new blueprint

``` bash
$ bedrock blueprint list

ecs-task-definition - Template for ECS tasks
aws-launch-template - Template for EC2 instances
aws-spot-fleet - AWS Spot Fleet request
aws-ecs-cluster - AWS ECS cluster provisioning
...
```

### Instance

Provision blueprint instances.

Subcommands:

* new - create a new blueprint instance.
* list - list known instances
* refresh - update a named blueprint instance
* destroy - remove a named blueprint instance

``` bash
$ bedrock instance new ecs-task-definition

Name [default]:     apachesling
Backend type [S3]:  s3
Namespace:          staging
Volumes:            ...
Mounts:             ...

Initialising workspace..
```

### List

List existing blueprint instances.

``` bash
$ bedrock list

ecs-task-definition:
    - apachesling

aws-launch-template:
    - reverseproxy

aws-spot-fleet:
    - reverseproxy
...
```

### Refresh

Refresh a blueprint instance.

``` bash
$ bedrock refresh

Select workspace to refresh: reverseproxy (aws-spot-fleet)

Refreshing reverseproxy (aws-spot-fleet).. 
```

### Destroy

Destroy a blueprint instance.

``` bash
$ bedrock destroy

Select workspace to destroy: reverseproxy (aws-spot-fleet)

Are you sure you want to destroy reverseproxy (aws-spot-fleet) [N]? Y

Destroying reverseproxy (aws-spot-fleet).. 
```
 