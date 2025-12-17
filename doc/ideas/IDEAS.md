# aicage: Ideas for future enhancements

## Use Agent version

We can use the version of an agent to:

### Tag aicage final images

Like:
  - wuodan/aicage:codex-fedora-0.72.0 (codex version = 0.72.0)
  - wuodan/aicage:codex-fedora-latest (existing)

The '-latest' tag can remain as it makes handling much easier.

### New agent version triggers image build

See pipeines in https://github.com/Wuodan/factoryai-droid-docker:
- one scheduled checks for new version and triggers
- build pipeline

`droid` here is actually complicated (wget script, parse version) while other tools can be queried with npm or pipx.

## Read image metadata from remote images

Now we use hub.docker API to read all image tags, then parse the image tags to get available images for a given tool:
<tool>-<base>-latest (example: codex-fedora-latest -> given tool `codex` base `fedora` is available)

It works but is limited to this one information. Will not work for custom user images nicely.

Better would be to read image metadata, there we can store more and better.

But docker itself can read full metadata only for local images. `skopeo` can do it for remote images.

To use `skopeo` in `aicage` it has to be either installed (pre-requisite) or we bundle the skopeo binary.  
See [details/bundling-go-binary-in-pypi.md](details/bundling-go-binary-in-pypi.md) for bundling binary.

## Match working directory in container to host project folder name

Using /workspace in container gets confusing. At minimum use the same folder name as host, much better would be to use 
the full path as on host.

The full path in container is also written to agent config (on host) so a match to host path would be really nice but 
might not work on Windows.

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


## More packages in base images

Now the base iamges are useful for Python and possibly Node development. But for Java, C, C++, C#, Rust, .NET ... 
we need more packages pre-installed.

See [details/polyglot_agentic_coding_base_image_debian.md](details/polyglot_agentic_coding_base_image_debian.md).

Sadly the images will grow in size.

## More CLI Coding Agents – Landscape Snapshot

Reference list and inspiration:
https://github.com/toolstud-io/LlmBrains  
(LLM Brains JetBrains plugin – simple dropdown launcher for externally installed CLI agents)

### Core / Major Players (still highly relevant)
- **Claude Code** (`claude`) – Anthropic
- **Codex CLI** (`codex`) – OpenAI
- **GitHub Copilot CLI** (`copilot`)
- **Gemini CLI** (`gemini`) – Google
- **Qwen Code** (`qwen`) – Alibaba
- **OpenCode** (`opencode`)

### Missing but Worth Considering
- **Cline** – autonomous coding agent, popular with Claude/OpenAI backends
- **Cursor CLI** – terminal companion to Cursor IDE workflows
- **ForgeCode** – community‑driven CLI coding agent
- **Cosine / similar community CLIs** – occasionally referenced in agent roundups

### Niche / Secondary (useful, but not mainstream)
- **Amp CLI** (Sourcegraph)
- **Crush** (Charm)
- **Droid** (Factory AI)
- **Goose** (Block)
- **Grok CLI** (xAI)
- **Qodo**
- **VT Code**
- **Warp CLI** (terminal with agent features, not a pure coding agent)

## Rename user in Ubuntu

Normally we use the user name from the host. But on `ubuntu` there already is a user with UID 1000 and we don't touch 
it. I heard in this case renaming user (same UID) is safe.

## Change working dir in image

Now we mount the project into `/workspace` and sometimes this might not feel "like on the host".  
At the minimum, work in a subfolder of `/workspace` with same dir name as on host.  
This does NOT require a new ENV var to the container as there will be only ONE subfolder to /workspace and the 
entrypoint.sh can simply `cd` into that.