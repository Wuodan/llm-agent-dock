from unittest import TestCase, mock

from aicage.registry._errors import RegistryError
from aicage.registry.agent_build import _refresh
from aicage.registry.agent_build._refresh import _BaseRefreshAction


class RefreshBaseDigestTests(TestCase):
    def test_refresh_base_image_pulls_tag_when_local_tag_missing(self) -> None:
        reporter = mock.Mock()
        with (
            mock.patch(
                "aicage.registry.agent_build._refresh.get_local_repo_digest_for_repo",
                side_effect=[None, None],
            ),
            mock.patch(
                "aicage.registry.agent_build._refresh.get_remote_digest",
                return_value="sha256:remote",
            ),
            mock.patch(
                "aicage.registry.agent_build._refresh.resolve_base_digest",
                return_value="ghcr.io/aicage/aicage-image-base@sha256:remote",
            ) as resolve_mock,
        ):
            digest = _refresh.refresh_base_image(
                base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                base_repository="ghcr.io/aicage/aicage-image-base",
                update_approved=False,
                reporter=reporter,
            )

        self.assertEqual("ghcr.io/aicage/aicage-image-base@sha256:remote", digest)
        resolve_mock.assert_called_once_with(
            "ghcr.io/aicage/aicage-image-base:ubuntu",
            "ghcr.io/aicage/aicage-image-base",
            reporter=reporter,
        )

    def test_refresh_base_image_plan_requests_confirmation_when_digests_differ(
        self,
    ) -> None:
        with (
            mock.patch(
                "aicage.registry.agent_build._refresh.get_local_repo_digest_for_repo",
                return_value="sha256:local",
            ),
            mock.patch(
                "aicage.registry.agent_build._refresh.get_remote_digest",
                return_value="sha256:remote",
            ),
        ):
            plan = _refresh.refresh_base_image_plan(
                base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                base_repository="ghcr.io/aicage/aicage-image-base",
            )

        self.assertEqual(
            "ghcr.io/aicage/aicage-image-base@sha256:local", plan.image_ref
        )
        self.assertIs(plan.action, _BaseRefreshAction.CONFIRM_PULL)

    def test_refresh_base_image_plan_uses_remote_digest_without_verification(
        self,
    ) -> None:
        with (
            mock.patch(
                "aicage.registry.agent_build._refresh.get_local_repo_digest_for_repo",
                return_value="sha256:local",
            ),
            mock.patch(
                "aicage.registry.agent_build._refresh.get_remote_digest",
                return_value="sha256:remote",
            ),
        ):
            plan = _refresh.refresh_base_image_plan(
                base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                base_repository="ghcr.io/aicage/aicage-image-base",
            )

        self.assertEqual(
            "ghcr.io/aicage/aicage-image-base@sha256:local", plan.image_ref
        )
        self.assertIs(plan.action, _BaseRefreshAction.CONFIRM_PULL)

    def test_refresh_base_image_uses_local_digest_when_user_declines_pull(self) -> None:
        reporter = mock.Mock()
        with (
            mock.patch(
                "aicage.registry.agent_build._refresh.get_local_repo_digest_for_repo",
                side_effect=["sha256:local", "sha256:local"],
            ),
            mock.patch(
                "aicage.registry.agent_build._refresh.get_remote_digest",
                return_value="sha256:remote",
            ),
            mock.patch(
                "aicage.registry.agent_build._refresh.resolve_base_digest"
            ) as resolve_mock,
        ):
            digest = _refresh.refresh_base_image(
                base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                base_repository="ghcr.io/aicage/aicage-image-base",
                update_approved=False,
                reporter=reporter,
            )
        self.assertEqual("ghcr.io/aicage/aicage-image-base@sha256:local", digest)
        resolve_mock.assert_not_called()

    def test_refresh_base_image_runs_pull_when_user_accepts_pull(self) -> None:
        reporter = mock.Mock()
        with (
            mock.patch(
                "aicage.registry.agent_build._refresh.get_local_repo_digest_for_repo",
                side_effect=["sha256:local", "sha256:local"],
            ),
            mock.patch(
                "aicage.registry.agent_build._refresh.get_remote_digest",
                return_value="sha256:remote",
            ),
            mock.patch(
                "aicage.registry.agent_build._refresh.resolve_base_digest",
                return_value="ghcr.io/aicage/aicage-image-base@sha256:remote",
            ) as resolve_mock,
        ):
            digest = _refresh.refresh_base_image(
                base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                base_repository="ghcr.io/aicage/aicage-image-base",
                update_approved=True,
                reporter=reporter,
            )
        self.assertEqual("ghcr.io/aicage/aicage-image-base@sha256:remote", digest)
        resolve_mock.assert_called_once_with(
            "ghcr.io/aicage/aicage-image-base:ubuntu",
            "ghcr.io/aicage/aicage-image-base",
            reporter=reporter,
        )

    def test_refresh_base_image_uses_verified_digest_when_local_matches_remote(
        self,
    ) -> None:
        reporter = mock.Mock()
        with (
            mock.patch(
                "aicage.registry.agent_build._refresh.get_local_repo_digest_for_repo",
                side_effect=["sha256:local", "sha256:local"],
            ),
            mock.patch(
                "aicage.registry.agent_build._refresh.get_remote_digest",
                return_value="sha256:local",
            ),
            mock.patch(
                "aicage.registry.agent_build._refresh.resolve_base_digest"
            ) as resolve_mock,
        ):
            digest = _refresh.refresh_base_image(
                base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                base_repository="ghcr.io/aicage/aicage-image-base",
                update_approved=False,
                reporter=reporter,
            )
        self.assertEqual("ghcr.io/aicage/aicage-image-base@sha256:local", digest)
        resolve_mock.assert_not_called()

    def test_refresh_base_image_verify_failure_uses_local_digest(self) -> None:
        reporter = mock.Mock()
        with (
            mock.patch(
                "aicage.registry.agent_build._refresh.get_local_repo_digest_for_repo",
                side_effect=["sha256:local", "sha256:local"],
            ),
            mock.patch(
                "aicage.registry.agent_build._refresh.get_remote_digest",
                return_value=None,
            ),
            mock.patch(
                "aicage.registry.agent_build._refresh.resolve_base_digest"
            ) as resolve_mock,
        ):
            digest = _refresh.refresh_base_image(
                base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                base_repository="ghcr.io/aicage/aicage-image-base",
                update_approved=False,
                reporter=reporter,
            )
        self.assertEqual("ghcr.io/aicage/aicage-image-base@sha256:local", digest)
        resolve_mock.assert_not_called()

    def test_refresh_base_image_verify_failure_without_local_raises(self) -> None:
        reporter = mock.Mock()
        with (
            mock.patch(
                "aicage.registry.agent_build._refresh.get_local_repo_digest_for_repo",
                side_effect=[None, None],
            ),
            mock.patch(
                "aicage.registry.agent_build._refresh.get_remote_digest",
                return_value=None,
            ),
        ):
            with self.assertRaises(RegistryError) as context:
                _refresh.refresh_base_image(
                    base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                    base_repository="ghcr.io/aicage/aicage-image-base",
                    update_approved=False,
                    reporter=reporter,
                )
        self.assertIn("Failed to resolve remote digest", str(context.exception))

    def test_refresh_base_image_plan_uses_local_base_when_remote_digest_unavailable(
        self,
    ) -> None:
        with (
            mock.patch(
                "aicage.registry.agent_build._refresh.get_local_repo_digest_for_repo",
                return_value="sha256:local",
            ),
            mock.patch(
                "aicage.registry.agent_build._refresh.get_remote_digest",
                return_value=None,
            ),
        ):
            plan = _refresh.refresh_base_image_plan(
                base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                base_repository="ghcr.io/aicage/aicage-image-base",
            )

        self.assertEqual(
            "ghcr.io/aicage/aicage-image-base@sha256:local", plan.image_ref
        )
        self.assertIs(plan.action, _BaseRefreshAction.USE_LOCAL)

    def test_refresh_base_image_plan_requires_pull_when_local_tag_missing(
        self,
    ) -> None:
        with (
            mock.patch(
                "aicage.registry.agent_build._refresh.get_local_repo_digest_for_repo",
                return_value=None,
            ),
            mock.patch(
                "aicage.registry.agent_build._refresh.get_remote_digest",
                return_value="sha256:remote",
            ),
        ):
            plan = _refresh.refresh_base_image_plan(
                base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                base_repository="ghcr.io/aicage/aicage-image-base",
            )

        self.assertEqual(
            "ghcr.io/aicage/aicage-image-base@sha256:remote", plan.image_ref
        )
        self.assertIs(plan.action, _BaseRefreshAction.PULL_NOW)
