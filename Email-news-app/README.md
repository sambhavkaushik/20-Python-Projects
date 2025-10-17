# 📧 Email News App

A small Python app that fetches top stories from RSS feeds (BBC, Reuters, Hacker News) and emails them as a daily digest.

## 🔧 Setup
```bash
pip install feedparser python-dateutil
```
Set environment variables:
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=your_email@gmail.com
TO_EMAIL=receiver@example.com
```

## ▶️ Usage
Preview digest (no email):
```bash
python email_news_app.py --preview
```
Send digest email:
```bash
python email_news_app.py --since 24 --max 15 --subject "My Daily News"
```

## 🕒 Automation
- **Cron (Linux/macOS):**
  ```bash
  0 8 * * * python /path/email_news_app.py --since 24 --max 20
  ```
- **Windows Task Scheduler:** Run daily at chosen time.

## 🧠 Default Feeds
- BBC World
- Reuters World
- Hacker News

## 💡 Author
**Sammy** — Built with ❤️ using Python 3