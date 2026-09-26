#!/usr/bin/env python3
"""Tests for tools/site_post.py. Runs entirely against a temp repo copy —
never against the real content/ or index.html."""

from __future__ import annotations

import shutil
import struct
import subprocess
import sys
import unittest
import zlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_POST = REPO_ROOT / "tools" / "site_post.py"

INDEX_TEMPLATE = """<!doctype html>
<html><body>
<section id="library">
  <!-- content:library:start -->
  <!-- content:library:end -->
</section>
</body></html>
"""

MAIN_WORK_MD = """---
schema: olimazi-site-copy/v1
section: main-work
site_repo: X
target: index.html
region: main-work
---

# Heading

hi
"""


def make_png(width: int, height: int) -> bytes:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data))

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = b"".join(b"\x00" + bytes([255, 0, 0] * width) for _ in range(height))
    idat = zlib.compress(raw)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


class SitePostTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self._temp_dir())
        self.repo = self.tmp / "olimazi-online"
        (self.repo / "content" / "library").mkdir(parents=True)
        (self.repo / "assets").mkdir(parents=True)
        (self.repo / "tools").mkdir(parents=True)
        (self.repo / "index.html").write_text(INDEX_TEMPLATE, encoding="utf-8")
        (self.repo / "content" / "main-work.md").write_text(MAIN_WORK_MD, encoding="utf-8")
        shutil.copy2(SITE_POST, self.repo / "tools" / "site_post.py")
        shutil.copy2(REPO_ROOT / "tools" / "render_collection.py", self.repo / "tools" / "render_collection.py")

        self.body_file = self.tmp / "caption.txt"
        self.image = self.tmp / "photo.png"
        self.image.write_bytes(make_png(200, 100))

    def _temp_dir(self) -> str:
        import tempfile
        d = tempfile.mkdtemp(prefix="site_post_test_")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return d

    def _seed_library_item(self, order: str, slug: str, title: str):
        path = self.repo / "content" / "library" / f"{order}-{slug}.md"
        path.write_text(
            "---\n"
            "schema: olimazi-site-copy/library-item/v1\n"
            "status: active\n"
            "---\n\n"
            f"# Title\n\n{title}\n\n"
            "# Subtitle\n\nposts\n\n"
            "# Caption\n\ncaption\n\n"
            f"# Images\n\nassets/{slug}.png\n\n"
            "# Height\n\n240px\n\n"
            "# Height Mobile\n\n150px\n\n"
            "# Aspect\n\n1.333\n",
            encoding="utf-8",
        )
        (self.repo / "assets" / f"{slug}.png").write_bytes(make_png(240, 180))

    def run_tool(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(self.repo / "tools" / "site_post.py"), *args],
            cwd=self.repo, capture_output=True, text=True,
        )

    def test_entry_prepended_and_shows_first(self):
        self._seed_library_item("01", "old-one", "Old One")
        self.body_file.write_text("A brand new caption line.\n\nMore detail here.", encoding="utf-8")

        result = self.run_tool(
            "--section", "library", "--title", "Brand New Post",
            "--body-file", str(self.body_file), "--image", str(self.image),
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        new_file = self.repo / "content" / "library" / "01-brand-new-post.md"
        self.assertTrue(new_file.exists())
        old_file = self.repo / "content" / "library" / "02-old-one.md"
        self.assertTrue(old_file.exists(), "old entry should be renamed, not lost")

        index_text = (self.repo / "index.html").read_text(encoding="utf-8")
        new_pos = index_text.index("Brand New Post")
        old_pos = index_text.index("Old One")
        self.assertLess(new_pos, old_pos, "newest entry must render before the old one")

    def test_existing_entries_kept(self):
        self._seed_library_item("01", "keep-me", "Keep Me")
        self._seed_library_item("02", "and-me", "And Me")
        self.body_file.write_text("Fresh content.", encoding="utf-8")

        result = self.run_tool(
            "--section", "library", "--title", "Fresh Post",
            "--body-file", str(self.body_file), "--image", str(self.image),
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        md_files = sorted(p.name for p in (self.repo / "content" / "library").glob("*.md"))
        self.assertEqual(md_files, ["01-fresh-post.md", "02-keep-me.md", "03-and-me.md"])
        index_text = (self.repo / "index.html").read_text(encoding="utf-8")
        for title in ("Fresh Post", "Keep Me", "And Me"):
            self.assertIn(title, index_text)

    def test_image_name_collision_suffixed(self):
        # Pre-seed an asset that would collide with the new post's derived name.
        (self.repo / "assets" / "collide-post.png").write_bytes(b"existing-bytes")
        self.body_file.write_text("Some caption text.", encoding="utf-8")

        result = self.run_tool(
            "--section", "library", "--title", "Collide Post",
            "--body-file", str(self.body_file), "--image", str(self.image),
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        original = (self.repo / "assets" / "collide-post.png").read_bytes()
        self.assertEqual(original, b"existing-bytes", "must never overwrite an existing asset")
        suffixed = self.repo / "assets" / "collide-post-2.png"
        self.assertTrue(suffixed.exists(), "colliding image must be suffixed, not skipped")

    def test_unknown_section_refused(self):
        self.body_file.write_text("text", encoding="utf-8")
        result = self.run_tool(
            "--section", "bogus", "--title", "X",
            "--body-file", str(self.body_file), "--image", str(self.image),
        )
        self.assertNotEqual(result.returncode, 0)

    def test_work_and_learning_refused_before_touching_index(self):
        before = (self.repo / "index.html").read_bytes()
        self.body_file.write_text("text", encoding="utf-8")
        for section in ("work", "learning"):
            result = self.run_tool(
                "--section", section, "--title", "X",
                "--body-file", str(self.body_file), "--image", str(self.image),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(section, result.stderr)
        self.assertEqual((self.repo / "index.html").read_bytes(), before)

    def test_render_marker_region_updated(self):
        self.body_file.write_text("Marker test caption.", encoding="utf-8")
        result = self.run_tool(
            "--section", "library", "--title", "Marker Test",
            "--body-file", str(self.body_file), "--image", str(self.image),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        index_text = (self.repo / "index.html").read_text(encoding="utf-8")
        start = index_text.index("<!-- content:library:start -->")
        end = index_text.index("<!-- content:library:end -->")
        self.assertIn("Marker Test", index_text[start:end])

    def test_lead_moves_entry_first_and_keeps_the_rest_in_order(self):
        self._seed_library_item("01", "alpha", "Alpha Entry")
        self._seed_library_item("02", "beta", "Beta Entry")
        self._seed_library_item("03", "gamma", "Gamma Entry")

        result = self.run_tool("--lead", "gamma")
        self.assertEqual(result.returncode, 0, result.stderr)

        md_files = sorted(p.name for p in (self.repo / "content" / "library").glob("*.md"))
        self.assertEqual(md_files, ["01-gamma.md", "02-alpha.md", "03-beta.md"])
        index_text = (self.repo / "index.html").read_text(encoding="utf-8")
        self.assertLess(index_text.index("Gamma Entry"), index_text.index("Alpha Entry"))
        self.assertLess(index_text.index("Alpha Entry"), index_text.index("Beta Entry"))
        self.assertIn("nothing committed", result.stdout)

    def test_lead_unknown_or_inactive_slug_refused(self):
        self._seed_library_item("01", "alpha", "Alpha Entry")
        self._seed_library_item("02", "hidden", "Hidden Entry")
        hidden = self.repo / "content" / "library" / "02-hidden.md"
        hidden.write_text(hidden.read_text(encoding="utf-8").replace("status: active", "status: draft"),
                          encoding="utf-8")
        for slug in ("nope", "hidden"):
            result = self.run_tool("--lead", slug)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(slug, result.stderr)
        self.assertTrue((self.repo / "content" / "library" / "01-alpha.md").exists())

    def test_lead_deploy_commits_library_only_and_pushes_to_a_local_remote(self):
        self._seed_library_item("01", "alpha", "Alpha Entry")
        self._seed_library_item("02", "beta", "Beta Entry")
        remote = self.tmp / "remote.git"
        subprocess.run(["git", "init", "--bare", "-b", "main", str(remote)], check=True, capture_output=True)

        def git(*args):
            return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
                                  cwd=self.repo, capture_output=True, text=True)

        git("init", "-b", "main")
        git("add", "-A")
        git("commit", "-m", "seed")
        git("remote", "add", "origin", str(remote))
        (self.repo / "stray.txt").write_text("another session's file", encoding="utf-8")
        git("add", "stray.txt")

        env_repo = dict(**__import__("os").environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
                        GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        result = subprocess.run(
            [sys.executable, str(self.repo / "tools" / "site_post.py"), "--lead", "beta", "--deploy"],
            cwd=self.repo, capture_output=True, text=True, env=env_repo,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("pushed to origin main", result.stdout)
        pushed = subprocess.run(["git", "--git-dir", str(remote), "ls-tree", "-r", "--name-only", "main"],
                                capture_output=True, text=True).stdout
        self.assertIn("content/library/01-beta.md", pushed)
        self.assertNotIn("content/library/01-alpha.md", pushed)
        self.assertNotIn("stray.txt", pushed)

        again = subprocess.run(
            [sys.executable, str(self.repo / "tools" / "site_post.py"), "--lead", "beta", "--deploy"],
            cwd=self.repo, capture_output=True, text=True, env=env_repo,
        )
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertIn("nothing to deploy", again.stdout)

    def test_touched_paths_splits_renames(self):
        sys.path.insert(0, str(self.repo / "tools"))
        self.addCleanup(sys.path.remove, str(self.repo / "tools"))
        import importlib
        module = importlib.import_module("site_post")
        self.assertEqual(
            module.touched_paths(["content/library/01-a.md -> content/library/02-a.md", "index.html"]),
            ["content/library/01-a.md", "content/library/02-a.md", "index.html"],
        )


if __name__ == "__main__":
    unittest.main()
