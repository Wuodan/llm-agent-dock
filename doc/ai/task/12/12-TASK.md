# Task 12: Build images on user's PC

I've been pondering this extension for a while now, it's like the last missing piece before go-live of `aicage`.

## Current situation

`aicage` is a python program to run CLI coding-agents in docker containers.

Key parts of `aicage` are:

### Image tooling

- Submodule `aicage-image-util` builds utility images for `aicage` runtime tasks.

### Base-images

- Submodule `aicage-image-base` builds the base-images.
- Those base images take a root-image (debian, ubuntu, fedora, etc.) and install a stack of tools for programming.
- Additionally, an `entrypoint.sh` is added which reacts to env-variables and mounts passed from `aicage` when running
the final-images.
- Base configuration:
  - Folder per base: `bases/<BASE>/`
  - `bases/<BASE>/base.yml` holds the relevant configuration of a base.
- Release-artifacts:
  - `bases.tar.gz`: An archive of the `bases` folder with the relevant configuration of a base-image.
- When are base-images updated:
  - Periodically, currently once per week.

### Final-images

- Submodule `aicage-image` builds the final-images. Each is an `agent` to `base-image` combination.
- `aicage-image` defines several coding-agents and builds final-images for the matrix "coding-agents to base-images".
- It installs one coding-agent on top of a base-image to build a final-image.
- Agent configuration:
  - Folder per agent: `agents/<AGENT>/`
  - `agents/<AGENT>/agent.yml` holds the relevant configuration of an agent.
    - Schema validation with `doc/validation/agent.schema.json`.
  - `agents/<AGENT>/install.sh` is the installation script for the agent used during image building.
  - `agents/<AGENT>/version.sh` prints the current version of the agent to trigger image building in CI pipelines.
- Release-artifact:
  - `images-metadata.yaml`:
    - Contains the configuration of base-images and agents.
    - Documented in `doc/images-metadata.md` in `aicage-image`.
    - Is packaged into releases of `aicage` and used at runtime to determine available agents and base-images.
  - `agents.tar.gz` (unused): An archive of the `agents` folder with the relevant configuration of an agent.
- When are final-images updated:
  - A CI-pipeline runs every 10 minutes and checks:
    - Agent version: Runs `agents/<AGENT>/version.sh` for every agent, if a final-image with that version exists and if
      not affected final-images are rebuilt.
    - Base-image updates: If the last layer of a base-image is in final-images to it, if not affected final-images are
      rebuilt.

### Aicage program

- Project `aicage` is the Python program used by users.
- `images-metadata.yaml` from `aicage-image` is packaged with it and used for agent and base-image configuration.
- Simple usage:
  - User starts it with `aicage <agent>`.
  - On first start it reads available agent-base combinations (aka final-images) and lets user choose a base to
    determine which final-image to run. This choice is persisted for future runs.
  - Image updates: Before running a final-image, `aicage` looks online for newer versions of it and pulls updates of it.
  - `aicage` then constructs env-vars and mounts for `docker run` and starts the container from the final-image.
  - The `entrypoint.sh` in the image uses the env-vars and mounts to properly set everything up.
  - Then the `agent` coding-agent program is started in the container.

## Desired extensions

I want to solve several problems nicely, all require building and maintaining images on user's PC.  
It also seems tricky to align the configuration and processes for the following changes so they
 don't interfere with each other and can be nicely combined.

### Non-redistributable agents

Some coding-agents cannot be legally redistributed as binaries. Their license does not allow that.  
But I think it's legal to provide installer scripts so the building of final-images from our base-images happens locally
on user's PC.  
The installation of those agents is trivial as well as the Dockerfile for it.  
Basically the `Dockerfile` and an `agents/<agent>/` folder from `aicage-image` would be enough to build.  

It would take careful integration into the current `aicage` process of determining final-images for a given agent but
should be possible with good planning.

#### Non-redistributable agents: Basic process

1. Non-redistributable agents are defined in the `aicage-image` project alongside the existing agents. One of:
   - Either as `agents/<AGENT>/` with a special flag in their `agents/<AGENT>/agent.yml`.
   - Or in a separate folder structure like `agents-non-redistributable/<AGENT>/`.
2. Testing: I really want those additional agents tested in CI pipelines.
   Important: We cannot push images with those agents to repositories (at least not public ones but better not at all).  
   But without persisting the final-images with those agents, the current mechanism for to detect when final-images must
   be rebuilt does not work.
   Suggest something to detect changes in base-images and agent-version to test agent-base image combinations for those
   non-redistributable agents. This may involve persisting information about those combos somewhere.
3. Packaging:
   - The configuration of non-redistributable agents must be in release artifacts of `aicage-image`.
   - Those artifacts must be used when packaging/releasing `aicage` so configuration of non-redistributable agents is
     packaged into `aicage` and can be used at runtime.
