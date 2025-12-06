variable "REPOSITORY" {
  default = "wuodan/aicage"
  description = "Repository namespace/image."
}

variable "VERSION" {
  default = "latest"
  description = "Tag suffix appended as <tool>-<base>-<VERSION>."
}

variable "PLATFORMS" {
  default = "linux/amd64,linux/arm64"
  description = "Comma-separated platform list used with --set \"*.platform=...\"."
}

variable "BASES" {
  default = "act,ubuntu"
  description = "Documented base aliases; keep README matrix in sync when editing."
}

variable "TOOLS" {
  default = "cline,codex,droid"
  description = "Documented tool keys; extend when adding new installers."
}

# Shared target - override BASE_IMAGE/TOOL + tags downstream.
target "_agent" {
  context = "."
  platforms = [
    for platform in split(",", PLATFORMS) : trimspace(platform)
    if trimspace(platform) != ""
  ]
  pull = true
}

# Tag format reference:
#   ${REPOSITORY}:<tool>-<base>-${VERSION}

# ---------------------------- Cline variants -----------------------------------
target "cline-act" {
  inherits = ["_agent"]
  args = {
    BASE_IMAGE = "ghcr.io/catthehacker/ubuntu:act-latest"
    TOOL       = "cline"
  }
  tags = ["${REPOSITORY}:cline-act-${VERSION}"]
  labels = {
    "org.opencontainers.image.description" = "Cline CLI / VSCode AI"
  }
}

target "cline-ubuntu" {
  inherits = ["_agent"]
  args = {
    BASE_IMAGE = "ubuntu:24.04"
    TOOL       = "cline"
  }
  tags = ["${REPOSITORY}:cline-ubuntu-${VERSION}"]
  labels = {
    "org.opencontainers.image.description" = "Cline CLI / VSCode AI"
  }
}

# ----------------------------- Codex variants ----------------------------------
target "codex-act" {
  inherits = ["_agent"]
  args = {
    BASE_IMAGE = "ghcr.io/catthehacker/ubuntu:act-latest"
    TOOL       = "codex"
  }
  tags = ["${REPOSITORY}:codex-act-${VERSION}"]
  labels = {
    "org.opencontainers.image.description" = "Codex coding agent"
  }
}

target "codex-ubuntu" {
  inherits = ["_agent"]
  args = {
    BASE_IMAGE = "ubuntu:24.04"
    TOOL       = "codex"
  }
  tags = ["${REPOSITORY}:codex-ubuntu-${VERSION}"]
  labels = {
    "org.opencontainers.image.description" = "Codex coding agent"
  }
}

# ------------------------ Factory Droid variants -------------------------------
target "droid-act" {
  inherits = ["_agent"]
  args = {
    BASE_IMAGE = "ghcr.io/catthehacker/ubuntu:act-latest"
    TOOL       = "droid"
  }
  tags = ["${REPOSITORY}:droid-act-${VERSION}"]
  labels = {
    "org.opencontainers.image.description" = "Factory.AI Droid agent"
  }
}

target "droid-ubuntu" {
  inherits = ["_agent"]
  args = {
    BASE_IMAGE = "ubuntu:24.04"
    TOOL       = "droid"
  }
  tags = ["${REPOSITORY}:droid-ubuntu-${VERSION}"]
  labels = {
    "org.opencontainers.image.description" = "Factory.AI Droid agent"
  }
}

# Add new agent targets above; keep the group list synchronized.

group "matrix" {
  targets = [
    "cline-act",
    "cline-ubuntu",
    "codex-act",
    "codex-ubuntu",
    "droid-act",
    "droid-ubuntu",
  ]
}
