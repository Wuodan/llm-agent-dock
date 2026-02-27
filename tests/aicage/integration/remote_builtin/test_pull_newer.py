from pathlib import Path

import pytest

from aicage.config.agent.loader import load_agents
from aicage.config.base.loader import load_bases
from aicage.constants import IMAGE_REGISTRY, IMAGE_REPOSITORY
from aicage.docker.query import get_local_repo_digest_for_repo, local_image_exists

from .._helpers import (
    assert_old_image_replaced,
    remove_image,
    replace_with_dummy_image,
    require_integration,
    run_agent_version,
    setup_workspace,
)

pytestmark = pytest.mark.integration

def test_builtin_agent_pulls_newer_digest(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    require_integration()
    workspace, env = setup_workspace(monkeypatch, tmp_path, "copilot")
    bases = load_bases()
    agents = load_agents(bases)
    image_ref = agents["copilot"].valid_bases["ubuntu"]
    old_image_ref = replace_with_dummy_image(image_ref)
    repository = f"{IMAGE_REGISTRY}/{IMAGE_REPOSITORY}"
    assert local_image_exists(old_image_ref)
    try:
        run_agent_version(env, workspace, "copilot")

        local_digest_after = get_local_repo_digest_for_repo(image_ref, repository)
        assert local_digest_after is not None
        assert_old_image_replaced(old_image_ref, image_ref)
    finally:
        remove_image(image_ref, force=True)
