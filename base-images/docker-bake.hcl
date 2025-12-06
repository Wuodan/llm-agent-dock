variable "AICAGE_BASE_REPOSITORY" {
  default = "ghcr.io/wuodan/aicage-base"
  description = "Repository namespace/image for base layers."
}

target "base" {
  context = "./base-images"
  dockerfile = "./base-images/Dockerfile"
  platforms = [
    for platform in split(" ", AICAGE_PLATFORMS) : platform
  ]
  pull = true
}
