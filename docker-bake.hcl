variable "REGISTRY" {
  default = "ghcr.io"
  description = "Registry host (override via AICAGE_REGISTRY)."
}

variable "REPOSITORY" {
  default = "wuodan/aicage"
  description = "Registry namespace/repo (org/image)."
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
  default = "act,universal,ubuntu"
  description = "Documented base aliases; keep README matrix in sync when editing."
}

variable "TOOLS" {
  default = "cline,codex,factory_ai_droid"
  description = "Documented tool keys; extend when adding new installers."
}

# Shared target - override BASE_IMAGE/TOOL + tags downstream.
target "_agent" {
  context = "."
  dockerfile = "Dockerfile"
  platforms = [
    for platform in split(",", PLATFORMS) : trimspace(platform)
    if trimspace(platform) != ""
  ]
  pull = true
}

# Tag format reference:
#   ${REGISTRY}/${REPOSITORY}:<tool>-<base>-${VERSION}

# ---------------------------- Cline variants -----------------------------------
target "cline-act" {
  inherits = ["_agent"]
  args = {
    BASE_IMAGE = "ghcr.io/catthehacker/ubuntu:act-latest"
    TOOL       = "cline"
  }
  tags = ["${REGISTRY}/${REPOSITORY}:cline-act-${VERSION}"]
  labels = {
    "org.opencontainers.image.description" = "Cline CLI / VSCode AI"
  }
}

target "cline-universal" {
  inherits = ["_agent"]
  args = {
    BASE_IMAGE = "mcr.microsoft.com/devcontainers/universal:2-linux"
    TOOL       = "cline"
  }
  tags = ["${REGISTRY}/${REPOSITORY}:cline-universal-${VERSION}"]
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
  tags = ["${REGISTRY}/${REPOSITORY}:cline-ubuntu-${VERSION}"]
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
  tags = ["${REGISTRY}/${REPOSITORY}:codex-act-${VERSION}"]
  labels = {
    "org.opencontainers.image.description" = "Codex coding agent"
  }
}

target "codex-universal" {
  inherits = ["_agent"]
  args = {
    BASE_IMAGE = "mcr.microsoft.com/devcontainers/universal:2-linux"
    TOOL       = "codex"
  }
  tags = ["${REGISTRY}/${REPOSITORY}:codex-universal-${VERSION}"]
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
  tags = ["${REGISTRY}/${REPOSITORY}:codex-ubuntu-${VERSION}"]
  labels = {
    "org.opencontainers.image.description" = "Codex coding agent"
  }
}

# ------------------------ Factory Droid variants -------------------------------
target "factory_ai_droid-act" {
  inherits = ["_agent"]
  args = {
    BASE_IMAGE = "ghcr.io/catthehacker/ubuntu:act-latest"
    TOOL       = "factory_ai_droid"
  }
  tags = ["${REGISTRY}/${REPOSITORY}:factory_ai_droid-act-${VERSION}"]
  labels = {
    "org.opencontainers.image.description" = "Factory.AI Droid agent"
  }
}

target "factory_ai_droid-universal" {
  inherits = ["_agent"]
  args = {
    BASE_IMAGE = "mcr.microsoft.com/devcontainers/universal:2-linux"
    TOOL       = "factory_ai_droid"
  }
  tags = ["${REGISTRY}/${REPOSITORY}:factory_ai_droid-universal-${VERSION}"]
  labels = {
    "org.opencontainers.image.description" = "Factory.AI Droid agent"
  }
}

target "factory_ai_droid-ubuntu" {
  inherits = ["_agent"]
  args = {
    BASE_IMAGE = "ubuntu:24.04"
    TOOL       = "factory_ai_droid"
  }
  tags = ["${REGISTRY}/${REPOSITORY}:factory_ai_droid-ubuntu-${VERSION}"]
  labels = {
    "org.opencontainers.image.description" = "Factory.AI Droid agent"
  }
}

# Add new agent targets above; keep the group list synchronized.

group "matrix" {
  targets = [
    "cline-act",
    "cline-universal",
    "cline-ubuntu",
    "codex-act",
    "codex-universal",
    "codex-ubuntu",
    "factory_ai_droid-act",
    "factory_ai_droid-universal",
    "factory_ai_droid-ubuntu",
  ]
}
