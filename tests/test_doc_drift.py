"""Documentation drift gates for released adjacent profiles and in-repo links."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

RELEASED_PROFILES = (
    "agent-lifecycle/0.1",
    "adapter-profile/0.1",
    "modulation-profile/0.1",
    "attention-projection/0.1",
)

MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
PINNED_ACTION = re.compile(
    r"uses:\s+actions/(checkout|setup-python)@([0-9a-f]{40})\s+#\s+v[\d.]+"
)
FLOATING_ACTION = re.compile(r"uses:\s+actions/(checkout|setup-python)@v\d+")


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def relative_targets(markdown: str) -> list[str]:
    targets = []
    for raw in MARKDOWN_LINK.findall(markdown):
        href = raw.strip()
        if href.startswith(("http://", "https://", "mailto:", "#")):
            continue
        href = href.split("#", 1)[0]
        if href:
            targets.append(href)
    return targets


def resolve_link(source: Path, href: str) -> Path:
    return (source.parent / href).resolve()


class DocumentationDriftTests(unittest.TestCase):
    def test_released_profiles_are_named_in_readme_spec_and_index(self):
        readme = load_text(ROOT / "README.md")
        spec = load_text(ROOT / "spec" / "v1" / "SPEC.md")
        index = load_text(ROOT / "profiles" / "README.md")
        for slug in RELEASED_PROFILES:
            with self.subTest(profile=slug):
                self.assertIn(f"vibenet.{slug}", readme)
                self.assertIn(f"profiles/{slug}/", readme)
                self.assertIn(f"vibenet.{slug}", spec)
                self.assertIn(f"profiles/{slug}/", spec)
                self.assertIn(f"[{slug}]({slug}/)", index)
                self.assertTrue((ROOT / "profiles" / slug).is_dir())

    def test_mcp_source_is_not_claimed_released_on_main(self):
        spec = load_text(ROOT / "spec" / "v1" / "SPEC.md")
        readme = load_text(ROOT / "README.md")
        self.assertNotIn("mcp-source/0.1", spec)
        self.assertNotIn("mcp-source/0.1", readme)

    def test_metadata_conventions_file_exists_and_is_linked(self):
        conventions = ROOT / "spec" / "v1" / "metadata-conventions.md"
        self.assertTrue(conventions.is_file())
        text = load_text(conventions)
        for key in ("publishable", "indexable", "fallback_reason"):
            self.assertIn(f"`{key}`", text)
        spec = load_text(ROOT / "spec" / "v1" / "SPEC.md")
        conformance = load_text(ROOT / "conformance" / "README.md")
        self.assertIn("metadata-conventions.md", spec)
        self.assertIn("spec/v1/metadata-conventions.md", conformance)

    def test_spec_and_conformance_markdown_links_resolve(self):
        files = [
            *(ROOT / "spec").rglob("*.md"),
            *(ROOT / "conformance").rglob("*.md"),
        ]
        missing = []
        for path in files:
            for href in relative_targets(load_text(path)):
                target = resolve_link(path, href)
                try:
                    target.relative_to(ROOT)
                except ValueError:
                    missing.append(f"{path.relative_to(ROOT)} -> {href} (outside repo)")
                    continue
                ok = target.is_file() or target.is_dir()
                if not ok:
                    missing.append(f"{path.relative_to(ROOT)} -> {href}")
        self.assertEqual(missing, [])

    def test_github_actions_are_pinned_to_commit_shas(self):
        workflow = load_text(ROOT / ".github" / "workflows" / "validate.yml")
        self.assertIsNone(FLOATING_ACTION.search(workflow))
        pinned = PINNED_ACTION.findall(workflow)
        names = {name for name, _sha in pinned}
        self.assertEqual(names, {"checkout", "setup-python"})


if __name__ == "__main__":
    unittest.main()
