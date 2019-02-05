#!/bin/bash

set -e

ansible-playbook deploy.yml --extra-vars=@vars.yml --tags pull,touch
