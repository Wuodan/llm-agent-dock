variable "AICAGE_REPOSITORY" {
  description = "Repository namespace/image."
}

variable "AICAGE_VERSION" {
  description = "Tag suffix appended as <tool>-<base>-<AICAGE_VERSION>."
}

variable "AICAGE_PLATFORMS" {
  description = "Space-separated platform list (linux/amd64 linux/arm64)."
}

variable "AICAGE_CACHE_DIR" {
  description = "Local cache root for builds."
  default     = ".buildx-cache"
}

# Single flexible target; scripts set TOOL/BASE_IMAGE/tags dynamically via --set.
target "agent" {
  context = "./final-images"
  platforms = [
    for platform in split(" ", AICAGE_PLATFORMS) : platform
  ]
}
