#!/usr/bin/env bash
set -euo pipefail

npm install -g @google/gemini-cli

# Remove native-build cache left under root's home by npm.
rm -rf /root/.cache/node-gyp
