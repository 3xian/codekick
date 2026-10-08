# Controller builds this neutral image; no benchmark source or Judge inputs enter it.
FROM discourse/discourse_dev@sha256:05a49b74da4d1252c6e571a2a3200ece5b8baa2757fe57626f712039ff4ea8e1
RUN npm install --global @openai/codex@0.161.0 && codex --version
RUN mkdir -p /workspace /run/codekick-auth /run/codekick-controller \
    && chown discourse:discourse /workspace /run/codekick-auth
USER discourse
WORKDIR /workspace
CMD ["sleep", "infinity"]
