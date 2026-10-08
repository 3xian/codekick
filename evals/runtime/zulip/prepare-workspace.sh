#!/usr/bin/env bash
# Run as root in the isolated runtime container after mounting a clean export
# at /workspace. /opt/codekick-zulip-overlay contains dependencies and generated
# assets produced by the historical provisioning tools, never source or tests.
set -euo pipefail
test -f /.dockerenv
cd /workspace
test -f tools/test-backend
cp -a /opt/codekick-zulip-overlay/. /workspace/
mkdir -p var/{coverage,log,node-coverage,test_uploads,uploads,xunit-test-results}
chown -R vagrant:vagrant /workspace
# Initialize a fresh isolated cluster rather than reuse an image-baked database.
# This also prevents provisioning snapshot state from leaking between runs.
pg_dropcluster --stop 14 main
pg_createcluster 14 main
service postgresql start
service redis-server start
service memcached start
env PATH="/workspace/.venv/bin:$PATH" scripts/setup/generate-rabbitmq-cookie
service rabbitmq-server start
env PATH="/workspace/.venv/bin:$PATH" scripts/setup/configure-rabbitmq
sudo -H -u vagrant env PATH="/workspace/.venv/bin:$PATH" tools/setup/postgresql-init-dev-db
sudo -H -u vagrant env PATH="/workspace/.venv/bin:$PATH" tools/setup/postgresql-init-test-db
# Native environment checks remain enabled. The native launcher regenerates
# test fixtures when source/migrations differ from the provisioned parent.
