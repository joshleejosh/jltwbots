#!/bin/bash

# USAGE: runbot.sh python_module args...

# Make sure we're in the correct directory in case there are any relative paths involved.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ${DIR}
source botenv/bin/activate
export PYTHONPATH=${PYTHONPATH}:${DIR}
python "$@"

