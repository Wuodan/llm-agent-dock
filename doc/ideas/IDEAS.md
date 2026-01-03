# aicage: Ideas for future enhancements

## Enable and document custom images by user

I can build and use locally but need to use the same image-names. It would be nice if we could (by config?) add any 
custom image to `aicage`. I'm not yet sure how, possibly by name (regex?), possibly by setting an image registry and 
filtering there based on image metadata (see other idea).

### Let user define extra installed packages

We could let user define a list (or installation script) for his chosen `aicage` image. Those packages would then be 
locally added to a local image and that image used by `aicage`.

Extra nice and rather cheap would then be: Whenever aicage pulls a new image, the custom packages are auto-added and a 
new local image is built.

This might also be helpful or fulfill most custom image use-cases.

## Validate image signature and provenance

The images produced by `aicage-image` and `aicage-image-base` are signed and have provenance.

We should add logic to verify we are using signed/provenanced images in:
- `aicage-image`: When we use the base-images in CI pipelines from `aicage-image-base`
- `aicage`: when we pull/use final-images produced by `aicage-image`

## Support symlinks in project-folder

If the project-folder contains symlinks to outside it's structure, then those fail in containers.  
To fix this we could collect such symlinks and propose to mount the targets to the containers.

## Support git submodules

Detect when in submodule and suggest to mount the parent repo.  
Reason: git in container fails without parent repo

## Centralize docker access

Right now docker is used in several places. Centralize that into one clean package.

## Centralize string constants for yaml values

Those strings should be cleanly centralized in one place.

## Integration tests with scenarios simulating user environment and actions

To largely automate my manual tests

Examples:
- docker not installed (ok, a unit-test can cover that)
- npm not installed but used in a version.sh (local agents or local custom agents)
- happy case process for actions user can do:
  - local agents
  - local custom agents
  - extensions
  - custom bases
  - combinations of those with or without npm installed, util-image used or not, etc

## Replace remove `aicage --entrypoint`

This overrides the same parameter to docker run. And with `docker run --entrypoint` user can do the same. We have it
only for debugging anyway.

## Fix silent pull of util-image

When aicage uses the util-image, it does a docker-run which pulls the image. But the user is kept waiting wondering
what's going on. On my Raspberry Pi 4 this takes a while.
