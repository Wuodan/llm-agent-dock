variable "AICAGE_REPOSITORY" {
  default = "wuodan/aicage"
  description = "Repository namespace/image."
}

variable "AICAGE_VERSION" {
  default = "dev"
  description = "Tag suffix appended as <tool>-<base>-<AICAGE_VERSION>."
}

variable "AICAGE_PLATFORMS" {
  default = "linux/amd64 linux/arm64"
  description = "Space-separated platform list (linux/amd64 linux/arm64)."
}

# Single flexible target; scripts set TOOL/BASE_IMAGE/tags dynamically via --set.
target "agent" {
  context = "./final-images"
  platforms = [
    for platform in split(" ", AICAGE_PLATFORMS) : platform
  ]
  pull = true
}
