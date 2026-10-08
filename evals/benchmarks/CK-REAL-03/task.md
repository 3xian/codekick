# GitLab repository migration fails on releases

Migrating a public GitLab repository into Gitea fails while importing releases. The reported repository is `https://gitlab.com/unboundsoftware/schemas`; its GoReleaser-generated releases contain four source archives and seven release links. GitLab's release API does not require these two lists to have matching lengths.

## Reproduction

Migrate the repository, including its releases, into Gitea. The reported deployment uses Gitea 1.25.3, a rootless Docker image in Kubernetes, PostgreSQL, and Git 2.49.1. The reporter also reproduced the problem on the Gitea demo site.

## Actual behavior

Migration fails with `panic: runtime error: index out of range [4] with length 4` and returns an internal server error.

## Expected behavior

Valid releases with more release links than source archives should migrate without a panic. Preserve the release links and the existing behavior of ordinary repository migrations.
