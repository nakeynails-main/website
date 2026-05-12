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
<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<meta name="color-scheme" content="light"/>
<meta name="supported-color-schemes" content="light"/>
<title>NakeyPen Reminder</title>
<!--[if mso]><noscript><xml><o:OfficeDocumentSettings><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml></noscript><![endif]-->
</head>
<body style="margin:0;padding:0;background-color:#F9F6F1;-webkit-text-size-adjust:100%;mso-line-height-rule:exactly;">

<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
  style="background-color:#F9F6F1;margin:0;padding:0;">
  <tr>
    <td align="center" style="padding:40px 16px;">

      <table role="presentation" width="560" cellpadding="0" cellspacing="0" border="0"
        style="max-width:560px;width:100%;">

        <!-- Logo -->
        <tr>
          <td align="center" style="padding-bottom:32px;">
            <img src="{LOGO_URL}" alt="nakeyNails" width="120" height="auto"
              style="display:block;width:120px;height:auto;border:0;"/>
          </td>
        </tr>

        <!-- Card -->
        <tr>
          <td style="background-color:#ffffff;padding:40px 36px 36px 36px;border:1px solid #E8E4DE;">

            <!-- Eyebrow -->
            <p style="margin:0 0 12px 0;font-family:Arial,Helvetica,sans-serif;font-size:10px;
              letter-spacing:3px;text-transform:uppercase;color:#9E9890;">
              Daily Reminder
            </p>

            <!-- Heading -->
            <p style="margin:0 0 24px 0;font-family:Georgia,'Times New Roman',Times,serif;
              font-size:34px;font-weight:400;line-height:1.15;color:#1A1610;">
              Time for your<br/><em>NakeyPen.</em>
            </p>

            <!-- Body -->
            <p style="margin:0 0 20px 0;font-family:Arial,Helvetica,sans-serif;
              font-size:16px;color:#5C5650;line-height:1.7;">
              {greeting} your nails are waiting. One click, one brush, 10 seconds.
              That is all it takes to keep your recovery on track.
            </p>

            <p style="margin:0;font-family:Georgia,'Times New Roman',Times,serif;
              font-size:15px;color:#5C5650;line-height:1.7;font-style:italic;">
              Consistency is what makes NakeyPen work. You have got this.
            </p>

          </td>
        </tr>

        <!-- Buy more bar -->
        <tr>
          <td style="padding-top:3px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td style="background-color:#1A1610;padding:20px 36px;">
                  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
                    <tr>
                      <td style="vertical-align:middle;">
                        <p style="margin:0 0 2px 0;font-family:Arial,Helvetica,sans-serif;
                          font-size:10px;letter-spacing:2px;text-transform:uppercase;color:#9E9890;">
                          Running low?
                        </p>
                        <p style="margin:0;font-family:Georgia,'Times New Roman',Times,serif;
                          font-size:18px;font-weight:400;color:#F9F6F1;">
                          Buy more NakeyPen
                        </p>
                      </td>
                      <td align="right" style="vertical-align:middle;padding-left:16px;white-space:nowrap;">
                        <a href="{AMAZON_URL}" target="_blank"
                          style="display:inline-block;background-color:#F9F6F1;color:#1A1610;
                          font-family:Arial,Helvetica,sans-serif;font-size:10px;font-weight:700;
                          letter-spacing:2px;text-transform:uppercase;text-decoration:none;
                          padding:12px 22px;">
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

        <!-- Footer -->
        <tr>
          <td align="center" style="padding:28px 0 8px 0;">
            <p style="margin:0 0 8px 0;font-family:Arial,Helvetica,sans-serif;
              font-size:11px;color:#9E9890;line-height:2;">
              <a href="mailto:help@nakeynails.com"
                style="color:#9E9890;text-decoration:underline;">Contact Us</a>
              &nbsp;·&nbsp;
              <a href="{REMIND_URL}"
                style="color:#9E9890;text-decoration:underline;">Edit Reminder Times</a>
              &nbsp;·&nbsp;
              <a href="mailto:help@nakeynails.com?subject=Unsubscribe&body=Please unsubscribe me."
                style="color:#9E9890;text-decoration:underline;">Unsubscribe</a>
            </p>
            <p style="margin:0;font-family:Arial,Helvetica,sans-serif;
              font-size:10px;color:#B0AA9E;line-height:1.6;">
              nakeyNails &middot; Made in USA &middot; help@nakeynails.com
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
    msg["Subject"] = "Your NakeyPen reminder"
    msg["From"]    = f"nakeyNails <help@nakeynails.com>"
    msg["To"]      = to_email
    msg["List-Unsubscribe"] = f"<mailto:help@nakeynails.com?subject=Unsubscribe>"
    msg["X-Priority"] = "3"
    msg["Precedence"] = "bulk"

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
