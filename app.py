#!/usr/bin/env python3

from aws_cdk import core

from synapse_docker_registry.synapse_docker_registry_stack import SynapseDockerRegistryStack


app = core.App()
SynapseDockerRegistryStack(app, "synapse-docker-registry")

app.synth()
