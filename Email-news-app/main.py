"""
email_news_app.py

A simple, production-ready-ish Python script that fetches top stories from a set of RSS feeds
(BBC, Reuters, Hacker News by default), builds a clean HTML+plain-text email digest,
then sends it via SMTP (e.g., Gmail with an app password).

Quick start:
1) pip install -r requirements.txt  (feedparser, python-dateutil)
2) Set environment variables (or make a .env and load them yourself):
   - SMTP_HOST (e.g., "smtp.gmail.com")
   - SMTP_PORT (e.g., 465 for SSL, or 587 for STARTTLS)
   - SMTP_USERNAME (full email address)
   - SMTP_PASSWORD (app password)
   - FROM_EMAIL (same as SMTP_USERNAME typically)
   - TO_EMAIL (comma-separated for multiple recipients)
3) Run: python email_news_app.py --max 15 --since 24

Notes:
- Use Gmail App Passwords (recommended) if using Gmail.
- You can change FEEDS below to whatever you like.
- Schedule with cron/Task Scheduler for daily digests.
"""

from __future__ import annotations

import os
import ssl
import sys
import smtplib
import html
import time
import argparse
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Tuple

try:
    import feedparser  # type: ignore
except Exception as e:
    print("Missing dependency 'feedparser'. Install with: pip install feedparser python-dateutil", file=sys.stderr)
    raise

try:
    from dateutil import parser as dateparser  # type: ignore
except Exception:
    print("Missing dependency 'python-dateutil'. Install with: pip install python-dateutil", file=sys.stderr)
    raise

# ---------------------- Config ----------------------
DEFAULT_FEEDS = [
    ("BBC World", "http://feeds.bbci.co.uk/news/world/rss.xml"),
    ("Reuters World", "http://feeds.reuters.com/reuters/worldNews"),
    ("Hacker News", "https://hnrss.org/frontpage"),
]

# Set sane logging defaults
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("email_news_app")

# ---------------------- Helpers ----------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Fetch RSS items and send an email digest.")
    p.add_argument("--feeds", nargs="*", help="Optional list of RSS URLs (overrides defaults)")
    p.add_argument("--max", type=int, default=20, help="Max total items across all feeds")
    p.add_argument("--per_feed", type=int, default=10, help="Max items per feed")
    p.add_argument("--since", type=int, default=24, help="Only include items published within N hours")
    p.add_argument("--subject", default="Your News Digest", help="Email subject")
    p.add_argument("--preview", action="store_true", help="Print digest to stdout instead of sending")
    p.add_argument("--no_html", action="store_true", help="Send plain-text only (no HTML part)")
    return p.parse_args()


def load_env() -> Dict[str, str]:
    """Load SMTP/Email settings from environment variables."""
    env = {
        "SMTP_HOST": os.getenv("SMTP_HOST", ""),
        "SMTP_PORT": os.getenv("SMTP_PORT", ""),
        "SMTP_USERNAME": os.getenv("SMTP_USERNAME", ""),
        "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD", ""),
        "FROM_EMAIL": os.getenv("FROM_EMAIL", ""),
        "TO_EMAIL": os.getenv("TO_EMAIL", ""),
    }
    missing = [k for k, v in env.items() if not v]
    if missing:
        logger.warning("Missing environment variables: %s", ", ".join(missing))
    return env


def fetch_feed(title: str, url: str) -> Tuple[str, List[Dict[str, Any]]]:
    """Fetch and parse a single RSS/Atom feed. Returns (title, entries)."""
    logger.info("Fetching feed: %s", url)
    fp = feedparser.parse(url)
    feed_title = title or fp.feed.get("title", url)
    items = []
    for e in fp.entries:
        published = None
        # Try multiple date fields
        for key in ("published", "updated", "created"):
            if key in e:
                try:
                    published = dateparser.parse(str(e[key]))
                    break
                except Exception:
                    continue
        link = e.get("link") or e.get("id") or ""
        items.append({
            "source": feed_title,
            "title": e.get("title", "(No title)"),
            "summary": e.get("summary", ""),
            "link": link,
            "published": published,
        })
    return feed_title, items


def harvest_all(feeds: List[Tuple[str, str]], per_feed: int, since_hours: int, max_total: int) -> List[Dict[str, Any]]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=since_hours)
    all_items: List[Dict[str, Any]] = []
    seen_links = set()

    for title, url in feeds:
        feed_title, items = fetch_feed(title, url)
        # Sort by published desc (fallback to now for None)
        items.sort(key=lambda x: x["published"] or datetime.now(timezone.utc), reverse=True)
        count = 0
        for it in items:
            if count >= per_feed:
                break
            if it["published"] and it["published"].tzinfo is None:
                # make naïve datetimes timezone-aware as UTC
                it["published"] = it["published"].replace(tzinfo=timezone.utc)
            if it["published"] and it["published"] < cutoff:
                continue
            link = it.get("link", "")
            if link in seen_links:
                continue
            seen_links.add(link)
            all_items.append(it)
            count += 1
            if len(all_items) >= max_total:
                break
        if len(all_items) >= max_total:
            break

    # Final global sort
    all_items.sort(key=lambda x: x["published"] or datetime.now(timezone.utc), reverse=True)
    return all_items