4. At runtime in `aicage`:
   - Towards users, those non-redistributable agents are treated like normal agents.
   - The change is where `aicage` currently determines if a new version of a final-image must be pulled. Here `aicage`
     must instead:
     1. Ask user which base he wants to get agent-base combination (same as for normal agents).
     2. Look up information about the base-image
     3. Run `version.sh` for the agent (possibly in a new `aicage-builder` image for `aicage`)
     4. Look at locally stored final-images for the agent-base combination.
     5. With the information from 2.-4. decide if the local final-image should be rebuilt.
     6. Possibly rebuilt local final image for the agent-base combination.
     7. Continue with the normal `aicage` process.

#### Non-redistributable agents: Documentation

This new way of adding agents and building them locally is `aicage` internal. The documentation must be for `aicage`
developers and not for users.

### Custom local agents

Users shall be able to define their own local agents in `~/.aicage/custom/agents/<AGENT>/`.
This is intended for private or experimental agents that are not part of `aicage-image`.

Structure should match `agents/<AGENT>/` from `aicage-image` as closely as possible:

- `agent.yml` with agent metadata and configuration.
- `install.sh` for agent installation during image build.
- `version.sh` to determine the agent version for update checks.
- Optional additional files referenced by `install.sh`.

Behavior:

- Those agents are treated like non-redistributable agents regarding version checks, image update checks, and
  local building.
- They are visible to users in the same way as other agents, but only on the local machine.

### Extensions for final-images

Some users will definitely want to add packages to final images.

Example:
To test GitHub pipelines, I missed `act` installed in the final image `ghcr.io/aicage/aicage:codex-fedora`.  
But for sure I will not add this to all base-images as `act` is not common enough.

#### Extensions for final-images: Basic solution idea

##### Extensions for final-images: Local extension configuration

Users can locally define extensions to final-images, for example in a `~/.aicage/custom/extension/<EXTENSION>/` folder, with
one such folder per extension.

Contents of `~/.aicage/custom/extension/<EXTENSION>/`:
- Dockerfile (optional):
  - Used to build the final image. If not present, `aicage` uses a builtin Dockerfile for this.
  - This needs good documentation for users writing this with an example and all possible ARG variables and similar well
    described in a dedicated Markdown document in project `aicage`.
- Installation scripts:
  - One or several (documented execution in alphabetical order) installation scripts which install
    or setup things during the image build.
  - Prefer `RUN --mount=type=bind,source=scripts,target=/tmp/aicage/scripts,readonly` over script copying in the builtin
    Dockerfile.
  - In the built-in Dockerfile, handle cases where the install-scripts are not executable (copy-chmod or error-exit).
- `extension.yml`:
  - Contains metadata for the extension like a description and display name.

>  The installation scripts and the process is base-image agnostic meaning there is not configuration to which base-
    or final-image an extension shall be applied. Meaning: installation-scripts typically call the package manager of 
    a distro (dnf, apt, etc.) and this does not work for all final-images as they might be based on another distro.  
    But this is ok as users typically chose a base matching their host OS.  
    If they really need an extension on several distros, then they can either define the extension twice with separate
    extension names or handle distros in their extension installation-scripts.

##### Extensions for final-images: Local extended final images

A final-image (agent+base) together with a set of extensions and a name for the final image form an
`extended final image`.

Such a configuration shall be stored in `~/.aicage/custom/image-extended/<CUSTOM_FINAL_IMAGE>/`.

When user is asked for a base-image to an agent, those extended-final-images shall be included if they are built for the
agent. When user selects such an extended-final-image, he shall not be asked for extensions to it.

##### Extensions for final-images: Processes in `aicage`

###### Extensions for final-images: Image selection process

1. On first call of `aicage <AGENT>` with an agent in a project folder, the user is currently asked for a base-image to
   the agent to get the final-image (agent+base combo) . That is stored as config for subsequent runs with same agent
   and same project folder.
2. When a normal base-image is selected and extensions are defined in `~/.aicage/custom/extension/<EXTENSION>/`, then
   `aicage` shall let user select 0-n of them.
3. The image name for the local image shall be `aicage-extended` without the docker registry.  
   Example:  
   Aicage final image name is 'ghcr.io/aicage/aicage', the custom extended images are named just `aicage-extended`.
4. As image tag, aicage shall take the final-image tag and append something like '-extensions' and -<EXTENSION> for
   each extension.
5. Aicage shall then store the configuration for the `~/.aicage/custom/image-extended/<CUSTOM_FINAL_IMAGE>/`

###### Extensions for final-images: Image building/updating process

