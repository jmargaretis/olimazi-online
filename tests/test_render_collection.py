import sys
import unittest
from pathlib import Path


TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import render_collection as collection


def make_item(
    slug: str,
    *,
    status: str = "active",
    placement: str = "library",
    feature_slot: int | None = None,
    chip: str = "Notes",
    details: tuple[str, ...] = (),
    sources: tuple[tuple[str, str], ...] = (),
) -> collection.Item:
    fields = {
        "Title": slug.title(),
        "Summary": f"{slug} summary",
        "Dialog Chip": f"{slug} notes",
        "Dialog Intro": f"{slug} intro",
        "Card Image": f"assets/{slug}-card.jpg",
        "Card Image Alt": f"{slug} card alt",
        "Dialog Image": f"assets/{slug}-dialog.jpg",
        "Dialog Image Alt": f"{slug} dialog alt",
    }
    if details:
        fields["Detail Heading"] = "Details"
    return collection.Item(
        path=Path(f"{slug}.md"),
        slug=slug,
        status=status,
        placement=placement,
        feature_slot=feature_slot,
        order=10,
        chip=chip,
        fields=fields,
        details=details,
        sources=sources,
    )


class CollectionRenderingTests(unittest.TestCase):
    def test_draft_item_renders_nowhere(self):
        draft = make_item("draft-note", status="draft")

        feature_cards, feature_dialogs = collection.feature_regions([draft])
        library_cards, library_dialogs = collection.library_regions([draft])

        self.assertNotIn("draft-note", feature_cards)
        self.assertNotIn("draft-note", feature_dialogs)
        self.assertNotIn("draft-note", library_cards)
        self.assertNotIn("draft-note", library_dialogs)

    def test_feature_item_does_not_also_render_in_library(self):
        feature = make_item("featured", placement="feature", feature_slot=2)

        feature_cards, feature_dialogs = collection.feature_regions([feature])
        library_cards, library_dialogs = collection.library_regions([feature])

        self.assertIn("featured-dialog", feature_cards)
        self.assertIn("featured-dialog", feature_dialogs)
        self.assertNotIn("featured", library_cards)
        self.assertNotIn("featured", library_dialogs)

    def test_three_active_feature_items_are_a_hard_error(self):
        items = [
            make_item(f"feature-{index}", placement="feature", feature_slot=slot)
            for index, slot in enumerate((1, 2, 1), 1)
        ]

        with self.assertRaisesRegex(collection.RenderError, "at most 2"):
            collection.validate_items(items)

    def test_cta_without_sources(self):
        self.assertEqual(collection.cta_label(make_item("plain")), "Open notes →")

    def test_cta_with_sources_for_non_recipe(self):
        item = make_item(
            "scent",
            sources=(("Source ↗", "https://example.com"),),
        )
        self.assertEqual(collection.cta_label(item), "Open notes and sources →")

    def test_cta_with_sources_for_recipe(self):
        item = make_item(
            "recipe",
            chip="Recipe",
            details=("Step one",),
            sources=(("Recipe ↗", "https://example.com"),),
        )
        self.assertEqual(collection.cta_label(item), "Open notes and recipe →")

    def test_absent_optional_blocks_render_no_empty_dom(self):
        dialog = collection.render_dialog(make_item("plain"), feature=False)

        self.assertNotIn("<h3>", dialog)
        self.assertNotIn("<ul>", dialog)
        self.assertNotIn('class="dialog-links"', dialog)
        self.assertNotIn("<p></p>", dialog)


if __name__ == "__main__":
    unittest.main()
