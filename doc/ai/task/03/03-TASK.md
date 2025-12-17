# Task 03: Add more packages to base-images

The focus of the task shall be to add more packages to base images. Currently, the base images lack packages for 
development of various programming languages and I want to change that.

We will start with one base distro "Fedora/RedHat" first and do the others later.

Further material on this topic is in this repo at:
- doc/ideas/IDEAS.md: Section "## More packages in base images"
- doc/ideas/details/polyglot_agentic_coding_base_image_debian.md: Basic summary by ChatGPT of packages I should add
  This document is a rough draft and the lists of packages mentioned are not definite and final.

## Current Fedora base image packages

Base images are built in the submodules `aicage-image-base`. In there these files are relevant:
- Dockerfile: Very slim, mostly calls a shell script for installations
- bases/fedora/base.yaml: Tells `aicage` where to find the shell script for installations
- scripts/os-installers/os-setup_debian.sh: The shell script for RedHat/Fedora.
  This shell script calls a few other scripts:
  - scripts/os-installers/helpers/install_node.sh 
  - scripts/os-installers/helpers/install_python.sh
  - scripts/os-installers/helpers/install_docker_redhat.sh

## Structure of future package installation

With a large list of packages I do not want too much installation in one script but rather need some logical structure.

I like having:
- a folder `scripts/os-installers/generic` for installation scripts to be used in several base-distros.  
  `scripts/os-installers/helpers/install_python.sh` currently is such a script. The difference for distros is small 
  (one special case for Alpine) so it's nice to have one script only.
- a `scripts/os-installers/distro/redhat` folder for RedHat specific installation. There should be on start shell script 
  (like now `scripts/os-installers/os-setup_redhat.sh`) which calls the other scripts. Thus, to docker this is one step 
  and only generated one image-diff (or whatever docker calls the build step diffs).
  The filename of this one script shall be `install.sh` as the folder already contains `redhat`.
  This script can contain very basic installation steps like `apt update` (debian) and the cleanup steps at the end.
- a `scripts/os-installers/distro/redhat/install` folder with the other scripts. The file names in here must be prefixed
  with a numbering scheme and a describing name like `05-java.sh` and the one script in `distro/redhat` simply starts
  all scripts in `distro/redhat/install` in the numbered order.
  If one of the scripts in here can be replaced with a script from folder `generic`, then use a minimal wrapper as a 
  symlink might not work on Windows

## Tests

I want some tests for those package categories. We do not need to test every single package but rather test important 
functionality.  
With Java for example: Are the tools to develop with Java present (java, maven, ant, Gradle, ...). Testing if they are 
usable is optional and only for key stuff.

### Structure of tests

I surely do not want all tests in one huge file but rather a similar logical structure as with the package installation.
Meaning: a place for `generic` files, a per distro structure (if needed), same numbering/naming scheme:
For a `/install/05-java.sh` there should be `test/05-java.*` file.

## Workflow for this task

I want you to:
1. Read the material (documentation, code, etc.)
2. Ask me questions if anything needs clarification. You may also suggest changes/extensions to the approach here.  
   This step is interactive between you and me.
3. Present me an implementation plan for my review. This needs my approval.
4. Implement the change for redhat/fedora including the test.
5. Run linters. To see how: read AGENTS.md (in this repo and submodule) and always use the existing venv in each repo.
6. Do NOT build images or run the full image-tests yourself unless I tell you so. Reason: large output and you reading 
   that costs me tokens/money. Let me build/test and tell you the problems I see.
  If I tell you to build or test, run one of these commands in the submodule with a high timeout especially for build:
   - `./scripts/build.sh --platform linux/amd64 --base fedora`
   - `./scripts/test.sh --image wuodan/aicage-image-base:fedora-latest`

Is this task clear to you?