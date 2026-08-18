# Library how-to

The homepage stacks and `library.html` both read `library.json`. The JSON file is the only content manifest; do not copy library content into either HTML page.

## Add a post

1. Put the image in `assets/`.
2. Add the new item to the appropriate stack's `items` array in `library.json`. Put the newest item first when it should become the cover.
3. Use `slide: true` on follow-up images that belong to the preceding post. Slides remain part of the viewer sequence but do not increase the entry count on the stack badge.
4. Include `body` and `links` only when the entry needs them. Link objects use `t` for the label and `href` for the URL.

An item may use these fields:

```json
{
  "src": "assets/example.jpg",
  "title": "Example title",
  "cap": "Short caption.",
  "body": ["First paragraph.", "Second paragraph."],
  "links": [{ "t": "Source label", "href": "https://example.com" }],
  "slide": false,
  "pos": "50% 40%",
  "retired": false
}
```

## Rotate the homepage

Set `front: true` on exactly two stacks and `front: false` on the rest. The homepage renders the two active stacks in the same order they appear in `library.json`. No HTML or JavaScript edit is needed.

## Retire or remove an item

- Set `retired: true` to keep an item in the manifest archive while hiding it from both pages.
- Retire every follow-up slide with its parent post.
- Delete the item object to remove it permanently.

The cover is always the first item in the stack that is not retired.

## Check an edit locally

Because the pages fetch JSON, open them through a local web server rather than directly from disk:

```powershell
python -m http.server 8000
```

Then check `http://localhost:8000/` and `http://localhost:8000/library.html` at desktop and mobile widths. Confirm that retired items are absent, stack counts exclude slides, and the previous/next controls reach every active item.
