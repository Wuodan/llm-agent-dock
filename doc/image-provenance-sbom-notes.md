# Image provenance and SBOM notes

Working notes from inspecting `ghcr.io/aicage/aicage:codex-fedora` on 2026-08-24. These are not
user-facing docs yet.

## What is stored where

For an agent image such as `ghcr.io/aicage/aicage:codex-fedora`, the normal image config labels
record the immediate aicage base image:

```text
org.opencontainers.image.base.name=ghcr.io/aicage/aicage-image-base:fedora
org.opencontainers.image.base.digest=sha256:f965324601434adc045c521eb8e1cb79f106d9a6cefdb384075acc635fc8d8e9
```

The original distro `FROM` image digest is not in those labels. It is in the BuildKit provenance
attestation attached to the corresponding `aicage-image-base` image.

For the inspected image, the chain was:

```text
ghcr.io/aicage/aicage:codex-fedora
  -> ghcr.io/aicage/aicage-image-base:fedora
     sha256:f965324601434adc045c521eb8e1cb79f106d9a6cefdb384075acc635fc8d8e9
  -> fedora:latest
     sha256:6c75d5bf57cb0fa5aa4b92c6a83c86c791644496d9ac230de7711f5b8ec3b898
```

## Inspect the agent image

List the OCI index and the per-platform image and attestation manifests:

```bash
docker buildx imagetools inspect ghcr.io/aicage/aicage:codex-fedora
```

The inspected index digest was:

```text
sha256:b15293fd5d540374d64066f97e0099dae4d72c020184b4e7f30ca06b0cc312b5
```

The real platform manifests were:

```text
linux/amd64 sha256:7d33e7dfe866aea5f720524d43ed249ef1dac64cc39e7baec147429d4c99f78b
linux/arm64 sha256:e9b8c33c6259de0f1072890bee6334fb142ed137c91e5e145f8375aa1e28d0ed
```

Read labels from a platform manifest:

```bash
crane config \
  ghcr.io/aicage/aicage:codex-fedora@sha256:7d33e7dfe866aea5f720524d43ed249ef1dac64cc39e7baec147429d4c99f78b |
  jq '.config.Labels'
```

The agent image provenance also records the immediate base image dependency:

```bash
crane blob \
  ghcr.io/aicage/aicage@sha256:152da8bf9a89065552be8349e0841d4e1c89f5230ef5bd10bd907e610d00874e |
  jq '.predicate.buildDefinition.resolvedDependencies,
      .predicate.buildDefinition.externalParameters'
```

That showed:

```text
pkg:docker/ghcr.io/aicage/aicage-image-base@fedora
  digest=sha256:f965324601434adc045c521eb8e1cb79f106d9a6cefdb384075acc635fc8d8e9
  platform=linux/amd64
build-arg:BASE_IMAGE=ghcr.io/aicage/aicage-image-base:fedora
  digest=sha256:f965324601434adc045c521eb8e1cb79f106d9a6cefdb384075acc635fc8d8e9
```

## Inspect the base image provenance

Inspect the base image index:

```bash
docker buildx imagetools inspect \
  ghcr.io/aicage/aicage-image-base@sha256:f965324601434adc045c521eb8e1cb79f106d9a6cefdb384075acc635fc8d8e9
```

The real platform manifests were:

```text
linux/amd64 sha256:a2c2b761e87b9045dd6ce810135b90100bba98682c9e559460f1ae2b8a4aed13
linux/arm64 sha256:d99c547ac82b1de98101697222d135b428d0eea174b31db193cb94b972197805
```

The attestation manifests were:

```text
amd64 attestation sha256:07456c3523b9ee8f32e57f7ff0e60864c6c7d7e44ef77fcfe2aba4a0ae119791
arm64 attestation sha256:1f3bcb802826e600b179b102016e8c2e5f3e7d908253ac850aad6f2ef27d11d4
```

Read an attestation manifest to find the SLSA provenance layer digest:

```bash
docker buildx imagetools inspect \
  ghcr.io/aicage/aicage-image-base@sha256:07456c3523b9ee8f32e57f7ff0e60864c6c7d7e44ef77fcfe2aba4a0ae119791 \
  --raw |
  jq '.layers[] | select(.annotations["in-toto.io/predicate-type"] == "https://slsa.dev/provenance/v1")'
```

For amd64, the SLSA provenance layer digest was:

```text
sha256:2ee8cbd64b647f2c6e3ff6341e1677fa93d23b5b640deaaf01c35f2cc629776c
```

Read the provenance:

```bash
crane blob \
  ghcr.io/aicage/aicage-image-base@sha256:2ee8cbd64b647f2c6e3ff6341e1677fa93d23b5b640deaaf01c35f2cc629776c |
  jq '.predicate.buildDefinition.resolvedDependencies,
      .predicate.buildDefinition.externalParameters'
```

That showed:

```text
build-arg:FROM_IMAGE=fedora:latest
pkg:docker/fedora@latest?platform=linux%2Famd64
sha256:6c75d5bf57cb0fa5aa4b92c6a83c86c791644496d9ac230de7711f5b8ec3b898
```

The arm64 base provenance had the same distro image digest:

```text
sha256:6c75d5bf57cb0fa5aa4b92c6a83c86c791644496d9ac230de7711f5b8ec3b898
```

## Read installed packages from the SBOM

The same attestation manifests contain an SPDX SBOM layer:

```bash
docker buildx imagetools inspect \
  ghcr.io/aicage/aicage-image-base@sha256:07456c3523b9ee8f32e57f7ff0e60864c6c7d7e44ef77fcfe2aba4a0ae119791 \
  --raw |
  jq '.layers[] | select(.annotations["in-toto.io/predicate-type"] == "https://spdx.dev/Document")'
```

For the amd64 base image, the SPDX layer digest was:

```text
sha256:1c8640c4301f45157de1f9e515756b52d3bb87f3e159f633b4eb7a0e2a384708
```

Extract package names, versions, and suppliers:

```bash
crane blob \
  ghcr.io/aicage/aicage-image-base@sha256:1c8640c4301f45157de1f9e515756b52d3bb87f3e159f633b4eb7a0e2a384708 |
  jq -r '.predicate.packages[] | [.name, .versionInfo, (.supplier // "")] | @tsv'
```

Example output:

```text
7zip    26.02-1.fc44    Organization: Fedora Project
7zip-standalone    26.02-1.fc44    Organization: Fedora Project
@gar/promise-retry    1.0.3    NOASSERTION
```

The final `aicage:codex-fedora` image also has an SPDX SBOM in its own attestation manifest. Use the
same process against the agent image attestation if the desired package list should include the
agent layer as well as the base layer.

## Notes for future user docs

- `docker buildx imagetools inspect` is enough to find image and attestation manifests.
- `crane config` is convenient for normal labels.
- `crane blob` is convenient for fetching attestation layers by digest.
- BuildKit `provenance: mode=max` preserves the resolved `latest` image digest, so FROM lock files
  are not required just for later auditing.
- The distro `latest` digest is only available after following the provenance chain to the base
  image that actually used `FROM_IMAGE=fedora:latest`.
