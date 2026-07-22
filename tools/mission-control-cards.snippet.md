# Mission Control site-copy cards — packet 12-C

The verifier should move each staged Markdown file to the matching vault path,
then add these cards without changing the existing Deploy flow or live-verify gate.
Commands assume Mission Control starts in `C:\Users\jmarg\work\olimazi-online`.

## Site — Hero spec

- Preview: `python tools/render_section.py --content "C:\Users\jmarg\OneDrive\Documents\Claude OS\projects\olimazi-brand\site-copy\hero-spec.md" --mode preview --target index.html`
- Build: `python tools/render_section.py --content "C:\Users\jmarg\OneDrive\Documents\Claude OS\projects\olimazi-brand\site-copy\hero-spec.md" --mode build --target index.html`
- Deploy: unchanged existing flow; retain the existing live-verify gate.

## Site — Main work

- Preview: `python tools/render_section.py --content "C:\Users\jmarg\OneDrive\Documents\Claude OS\projects\olimazi-brand\site-copy\main-work.md" --mode preview --target index.html`
- Build: `python tools/render_section.py --content "C:\Users\jmarg\OneDrive\Documents\Claude OS\projects\olimazi-brand\site-copy\main-work.md" --mode build --target index.html`
- Deploy: unchanged existing flow; retain the existing live-verify gate.

## Site — Method

- Preview: `python tools/render_section.py --content "C:\Users\jmarg\OneDrive\Documents\Claude OS\projects\olimazi-brand\site-copy\method.md" --mode preview --target index.html`
- Build: `python tools/render_section.py --content "C:\Users\jmarg\OneDrive\Documents\Claude OS\projects\olimazi-brand\site-copy\method.md" --mode build --target index.html`
- Deploy: unchanged existing flow; retain the existing live-verify gate.

## Site — Mind

- Preview: `python tools/render_section.py --content "C:\Users\jmarg\OneDrive\Documents\Claude OS\projects\olimazi-brand\site-copy\mind.md" --mode preview --target index.html`
- Build: `python tools/render_section.py --content "C:\Users\jmarg\OneDrive\Documents\Claude OS\projects\olimazi-brand\site-copy\mind.md" --mode build --target index.html`
- Deploy: unchanged existing flow; retain the existing live-verify gate.

## Site — Contact

- Preview: `python tools/render_section.py --content "C:\Users\jmarg\OneDrive\Documents\Claude OS\projects\olimazi-brand\site-copy\contact.md" --mode preview --target index.html`
- Build: `python tools/render_section.py --content "C:\Users\jmarg\OneDrive\Documents\Claude OS\projects\olimazi-brand\site-copy\contact.md" --mode build --target index.html`
- Deploy: unchanged existing flow; retain the existing live-verify gate.

## Site — Dialogs

- Preview: `python tools/render_section.py --content "C:\Users\jmarg\OneDrive\Documents\Claude OS\projects\olimazi-brand\site-copy\dialogs.md" --mode preview --target index.html`
- Build: `python tools/render_section.py --content "C:\Users\jmarg\OneDrive\Documents\Claude OS\projects\olimazi-brand\site-copy\dialogs.md" --mode build --target index.html`
- Deploy: unchanged existing flow; retain the existing live-verify gate.
