# Extensions

Extensions allow installing additional tools into an existing final image. Extensions are defined locally under
`~/.aicage-custom/extensions/` and are applied in the order selected by the user.
Extensions are base-image agnostic; scripts should handle distribution differences if needed.

## Directory layout

Each extension lives in its own directory:

```text
~/.aicage-custom/extensions/<EXTENSION>/
├─ extension.yml (or extension.yaml)
├─ Dockerfile        # optional
└─ scripts/          # optional
   ├─ 01-setup.sh
   └─ 02-install.sh
```

Only scripts in the `scripts/` directory are executed. Scripts run in alphabetical order.
The extension id is the directory name and is used when selecting extensions.
Define at least one of `scripts/` or `shares`.

## extension.yml

`extension.yml` (or `extension.yaml`) must contain the following keys:

```yaml
name: "Display name"
description: "Short description of what the extension adds."
shares: # optional
  - ~/.config/my-tool
  - ~/.cache/my-tool:ro
```

`shares` can be used to define host mounts. Each entry uses the same syntax as `--share`: `HOST`
or `HOST:ro`. The host path must already exist.

No additional keys are supported.

## Scripts

Scripts are executed inside the image build. Use shell scripts (`*.sh`) and avoid interactive prompts.
Scripts run with `bash` and `set -e` enabled by the built-in Dockerfile. Non-executable scripts are made
executable before running.

## Dockerfile (optional)

If `Dockerfile` is present, it is used instead of the built-in Dockerfile. The build context is the extension
directory. The following build args are provided:

- `BASE_IMAGE`: the image to extend (the current image in the extension chain)
- `EXTENSION`: the extension id (directory name)

Custom Dockerfiles are responsible for running any scripts if needed.
The built-in Dockerfile is at `config/extension-build/Dockerfile`.

Example:

```Dockerfile
ARG BASE_IMAGE=base
FROM ${BASE_IMAGE} AS runtime

RUN --mount=type=bind,source=scripts,target=/tmp/aicage/scripts,readonly \
    /tmp/aicage/scripts/01-install.sh
```

## Extended images

When extensions are selected, the default local image tag is:

```text
aicage-extended:<agent>-<base>-<ext1>-<ext2>
```

The project config stores the selected base, extensions, and image ref for reuse on subsequent runs.

## Example

`extension.yml`:

```yaml
name: "Marker extension"
description: "Creates a marker file in the image."
```

`scripts/01-marker.sh`:

```bash
#!/usr/bin/env bash
set -e

mkdir -p /usr/local/share/aicage-extensions
echo "marker" > /usr/local/share/aicage-extensions/marker.txt
```
