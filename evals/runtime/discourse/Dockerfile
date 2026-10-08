# Historical .devcontainer/devcontainer.json image, native linux/arm64.
# Context: recipe/bootstrap, locked Gemfile/package manifests, and vendor patches only.
# Never include application sources, .git, oracle patches, or Controller metadata.
FROM discourse/discourse_dev@sha256:05a49b74da4d1252c6e571a2a3200ece5b8baa2757fe57626f712039ff4ea8e1
USER root
ENV BUNDLE_PATH=/opt/codekick/bundle \
    BUNDLE_FROZEN=true \
    BUNDLE_WITHOUT=development \
    RAILS_ENV=test \
    LOAD_PLUGINS=0 \
    PGUSER=discourse \
    PGHOST=/var/run/postgresql
WORKDIR /opt/codekick/dependencies
COPY Gemfile Gemfile.lock ./
RUN bundle _2.6.4_ install --jobs 2 --retry 3 && \
    chmod -R a+rX /opt/codekick/bundle
ENV PNPM_HOME=/opt/codekick/pnpm \
    npm_config_store_dir=/opt/codekick/pnpm-store
RUN npm install --global pnpm@9.15.5
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./
COPY patches/ ./patches/
RUN pnpm fetch --frozen-lockfile --store-dir /opt/codekick/pnpm-store && \
    chmod -R a+rX /opt/codekick/pnpm-store
COPY bootstrap.sh /usr/local/bin/codekick-discourse-bootstrap
RUN chmod 755 /usr/local/bin/codekick-discourse-bootstrap
WORKDIR /workspace
ENTRYPOINT ["/usr/local/bin/codekick-discourse-bootstrap"]
CMD ["sleep", "infinity"]
