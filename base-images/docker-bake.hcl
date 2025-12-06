variable "AICAGE_BASE_REPOSITORY" {
  description = "Repository namespace/image for base layers."
}

target "base" {
  context = "base-images"
  dockerfile = "Dockerfile"
  platforms = [
    for platform in split(" ", AICAGE_PLATFORMS) : platform
  ]
  pull = true
}

variable "AICAGE_PLATFORMS" {
  description = "Space-separated platform list (linux/amd64 linux/arm64)."
}
