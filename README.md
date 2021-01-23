# Bedrock Command-line Interface (CLI)

A command line tool for managing Terraform blueprints.

## Overiew

The Bedrock command line tool builds on the excellent features of Terraform to provide a "no-code" approach to
provisioning infrastructure.


## Introduction

Bedrock can be used as a drop-in replacement for Terraform, in that all the commands are the same except for two key
differences:

First, all commands are executed in the context of a `blueprint`, which is a predefined Terraform
configuration. Each command will prompt for selection from a list of registered blueprints before executing
the command.

The other key difference is that all local state, modules, plugins, etc. are stored under a single directory, which
by default is the current user directory but can be defined as any local directory. This means that you don't need to 
change directories in order to run commands on different Terraform configurations.


## Bedrock Commands

To support these key differences Bedrock introduces three additional commands that are not available with Terraform:

### Backend

The backend command supports configuration of Terraform state management, which may be either a `local`, `s3`, or
`remote` configuration.

A local configuration is the default for all blueprints, and just means that state is stored locally under the 
`~/.bedrock` directory. Whilst no configuration is required for local state, it can be a poor choice if you don't 
create regular backups or use ephemeral execution environments.

An AWS S3 bucket may be used to store Terraform state securely, which requires the appropriate credentials to be
configured to read and write to the bucket.

Finally a remote configuration using Terraform Cloud may be configured for which a configuration file should be
provided in the user home directory (i.e. `.terraformrc`).

_NOTE:_ Terraform doesn't support different backend configurations for workspaces in a single configuration. This
means that you must use the same state management configuration for all instances of a blueprint. If you need to
manage multiple independent configuration sets you can create and run in different blueprint directories. 


### Config

If a blueprint doesn't provide default values for all variables, or if you would like to override some defaults, you
may use the Bedrock config command. This is a simple way to specify variables values using a `key=value` format. For
more complex variable configurations you may specify a var-file location for some commands using the `-var-file` option.

### Blueprint

Finally, the blueprint command allows you to configure and manage registered blueprints. Whilst the default blueprints
may support general purpose use-cases, sometimes you may want to provide your own more specialised blueprints for use
with the Bedrock command line tool.

To create a Bedrock-compatible blueprint you just need to create a Docker image that includes a version of Terraform,
and the blueprint configuration under the `/blueprint` directory.

    
## Workspaces

To support creating multiple instances of a blueprint you may use Terraform workspaces in the same way as you would
with the Terraform command line tool. For each blueprint workspace, Bedrock will provide separate state management and
variable overrides.

As workspaces may be used to create blueprint instances across multiple environments and accounts, some care should
be taken to define a workspace naming convention. For example, you may wish to prefix workspace names with the
account number, followed by application name, environment, etc.

As an example, to configure an ECS cluster I might create a workspace such as: `987654321-myapp-staging`


## Blueprint Home Directory

As mentioned earlier all local state and configuration is maintained in a single default directory. Sometimes you
may require isolation of state files, such as when managing different tenancies or separation of production and
non-production environments.

Bedrock supports an environment variable to override the default blueprint home directory, which you can specify
either on the command line or export to your environment:

    $ BLUEPRINT_HOME=/tmp/bedrock bedrock workspace list

Used in conjunction with target environment overrides (such as `AWS_PROFILE` for AWS tenancy management) you can
switch between different tenancies very easily:

    $ AWS_PROFILE=staging BLUEPRINT_HOME=/opt/bedrock/staging bedrock apply # make changes in staging environment



--------------

## Introduction

The bedrock CLI is a simple tool to help manage the execution of Terraform blueprints.

You typically may have a number of Terraform configurations that you use across multiple environments (e.g. dev, test prod, etc.).
As these configurations grow that can become difficult to manage.

Bedrock makes it easy to provision configuration _blueprints_ from anywhere so you can focus on building rather than configuring 
your environments.

### What is a Blueprint?

We all know the benefits of Terraform Modules, and the many ways that they can be published and consumed. Bedrock extends on this concept
of portable configurations to include things that you wouldn't usually package with a module (e.g. provider configuration, etc.)

Essentially a Blueprint is a complete Terraform configuration packaged as a Docker image that can be executed anywhere Docker is supported.

For Bedrock to manage your blueprints all you need is a Docker image (one for each blueprint), with the Terraform 
configuration in the `/blueprint` path. The image should also include a Terraform runtime as the default entry point
(see the official Terraform Docker image for example).

Bedrock will manage the backend configuration, inputs and provider configuration in a configurable location, such that 
your blueprint instances are accessible and easily managed from anywhere.


## Getting Started

You can install bedrock CLI via pip as follows:

    $ pip install bedrockcli



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
 
