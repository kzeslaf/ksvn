#!/bin/bash

set -e

DIR="$( cd "$( dirname "$( readlink -f "${BASH_SOURCE[0]}" )" )" && pwd -P )"

(
    source "$DIR/../.env/bin/activate"
    "$DIR/ksvn.py" "$@"
)
