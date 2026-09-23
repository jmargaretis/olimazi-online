#!/usr/bin/env python3
"""Render the Rental Manager mail and phone pages for the sample property.

The live /mail and /capture pages read the owner's real property folder and
network, so they are never shot. This builds the same pages from the
tracker's own engine in a temp tree that only knows the sample fixture:
sample drafts in the mail queue, and a sample address and code on the phone
page, with the phone's own page shown beside it. Output goes to
.design-loop/clips/fixture/ for capture.js.

    python tools/clips/make_fixture_pages.py
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path

TRACKER = Path(r"C:/Users/jmarg/work/olimazi-tracker")
FIXDIR = Path(__file__).resolve().parents[2] / ".design-loop" / "clips" / "fixture"
OUT = FIXDIR / "SchE_Mail.html"
PHONE_OUT = FIXDIR / "SchE_Phone.html"
PHONE_STATUS = {"running": True, "address": "http://192.168.1.20:8743", "code": "482913",
                "expires_at": None, "count": 2}
PHONE_RESULTS = [("ok", "IMG_4103.jpg — saved as PHONE__IMG_4103.jpg"),
                 ("dup", "IMG_4102.jpg — already have this one"),
                 ("ok", "IMG_4102.jpg — saved as PHONE__IMG_4102.jpg")]


def phone_frame(page: str) -> str:
    """The phone's own page, filled in, inside a plain device outline."""
    from html import escape
    page = page[:page.index("<script>")] + "</body></html>"
    page = page.replace("maxlength=6>", "maxlength=6 value=482913>")
    items = "".join(f"<li class={c}>{escape(t)}</li>" for c, t in PHONE_RESULTS)
    page = page.replace("<ul id=results></ul>", f"<ul id=results>{items}</ul>")
    return ("<div id=phone style='position:fixed;right:64px;top:118px;width:360px;height:760px;"
            "border:12px solid #16202A;border-radius:44px;overflow:hidden;background:#D6DEE3;"
            "box-shadow:0 18px 40px rgba(22,32,42,.25)'>"
            f"<iframe srcdoc=\"{escape(page, quote=True)}\" style='border:0;width:100%;height:100%'></iframe></div>")

DRAFTS = [
    dict(to="sam.tenant@example.com", subject="Re: AC unit stopped working",
         thread_subject="AC unit stopped working", last_speaker="Sam Tenant (tenant), 2026-07-18",
         in_reply_to="<ac-unit-0718@example.com>", created="2026-07-18T19:44:03",
         body="Hi Sam,\n\nThanks for the photos. Sample HVAC Co can come Thursday between 9 and 12 "
              "to replace the condenser fan motor. The $480 part is paid by the owner.\n\n"
              "If that window does not work, reply here and I will move it.\n\nThanks"),
    dict(to="dispatch@example.com", subject="Thursday visit: condenser fan motor",
         thread_subject="Diagnostic visit, AC outdoor unit", last_speaker="Sample HVAC Co (vendor), 2026-07-18",
         in_reply_to="", created="2026-07-18T19:42:10",
         body="Hi,\n\nPlease go ahead with the fan motor replacement at the quoted $480. "
              "The tenant confirmed Thursday 9 to 12 works.\n\nSend the invoice when the job closes."),
]
SENT = dict(to="sam.tenant@example.com", subject="Re: AC unit stopped working",
            created="2026-07-18T08:10:00", sent_at="2026-07-18T08:12:31",
            body="Got it. A technician is being booked for a diagnostic visit.")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="olimazi-mail-") as tmp:
        work = Path(tmp)
        for folder in ("engine", "config", "fixtures"):
            shutil.copytree(TRACKER / folder, work / folder,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "mail-queue"))
        prop = work / "fixtures" / "sample-property"
        ini = work / "tracker.ini"
        ini.write_text(f"[tracker]\nproperty = {prop}\n\n[mail]\nsend_policy = approve-queue\n", encoding="utf-8")
        os.chdir(work)
        sys.path.insert(0, str(work / "engine"))
        import mail_queue
        mail_queue.CONFIG_PATH = str(ini)
        entries = [dict(d, status="queued", sent_at="") for d in DRAFTS] + [
            dict(SENT, in_reply_to="", thread_subject=SENT["subject"], last_speaker="", status="sent")]
        for n, d in enumerate(entries):
            e = {"id": d["created"].replace("-", "").replace(":", "") + f"-s{n:05d}",
                 "to": d["to"], "subject": d["subject"], "body": d["body"],
                 "in_reply_to": d["in_reply_to"], "thread_subject": d["thread_subject"],
                 "last_speaker": d["last_speaker"], "flags": mail_queue.flags_for(d["subject"], d["body"]),
                 "status": d["status"], "created": d["created"], "sent_at": d["sent_at"],
                 "sent_message_id": "", "error": ""}
            mail_queue._write(e, prop)
        import dashboard_server
        dashboard_server.RECONCILE_ROOT = str(prop)
        html = dashboard_server.render_mail_page()
        import capture
        phone_page = capture.CAPTURE_PAGE
        capture.status = lambda: dict(PHONE_STATUS)
        phone = dashboard_server.render_capture_page()
        phone = phone.replace("</body>", phone_frame(phone_page) + "</body>")
        os.chdir(TRACKER)
    real = Path(TRACKER / "tracker.ini").read_text(encoding="utf-8")
    for line in real.splitlines():
        if line.strip().startswith("property"):
            leak = line.split("=", 1)[1].strip()
            if leak and (leak in html or leak in phone):
                print("real property path leaked; not written")
                return 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    PHONE_OUT.write_text(phone, encoding="utf-8")
    print("wrote", OUT, len(html), PHONE_OUT, len(phone))
    return 0


if __name__ == "__main__":
    sys.exit(main())
