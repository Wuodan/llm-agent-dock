IMAGE_REGISTRY: str = "ghcr.io"
_IMAGE_REGISTRY_API_URL: str = "https://ghcr.io/v2"
_IMAGE_REGISTRY_API_TOKEN_URL: str = (
    "https://ghcr.io/token?service=ghcr.io&scope=repository"
)
IMAGE_REPOSITORY: str = "aicage/aicage"
IMAGE_BASE_REPOSITORY: str = "aicage/aicage-image-base"
DEFAULT_IMAGE_BASE: str = "ubuntu"
VERSION_CHECK_IMAGE: str = "ghcr.io/aicage/aicage-image-util:agent-version"

LOCAL_IMAGE_BASE_REPOSITORY: str = "aicage-image-base"
LOCAL_IMAGE_REPOSITORY: str = "aicage"

DEFAULT_EXTENDED_IMAGE_NAME: str = "aicage-extended"

_COSIGN_IMAGE_NAME: str = "ghcr.io/sigstore/cosign/cosign"
# _COSIGN_IMAGE_DIGEST holds the digest of
# ghcr.io/sigstore/cosign/cosign:latest
# at the time of a release
_COSIGN_IMAGE_DIGEST: str = "sha256:0b015a3557a64a751712da8a6395534160018eaaa2d969882a85a336de9adb70"
COSIGN_IMAGE_REF: str = f"{_COSIGN_IMAGE_NAME}@{_COSIGN_IMAGE_DIGEST}"
COSIGN_OIDC_ISSUER: str = "https://token.actions.githubusercontent.com"
COSIGN_IDENTITY_REGEXP: str = (
    "^https://github.com/aicage/github-actions/.github/workflows/.*@refs/.*/.*$"
)

DOCKER_REGISTRY_REQUEST_TIMEOUT_SECONDS: float = 5.0
REGISTRY_DIGEST_REQUEST_TIMEOUT_SECONDS: float = 4.0
PYPI_VERSION_CHECK_TIMEOUT_SECONDS: float = 3.5
PROJECT_FILE_LOCK_TIMEOUT_SECONDS: int = 30
HOST_VERSION_CHECK_TIMEOUT_SECONDS: float = 15.0
BUILDER_VERSION_CHECK_TIMEOUT_SECONDS: float = 20.0
PROXY_ENV_NAMES: tuple[str, ...] = (
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "NO_PROXY",
)
