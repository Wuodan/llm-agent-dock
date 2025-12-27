# Subtask 4: Use static `images-metadata.yaml` packaged with `aicage`

Read doc/ai/task/09/09-TASK.md and doc/ai/task/09/*.

I changed my mind about the live download of `~/.aicage/images-metadata.yaml`.
The file shall now no longer be downloaded live, but rather baked into the package which users install with:
`pipx install aicage`
similar to `src/aicage/config/config.yaml`

For this the following has to change ...


## Release pipeline: Add `aicage` version

During build pipeline `.github/workflows/publish.yml` I want the `aicage` version added to both `config.yaml` and `images-metadata.yaml` in the same stype as `aicage-image` and `aicage-image-base` versions are already in `images-metadata.yaml`.

Similar to the pipelines in submodule `aicage-image` I want to verify those 2 files against a schmema. Add such schmemas and use them to validate the config files in this projects build pipeline.


## Overwrite local config files from old version

When `aicage` runs, it shall check if the files:
- ~/.aicage/config.yaml
- ~/.aicage/images-metadata.yaml
contain older versions and if so overwrite them right at start before they are being loaded.


## Remove the download of `images-metadata.yaml`

From then on only use the file which is packaged.


## Sub-Task Workflow

Don't forget to read AGENTS.md and always use the existing venv.

You shall follow this order:
1. Read documentation and code to understand the task. 
2. Aks me questions if something is not clear to you
3. Present me with an implementation solution - this needs my approval
4. Implement the change autonomously including a loop of running-tests, fixing bugs, running tests
5. Run linters as in the pipeline `.github/workflows/publish.yml`
6. Present me the change for review
7. Interactively react to my review feedback

Visibility note: apply the "defining scope" rule from AGENTS.md (tests are exempt when deciding "outside").
