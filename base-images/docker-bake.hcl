variable "AICAGE_BASE_REPOSITORY" {
  description = "Repository namespace/image for base layers."
}

variable "AICAGE_CACHE_DIR" {
  description = "Local cache root for builds."
  default     = ".buildx-cache"
}

target "base" {
  context = "base-images"
  dockerfile = "Dockerfile"
  platforms = [
    for platform in split(" ", AICAGE_PLATFORMS) : platform
  ]
}

variable "AICAGE_PLATFORMS" {
  description = "Space-separated platform list (linux/amd64 linux/arm64)."
}
