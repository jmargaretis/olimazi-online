import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import render_collection as collection


def make_item(
    slug: str,
    *,
    order: int = 1,
    status: str = "active",
    images: tuple[collection.Image, ...] | None = None,
    notes: tuple[str, ...] = (),
    links: tuple[collection.Link, ...] = (),
    eager: bool = False,
    aspect: str = "1.333",
) -> collection.Item:
    title = slug.replace("-", " ").title()
    return collection.Item(
        path=Path(f"{order:02d}-{slug}.md"),
        slug=slug,
        status=status,
        title=title,
        card_title=title,
        subtitle="test shelf",
        caption="Test caption.",
        notes=notes,
        links=links,
        images=images or (collection.Image(f"assets/{slug}.jpg", title, "Test caption."),),
        height="220px",
        height_mobile="140px",
        aspect=aspect,
        eager=eager,
    )


class CollectionRenderingTests(unittest.TestCase):
    def test_draft_item_is_omitted(self):
        rendered = collection.render_library([make_item("draft-note", status="draft")])
        self.assertEqual(rendered, "")

    def test_sorted_filename_order_controls_page_order(self):
        later = make_item("later", order=9)
        earlier = make_item("earlier", order=2)
        rendered = collection.render_library([later, earlier])
        self.assertLess(rendered.index("Earlier"), rendered.index("Later"))

    def test_optional_notes_and_links_are_absent_without_empty_attributes(self):
        rendered = collection.render_item(make_item("plain"))
        self.assertNotIn("data-body", rendered)
        self.assertNotIn("data-links", rendered)
        self.assertNotIn("data-slides", rendered)

    def test_multi_image_item_renders_slides_json_images_and_deck(self):
        item = make_item(
            "slides",
            images=(
                collection.Image("assets/one.jpg", "One", "First."),
                collection.Image("assets/two.jpg", "Two", "Second."),
            ),
        )
        rendered = collection.render_item(item)
        self.assertIn("data-slides=", rendered)
        self.assertIn('<figure class="slides">', rendered)
        self.assertEqual(rendered.count('loading="lazy"'), 2)
        self.assertIn('<b class="at"></b><b></b>', rendered)

    def test_aspect_is_copied_verbatim(self):
        rendered = collection.render_item(make_item("wide-crop", aspect=".563"))
        self.assertIn("--ar:.563", rendered)

    def test_single_image_title_override_controls_alt_without_changing_item_title(self):
        item = make_item(
            "illustration",
            images=(collection.Image("assets/picture.png", "A wider alt", "Test caption."),),
        )
        rendered = collection.render_item(item)
        self.assertIn('data-title="Illustration"', rendered)
        self.assertIn('alt="A wider alt"', rendered)
        self.assertNotIn('<img class="on"', rendered)

    def test_missing_image_error_names_record_and_file(self):
        path = Path("11-missing.md")
        with self.assertRaisesRegex(
            collection.RenderError, r"11-missing\.md.*assets/does-not-exist\.jpg"
        ):
            collection.parse_images(
                "assets/does-not-exist.jpg", "Missing", "Missing.", path
            )

    def test_repo_content_round_trips_current_shelf_byte_for_byte(self):
        items = collection.load_items(ROOT / "content" / "library")
        self.assertEqual(len(items), 10)
        target = collection.read_text(ROOT / "index.html")
        start, end = collection_region(target)
        self.assertEqual(target[start:end], "\n" + collection.render_library(items) + "\n      ")


def collection_region(target: str) -> tuple[int, int]:
    start_marker = "<!-- content:library:start -->"
    end_marker = "<!-- content:library:end -->"
    return target.index(start_marker) + len(start_marker), target.index(end_marker)


if __name__ == "__main__":
    unittest.main()
