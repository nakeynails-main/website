#!/usr/bin/env python3
"""
send_reminders.py
Runs every 15 minutes via GitHub Actions.
Reads Google Sheets, sends NakeyPen reminder emails via Gmail SMTP.
"""

import os, json, smtplib, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from zoneinfo import ZoneInfo
import gspread
from google.oauth2.service_account import Credentials

# ── Config ───────────────────────────────────────────────────────
GMAIL_USER     = os.environ["GMAIL_USER"]
GMAIL_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
SHEET_ID       = os.environ["SHEET_ID"]
SHEET_CREDS    = json.loads(os.environ["GOOGLE_SHEETS_CREDS"])

AMAZON_URL  = "https://www.amazon.com/dp/B0G14TM258"
SITE_URL    = "https://nakeynails.com"
LOGO_URL    = "https://nakeynails.com/logo.png"
REMIND_URL  = f"{SITE_URL}/remind-me.html"

# ── Connect to Google Sheets ─────────────────────────────────────
scope  = ["https://spreadsheets.google.com/feeds",
          "https://www.googleapis.com/auth/drive"]
creds  = Credentials.from_service_account_info(SHEET_CREDS, scopes=scope)
client = gspread.authorize(creds)
sheet  = client.open_by_key(SHEET_ID).sheet1
rows   = sheet.get_all_records()

now_utc = datetime.datetime.now(datetime.timezone.utc)
print(f"Running at UTC: {now_utc.strftime('%Y-%m-%d %H:%M')}")
sent = 0

# ── Build HTML email ─────────────────────────────────────────────
def build_email(name):
    greeting = f"Hey {name.split()[0].title()}," if name.strip() else "Hey there,"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>NakeyPen Reminder</title>
</head>
<body style="margin:0;padding:0;background:#F9F6F1;font-family:'Helvetica Neue',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#F9F6F1;padding:40px 20px;">
  <tr>
    <td align="center">
      <table width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;">

        <!-- Logo -->
        <tr>
          <td align="center" style="padding-bottom:40px;">
            <img src="{LOGO_URL}" alt="nakeyNails" height="32" style="display:block;height:32px;width:auto;"/>
          </td>
        </tr>

        <!-- Main message -->
        <tr>
          <td style="background:#ffffff;padding:48px 40px 40px;border:1px solid rgba(26,22,16,0.08);">
            <p style="margin:0 0 8px;font-size:11px;letter-spacing:0.28em;text-transform:uppercase;color:#9E9890;">
              Daily Reminder
            </p>
            <h1 style="margin:0 0 24px;font-family:Georgia,serif;font-size:32px;font-weight:300;line-height:1.1;color:#1A1610;letter-spacing:-0.02em;">
              Time for your<br/><em>NakeyPen.</em>
            </h1>
            <p style="margin:0 0 32px;font-size:16px;color:#5C5650;line-height:1.7;font-weight:300;">
              {greeting} your nails are waiting. One click, one brush, 10 seconds.
              That is all it takes to keep your recovery on track.
            </p>
            <p style="margin:0;font-size:14px;color:#5C5650;line-height:1.7;font-weight:300;font-style:italic;">
              Consistency is what makes NakeyPen work. You have got this.
            </p>
          </td>
        </tr>

        <!-- Buy more button -->
        <tr>
          <td style="padding-top:4px;">
            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="background:#1A1610;padding:18px 40px;">
                  <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                      <td>
                        <p style="margin:0;font-size:11px;letter-spacing:0.22em;text-transform:uppercase;color:#9E9890;">
                          Running low?
                        </p>
                        <p style="margin:4px 0 0;font-family:Georgia,serif;font-size:18px;font-weight:300;color:#F9F6F1;">
                          Buy more NakeyPen
                        </p>
                      </td>
                      <td align="right">
                        <a href="{AMAZON_URL}" target="_blank"
                           style="display:inline-block;background:#F9F6F1;color:#1A1610;font-size:10px;font-weight:400;letter-spacing:0.26em;text-transform:uppercase;text-decoration:none;padding:12px 24px;">
                          Shop Now
                        </a>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- Footer links -->
        <tr>
          <td style="padding:28px 0 0;text-align:center;">
            <p style="margin:0;font-size:11px;letter-spacing:0.18em;text-transform:uppercase;color:#9E9890;line-height:2;">
              <a href="mailto:help@nakeynails.com" style="color:#9E9890;text-decoration:none;">Contact Us</a>
              &nbsp;&nbsp;·&nbsp;&nbsp;
              <a href="{REMIND_URL}" style="color:#9E9890;text-decoration:none;">Edit Reminder Times</a>
              &nbsp;&nbsp;·&nbsp;&nbsp;
              <a href="mailto:help@nakeynails.com?subject=Unsubscribe&body=Please unsubscribe me from NakeyPen reminders." style="color:#9E9890;text-decoration:none;">Unsubscribe</a>
            </p>
            <p style="margin:16px 0 0;font-size:10px;color:#9E9890;letter-spacing:0.1em;">
              nakeyNails · Made in USA · help@nakeynails.com
            </p>
          </td>
        </tr>

      </table>
    </td>
  </tr>
</table>
</body>
</html>"""

# ── Send one email ────────────────────────────────────────────────
def send_email(to_email, name):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Time to strengthen your nails with NakeyPen"
    # msg["From"]    = f"nakeyNails <{GMAIL_USER}>"
    msg["From"]    = "nakeyNails <help@nakeynails.com>"
    msg["To"]      = to_email

    # Plain text fallback
    plain = (f"Hey, time to apply your NakeyPen!\n\n"
             f"One click, one brush, 10 seconds.\n\n"
             f"Shop: {AMAZON_URL}\n"
             f"Edit reminders: {REMIND_URL}\n"
             f"Unsubscribe: mailto:help@nakeynails.com?subject=Unsubscribe")

    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(build_email(name), "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(GMAIL_USER, to_email, msg.as_string())

# ── Main loop ─────────────────────────────────────────────────────
for row in rows:
    email     = str(row.get("Email", "")).strip().lower()
    name      = str(row.get("Name",  "")).strip()
    timezone  = str(row.get("Timezone", "UTC")).strip()
    times_raw = str(row.get("Times", "[]")).strip()

    if not email or "@" not in email:
        continue

    # Parse reminder times
    try:
        times = json.loads(times_raw)
    except Exception:
        continue

    if not times:
        continue

    # Convert current UTC to user's local time
    try:
        tz = ZoneInfo(timezone)
    except Exception:
        tz = ZoneInfo("UTC")

    now_local  = now_utc.astimezone(tz)
    now_mins   = now_local.hour * 60 + now_local.minute

    # Check if any reminder time matches now (within ±7 minute window)
    should_send = False
    for t in times:
        try:
            h, m = map(int, str(t).split(":"))
            reminder_mins = h * 60 + m
            if abs(now_mins - reminder_mins) <= 7:
                should_send = True
                break
        except Exception:
            continue

    if not should_send:
        continue

    # Send it
    try:
        send_email(email, name)
        print(f"Sent to {email} ({timezone} {now_local.strftime('%H:%M')})")
        sent += 1
    except Exception as e:
        print(f"Failed {email}: {e}")

print(f"\nDone. Sent {sent} reminder(s).")
