#!/usr/bin/env bash
# Controller-only provisioning. Input must be a clean verified-parent export,
# without hidden tests, reference source, historical Git objects or metadata.
# This script does not run benchmark tests or make acceptance claims.
set -euo pipefail
if [[ $# != 2 ]]; then
    printf 'Usage: %s <absolute-clean-parent-export> <unique-codekick-prefix>\n' "$0" >&2
    exit 2
fi
source_dir=$1
prefix=$2
case "$source_dir" in /*) ;; *) echo 'Source path must be absolute' >&2; exit 2 ;; esac
case "$prefix" in codekick-*) ;; *) echo 'Prefix must start with codekick-' >&2; exit 2 ;; esac
recipe_dir=$(cd -- "$(dirname -- "$0")" && pwd)
test -f "$source_dir/uv.lock"
test -f "$source_dir/tools/provision"
test ! -e "$source_dir/.git"
docker build --tag "$prefix-base" "$recipe_dir"
docker run -d --name "$prefix-provision" --memory 4g --cpus 2 \
    --mount "type=bind,source=$source_dir,target=/workspace" "$prefix-base"
docker exec "$prefix-provision" chown -R vagrant:vagrant /workspace
# Native provision requires a real Git repository. A new empty repository has
# no commit objects, branch refs, remotes, historical or future source.
docker exec -u vagrant -w /workspace "$prefix-provision" git init
docker exec -u vagrant -w /workspace -e GITHUB_ACTIONS=1 \
    -e PUPPETEER_SKIP_DOWNLOAD=1 "$prefix-provision" \
    tools/provision --skip-dev-db-build
docker exec "$prefix-provision" bash -c '
    set -e
    mkdir -p /opt/codekick-zulip-overlay
    cd /workspace
    cp -a --parents .venv node_modules static/generated web/generated \
        locale/language_name_map.json locale/language_options.json \
        zproject/dev-secrets.conf /opt/codekick-zulip-overlay/
    find locale -name "*.mo" -exec cp -a --parents {} /opt/codekick-zulip-overlay/ \;
'
docker cp "$recipe_dir/prepare-workspace.sh" \
    "$prefix-provision:/usr/local/bin/codekick-prepare-workspace"
docker stop "$prefix-provision"
# Docker commit explicitly excludes bind-mounted /workspace and its .git.
docker commit "$prefix-provision" "$prefix-runtime"
docker image inspect "$prefix-runtime" --format '{{.Id}}'
