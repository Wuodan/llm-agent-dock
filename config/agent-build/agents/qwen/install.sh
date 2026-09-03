#!/usr/bin/env bash
set -euo pipefail

npm install -g @qwen-code/qwen-code@latest

# Remove native-build cache left under root's home by npm.
rm -rf /root/.cache/node-gyp
