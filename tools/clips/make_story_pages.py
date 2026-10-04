#!/usr/bin/env python3
"""Render the Rental Manager pages for the RM story clip: one AC replacement.

Sample property only. The tracker's own engine renders every page from a temp
copy of the sample fixture, so nothing comes from the owner's folder. The
story: the tenant writes in, the vendor is asked for a quote, the quote is
approved, the invoice is checked against it, the order closes, and the new
condenser goes on the Assets tab. Each state is its own page under
.design-loop/clips/fixture/story/ for capture.js.

    python tools/clips/make_story_pages.py
"""
from __future__ import annotations

import functools
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

TRACKER = Path(r"C:/Users/jmarg/work/olimazi-tracker")
OUT = Path(__file__).resolve().parents[2] / ".design-loop" / "clips" / "fixture" / "story"

TITLE = "Replace AC condenser"
VENDOR = "Sample HVAC Co"
QUOTE = {"id": "Q-AC-1", "vendor": VENDOR, "amount": 4200.0, "requested": "2026-09-23",
         "received": "2026-09-25", "doc": "source-docs/sample-hvac-quote.pdf"}
INVOICE = {"amount": 4350.0, "received": "2026-10-02", "doc": "source-docs/sample-hvac-invoice.jpg"}

# (page, today for the follow-up timer, order fields)
STATES = [
    ("wo-ask", "2026-09-22", {"status": "Open"}),
    ("wo-quote", "2026-09-25", {"status": "Open", "quotes": [dict(QUOTE, state="received")]}),
    ("wo-approved", "2026-09-29", {"status": "Open", "quotes": [dict(QUOTE, state="approved", approved="2026-09-26")]}),
    ("wo-invoice", "2026-10-02", {"status": "Open", "quotes": [dict(QUOTE, state="approved", approved="2026-09-26")],
                                  "invoice": INVOICE}),
    ("wo-closed", "2026-10-03", {"status": "Closed", "closed": "2026-10-03", "closed_by_owner": "2026-10-03",
                                 "quotes": [dict(QUOTE, state="approved", approved="2026-09-26")], "invoice": INVOICE}),
]

TENANT_REPLY = dict(
    to="sam.tenant@example.com", subject="Re: AC unit stopped working", thread_subject="AC unit stopped working",
    last_speaker="Sam Tenant (tenant), 2026-09-22", in_reply_to="<ac-unit-0922@example.com>", created="2026-09-22T18:40:00",
    body="Hi Sam,\n\nThanks for the photos. The outdoor unit is 19 years old, so I am asking Sample HVAC Co "
         "to quote a replacement. I will send you a time as soon as I have one.\n\nThanks")