`aicage` currently checks if remotely a new version of a final-image is available and pulls it before docker-run.

For local extended final images this must be a bit different:
- It shall check online if the final-image (which the extended final image is based upon) has a newer version.
- If so or locally the extended final image is not present, then `aicage` shall build the extended final image
  (possibly using an `aicage-builder` image) and store it locally.
- Log output of building shall go to a log-file after telling user that building is started and where the log-file is.

#### Extensions for final-images: Documentation

As this is user oriented and users must add exact config files in an exact structure, this must be very well documented
for end-users with examples, etc.

Additional information for `aicage` developers can be a bit sparse as it should only contain what is not covered in the
extensive documentation for end-users.

### Custom local base-images

> I am not really sure yet how to implement this as especially the image selection process with extensions and locally
> built extended final images plus these custom local base images starts to look really complex.

Sooner or later some users will need other base images, for example based upon an exotic linux distro.

So it would be nice to let users define such local custom base-images in
`~/.aicage/custom/image-base/<CUSTOM_BASE_IMAGE>/` in a format very similar to the `bases/<BASE>/` folders
in `aicage-image-base`.

The processes in `aicage` should pretty much remain the same.

#### Custom local base-images: Image build process

But when such a custom base is selected for an agent, then:
1. `aicage` must first build it locally to a local base-image:
   - image name: `aicage-image-base-custom`
   - image tag: `<CUSTOM_BASE_IMAGE>`, the alias to the base
2. Then locally add the agent (using the agent configuration) and store the resulting image locally.

#### Custom local base-images: Image update process

When a custom local base-images is selected for an agent and the image for agent-base combo exists locally, then
`aicage` must check if the image needs updating before running it. This shall be based on these checks:
- Agent version: using `version.sh`
- Check if the `root_image` defined in `base.yml` has a newer version available online.

### `aicage-builder` images

For local building of images and also local version-checks for non-redistributable agents it might be better to use a
dedicated docker image as some tools might not be installed locally:
- tools to build images should be available
- `npm` for agent-version checks might not be available

If we do this, it will be in a separate git repo, or maybe even two if we decide for separate images for image-building
and the version check.

Here I want your opinion and/or suggestions towards this idea.
See `doc/ai/task/12/12-AICAGE-BUILDER.md` for pros/cons and options.

## Open questions / needs definition

- Image selection rules across normal, non-redistributable, and custom agents plus extensions and custom base images
  should stay flexible for now and may evolve during subtasks.
- Local build/update metadata shall be stored as files somewhere under `~/.aicage/` (exact structure to be defined).
- Agent version checks: try option A (image), on error try option B (host), on error fail hard.
- Build failures: show a short error to the user and point to the log file location.
- `agent.yml` fields rely on existing docs and schema; `extension.yml` is expected to be minimal (description and name).

## Task splitting into subtasks

All those changes together are too much for one coding session with an AI coding agent. Especially testing and tuning
tends to eat up the context window.

So this shall be split into several subtasks from early on with these steps and considerations:
- One subtask first just for defining the sub-tasks. This task involves splitting into subtasks without already hard
  defining implementation details. For each subtask it creates a subfolder of `doc/ai/task/12` like `doc/ai/task/12/01`
  for subtask 1 and a document `01-SUBTASK.md` in it. `01-SUBTASK.md` describes the subtask and references this document
  plus other important documents like `AGENTS.md` and the `SubTask Workflow` from below (or it tends to be ignored).
- Each subtask is autonomous while keeping the entire task and the other subtasks in mind to not block or handicap other
  subtasks.
- Each subtask results in well-structured code following existing coding and testing guidelines. All tests must succeed,
  test coverage must be good and I want to review and fine-tune the changes for each subtask.
- At the end of a subtask, a subtask summary document must be created in the subtask folder. Use the template in
  doc/ai/task/12/SUBTASK-SUMMARY-TEMPLATE.md and adapt as needed. This must be part of the focus for following
  subtasks (subtask document shall contain instructions to read these from other subtasks). Lessons learned is
  always nice to have in such a document, especially when you encounter a tense discussion or misunderstandings
  between me and you.

## Task/SubTask Workflow

Don't forget to read AGENTS.md and always use the existing venv.

You shall follow this order:
1. Read documentation and code to understand the task. 
2. Ask me questions if something is not clear to you
3. Present me with an implementation solution - this needs my approval
4. Implement the change autonomously including a loop of running-tests, fixing bugs, running tests
5. Run linters as in the pipeline `.github/workflows/publish.yml`
6. Present me the change for review
7. Interactively react to my review feedback
8. Do not create the subtask summary unless and until I explicitly tell you to do so.
9. Do not commit any changes unless explicitly instructed by the user. Remind him about it when you think committing is
   due.
