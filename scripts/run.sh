#!/bin/sh
set -eu
project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
. "$project_dir/scripts/java-env.sh"
cd "$project_dir"
if [ "$#" -eq 0 ]; then
    set -- --demo
fi
exec java -jar "$project_dir/target/campus-equipment-loan.jar" "$@"
