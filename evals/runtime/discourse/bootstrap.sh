#!/usr/bin/env bash
# Services are private to this container; no host ports or host data directories.
set -euo pipefail
if [[ $(id -u) != 0 ]]; then
  echo 'Bootstrap requires container root; run Actor afterward as discourse.' >&2
  exit 1
fi
install -d -o postgres -g postgres /var/run/postgresql /tmp/codekick-discourse-pg
if [[ ! -s /tmp/codekick-discourse-pg/PG_VERSION ]]; then
  sudo -u postgres /usr/lib/postgresql/15/bin/initdb -D /tmp/codekick-discourse-pg --auth=trust
  printf "\nlisten_addresses = ''\nshared_buffers = 128MB\nfsync = off\nsynchronous_commit = off\nfull_page_writes = off\n" >> /tmp/codekick-discourse-pg/postgresql.conf
fi
sudo -u postgres /usr/lib/postgresql/15/bin/pg_ctl -D /tmp/codekick-discourse-pg -l /tmp/codekick-discourse-pg/server.log -w start
if [[ $(sudo -u postgres psql -h /var/run/postgresql -tAc "SELECT 1 FROM pg_roles WHERE rolname = 'discourse'") != 1 ]]; then
  sudo -u postgres psql -h /var/run/postgresql -c "CREATE ROLE discourse LOGIN SUPERUSER;"
fi
redis-server --bind 127.0.0.1 --port 6379 --daemonize yes --save '' --appendonly no
redis-cli ping
exec "$@"
