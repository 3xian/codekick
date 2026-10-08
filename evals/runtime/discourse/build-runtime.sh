#!/usr/bin/env bash
# Build from a clean parent export. Only dependency manifests/vendor patches enter image.
# Usage: build-runtime.sh /path/to/clean-pre-export [codekick-discourse-runtime:ck-real-04]
set -euo pipefail
source_dir=$(realpath "${1:?clean parent export directory required}")
image=${2:-codekick-discourse-runtime:ck-real-04}
recipe_dir=$(cd -- "$(dirname -- "$0")" && pwd)
context=$(mktemp -d "${TMPDIR:-/tmp}/codekick-discourse-build.XXXXXX")
trap 'rm -rf -- "$context"' EXIT
cp "$recipe_dir/Dockerfile" "$recipe_dir/bootstrap.sh" "$context/"
for manifest in Gemfile Gemfile.lock package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc; do
  cp "$source_dir/$manifest" "$context/"
done
cp -R "$source_dir/patches" "$context/patches"
docker build --memory 3g --platform linux/arm64 -t "$image" "$context"
