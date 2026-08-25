#!/usr/bin/env bash
# GIT_ASKPASS helper: answer git's HTTPS credential prompts from $GITHUB_TOKEN (feature 130).
#
# The container has no SSH key and no ssh-agent, so GitHub is reached over HTTPS with the
# fine-grained PAT from development-secrets.ini. The token is handed to git through this helper and
# an environment variable - never on the command line (visible in /proc) and never written into
# .git/config. Username is the fixed `x-access-token` GitHub expects for a token.
case "$1" in
  *sername*) echo "x-access-token" ;;
  *) echo "${GITHUB_TOKEN:?GITHUB_TOKEN is not set}" ;;
esac
