# aicage: Ideas for future enhancements

## Use Agent version

We can use the version of an agent to:

### Tag aicage final images

Like:
  - ghcr.io/aicage/aicage:codex-fedora-0.72.0 (codex version = 0.72.0)
  - ghcr.io/aicage/aicage:codex-fedora-latest (existing)

The '-latest' tag can remain as it makes handling much easier.

### New agent version triggers image build

See pipelines in https://github.com/Wuodan/factoryai-droid-docker:
- one scheduled checks for new version and triggers
- build pipeline

`droid` here is actually complicated (wget script, parse version) while other tools can be queried with npm or pipx.

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