def strip_private(html: str) -> str:
    # The intake ledger reads the owner's own mail folder; it never belongs on a sample page.
    return re.sub(r"<tr data-note=\"intake:.*?</tr>", "", html, flags=re.S)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    pages = {}
    with tempfile.TemporaryDirectory(prefix="olimazi-story-") as tmp:
        work = Path(tmp)
        for folder in ("engine", "config", "fixtures"):
            shutil.copytree(TRACKER / folder, work / folder,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "mail-queue"))
        prop = work / "fixtures" / "sample-property"
        ini = work / "tracker.ini"
        ini.write_text(f"[tracker]\nproperty = {prop}\n\n[mail]\nsend_policy = approve-queue\n", encoding="utf-8")
        os.chdir(work)
        sys.path.insert(0, str(work / "engine"))
        import work_orders as wo
        import management_page
        management_page.intake_section = lambda: ""
        follow_up = wo.follow_up

        mj = prop / "management.json"
        base = json.loads(mj.read_text(encoding="utf-8"))
        issue = next(i for i in base["issues"] if i.get("id") == "ISSUE-001")
        issue["reported"] = "2026-09-22"
        issue.pop("expense_link", None)  # an improvement is an asset, not a line 14 repair
        issue["linked_emails"] = [{"subject": "AC unit stopped working", "date": "2026-09-22", "folder": "Tenant"},
                                  {"subject": "Re: AC unit stopped working", "date": "2026-09-22", "folder": "Sent"},
                                  {"subject": "Quote request: " + TITLE, "date": "2026-09-23", "folder": "Vendors"}]
        issue["notes"] = [{"date": "2026-09-22", "text": "Tenant reports the outdoor unit will not start."},
                          {"date": "2026-09-23", "text": "Unit is 19 years old. Replacement quoted."}]
        base["work_orders"] = [o for o in base["work_orders"] if "AC condenser" not in o.get("title", "")]

        for name, today, fields in STATES:
            data = json.loads(json.dumps(base))
            order = {"title": TITLE, "vendor": VENDOR, "vendor_email": "dispatch@example.com",
                     "opened": "2026-09-22", "kind": "improvement",
                     "notes": "Outdoor unit failed; replace the condenser.", "docs": [], **fields}
            data["work_orders"].insert(0, order)
            mj.write_text(json.dumps(data, indent=1), encoding="utf-8")
            wo.follow_up = functools.partial(follow_up, today=today)
            pages[name] = strip_private(management_page.render(prop).read_text(encoding="utf-8"))

        # Mail: the reply to the tenant and the quote request to the vendor, both waiting on Send.
        import mail_queue
        mail_queue.CONFIG_PATH = str(ini)
        subject, body = wo.quote_request_draft({"title": TITLE, "vendor": VENDOR},
                                               property_name="12 Sample Street", owner="Pat Owner")
        drafts = [TENANT_REPLY, dict(to="dispatch@example.com", subject=subject, body=body, thread_subject=subject,
                                     last_speaker="", in_reply_to="", created="2026-09-23T08:05:00")]
        for n, d in enumerate(drafts):
            mail_queue._write({"id": d["created"].replace("-", "").replace(":", "") + f"-s{n:05d}",
                               "to": d["to"], "subject": d["subject"], "body": d["body"],
                               "in_reply_to": d["in_reply_to"], "thread_subject": d["thread_subject"],
                               "last_speaker": d["last_speaker"], "flags": mail_queue.flags_for(d["subject"], d["body"]),
                               "status": "queued", "created": d["created"], "sent_at": "",
                               "sent_message_id": "", "error": ""}, prop)
        import dashboard_server
        dashboard_server.RECONCILE_ROOT = str(prop)
        pages["mail"] = dashboard_server.render_mail_page()

        # Assets: the closed improvement is offered; then the same page after Add to Assets.
        import assets_page
        tracker = str(prop / "sample-tracker.xlsx")
        css = dashboard_server.MAIL_CSS
        pages["assets"] = assets_page.render(str(prop), tracker, css)
        pages["assets-suggest"] = json.dumps(assets_page.suggest_json(TITLE))
        code, result, _ = assets_page._add({"asset": TITLE, "in_service": "2026-10-03", "cost": "4350.00",
                                            "class_key": "27.5", "life": "27.5",
                                            "source": f"{VENDOR} work order"}, str(prop), tracker, lambda *a: None)
        if code != 200:
            print("asset add failed", result)
            return 1
        pages["assets-added"] = assets_page.render(str(prop), tracker, css)
        os.chdir(TRACKER)

    real = (TRACKER / "tracker.ini").read_text(encoding="utf-8")
    leaks = [line.split("=", 1)[1].strip() for line in real.splitlines() if line.strip().startswith("property")]
    for name, html in pages.items():
        for leak in leaks:
            if leak and leak in html:
                print("real property path leaked in", name, "; nothing written")
                return 1
    for name, html in pages.items():
        (OUT / (name + (".json" if name.endswith("suggest") else ".html"))).write_text(html, encoding="utf-8")
    print("wrote", ", ".join(pages), "to", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