def render_plain(items: List[Dict[str, Any]]) -> str:
    lines = []
    for i, it in enumerate(items, 1):
        ts = it["published"].astimezone().strftime("%Y-%m-%d %H:%M") if it.get("published") else ""
        lines.append(f"{i}. {it['title']}\n   {it['source']} | {ts}\n   {it['link']}\n")
    if not lines:
        lines = ["No new items found for the selected time window."]
    return "\n".join(lines)


def render_html(items: List[Dict[str, Any]]) -> str:
    def esc(s: str) -> str:
        return html.escape(s or "")

    parts = [
        """
        <html>
          <body style="font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; line-height:1.5;">
            <h2 style="margin:0 0 12px;">Your News Digest</h2>
            <p style="color:#555; margin:0 0 16px;">Top updates from your selected feeds.</p>
            <ol style="padding-left:20px;">
        """
    ]
    if not items:
        parts.append("<li>No new items found for the selected time window.</li>")
    for it in items:
        ts = it["published"].astimezone().strftime("%Y-%m-%d %H:%M") if it.get("published") else ""
        parts.append(
            f"""
            <li style=\"margin-bottom:12px;\">
              <div style=\"font-weight:600;\"><a href=\"{esc(it.get('link',''))}\" target=\"_blank\" rel=\"noopener noreferrer\">{esc(it['title'])}</a></div>
              <div style=\"color:#666; font-size:13px;\">{esc(it['source'])} • {esc(ts)}</div>
            </li>
            """
        )
    parts.append("""
            </ol>
            <hr style="border:none; border-top:1px solid #eee; margin:16px 0;"/>
            <div style="color:#777; font-size:12px;">You received this digest because you (or a script) ran email_news_app.py.</div>
          </body>
        </html>
    """)
    return "".join(parts)


def build_message(subject: str, from_email: str, to_emails: List[str], plain: str, html_body: str | None) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = ", ".join(to_emails)

    part1 = MIMEText(plain, "plain", "utf-8")
    msg.attach(part1)

    if html_body:
        part2 = MIMEText(html_body, "html", "utf-8")
        msg.attach(part2)
    return msg


def send_email(env: Dict[str, str], msg: MIMEMultipart) -> None:
    host = env.get("SMTP_HOST")
    port_s = env.get("SMTP_PORT")
    user = env.get("SMTP_USERNAME")
    pwd = env.get("SMTP_PASSWORD")

    if not (host and port_s and user and pwd):
        raise RuntimeError("SMTP_HOST/SMTP_PORT/SMTP_USERNAME/SMTP_PASSWORD must be set.")

    port = int(port_s)

    # SSL (implicit) if port is 465, otherwise STARTTLS
    if port == 465:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(host, port, context=context) as server:
            server.login(user, pwd)
            server.send_message(msg)
    else:
        with smtplib.SMTP(host, port) as server:
            server.ehlo()
            if port == 587:
                server.starttls(context=ssl.create_default_context())
                server.ehlo()
            server.login(user, pwd)
            server.send_message(msg)


# ---------------------- Main ----------------------

def main():
    args = parse_args()
    env = load_env()

    # Choose feeds: either user-provided URLs or defaults with names
    if args.feeds:
        feeds = [(f"Feed {i+1}", u) for i, u in enumerate(args.feeds)]
    else:
        feeds = DEFAULT_FEEDS

    items = harvest_all(
        feeds=feeds,
        per_feed=args.per_feed,
        since_hours=args.since,
        max_total=args.max,
    )

    plain = render_plain(items)
    html_body = None if args.no_html else render_html(items)

    to_emails = [e.strip() for e in env.get("TO_EMAIL", "").split(",") if e.strip()]

    if args.preview:
        print("\n===== PLAIN TEXT DIGEST =====\n")
        print(plain)
        if html_body:
            print("\n===== HTML DIGEST (source) =====\n")
            print(html_body)
        return

    if not to_emails:
        raise RuntimeError("TO_EMAIL is empty. Provide at least one recipient.")

    from_email = env.get("FROM_EMAIL") or env.get("SMTP_USERNAME") or ""
    if not from_email:
        raise RuntimeError("FROM_EMAIL or SMTP_USERNAME must be set.")

    msg = build_message(
        subject=args.subject,
        from_email=from_email,
        to_emails=to_emails,
        plain=plain,
        html_body=html_body,
    )

    send_email(env, msg)
    logger.info("Digest sent to: %s", ", ".join(to_emails))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logger.exception("Failed to send digest: %s", exc)
        sys.exit(1)
