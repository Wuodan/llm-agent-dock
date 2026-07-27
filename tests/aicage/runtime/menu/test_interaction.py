from unittest import TestCase

from aicage.reporting import ConsoleOperationReporter
from aicage.runtime.menu import interaction
from aicage.runtime.menu.textual.services.execution_reporting import ExecutionReporter


class CreateRuntimeInteractionTests(TestCase):
    def test_create_runtime_interaction_returns_textual_interaction_for_ui_mode(
        self,
    ) -> None:
        resolved = interaction.create_runtime_interaction("ui")

        self.assertEqual("TextualInteraction", resolved.__class__.__name__)
        self.assertIsInstance(resolved.reporter, ExecutionReporter)

    def test_create_runtime_interaction_returns_none_interaction_for_none_mode(
        self,
    ) -> None:
        resolved = interaction.create_runtime_interaction("none")

        self.assertEqual("_NoneInteraction", resolved.__class__.__name__)
        self.assertIsInstance(resolved.reporter, ConsoleOperationReporter)

    def test_create_runtime_interaction_returns_simple_interaction_for_simple_mode(
        self,
    ) -> None:
        resolved = interaction.create_runtime_interaction("simple")

        self.assertEqual("SimpleInteraction", resolved.__class__.__name__)
        self.assertIsInstance(resolved.reporter, ConsoleOperationReporter)
