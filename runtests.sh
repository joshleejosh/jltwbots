#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ${DIR}
source botenv/bin/activate
export PYTHONPATH=${PYTHONPATH}:${DIR}

python -m unittest discover bottest "$@"

