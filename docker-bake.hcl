variable "REPOSITORY" {
  default = "wuodan/aicage"
  description = "Repository namespace/image."
}

variable "VERSION" {
  default = "latest"
  description = "Tag suffix appended as <tool>-<base>-<VERSION>."
}

variable "PLATFORMS" {
  default = "linux/amd64 linux/arm64"
  description = "Space-separated platform list (linux/amd64 linux/arm64)."
}

# Single flexible target; scripts set TOOL/BASE_IMAGE/tags dynamically via --set.
target "agent" {
  context = "."
  platforms = [
    for platform in split(" ", PLATFORMS) : platform
  ]
  pull = true
}
