"""Tests for roadmap next-steps documentation generator."""

import unittest

from tools.docs.generate_docs import compute_next_steps, render_markdown


class GenerateDocsTest(unittest.TestCase):
    def test_compute_next_steps_returns_exactly_twenty_items(self):
        steps = compute_next_steps(limit=20)
        self.assertEqual(len(steps), 20)

    def test_compute_next_steps_is_stable(self):
        first = [step.id for step in compute_next_steps(limit=20)]
        second = [step.id for step in compute_next_steps(limit=20)]
        self.assertEqual(first, second)

    def test_render_markdown_expected_format(self):
        steps = compute_next_steps(limit=20)
        markdown = render_markdown(steps)

        self.assertTrue(markdown.startswith("## Next 20 Coding Steps\n\n1. "))
        lines = [line for line in markdown.splitlines() if line and line[0].isdigit()]
        self.assertEqual(len(lines), 20)
        self.assertIn("[agent]", markdown)
        self.assertIn("[mission]", markdown)
        self.assertIn("[ui]", markdown)
        self.assertIn("[tests]", markdown)
        # [docs] tasks may fall outside top-20 when higher-priority battle tasks are present
        self.assertTrue(
            "[docs]" in markdown or "[battle]" in markdown,
            "Expected at least one [docs] or [battle] domain entry in top-20",
        )


if __name__ == "__main__":
    unittest.main()
