from email.message import EmailMessage
import os
import smtplib


def send_mail(to: str, subject: str, body: str) -> None:
    msg = EmailMessage()
    msg["From"] = "noreply@camagru.local"
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    host = os.environ.get("SMTP_HOST", "mailpit")
    port = int(os.environ.get("SMTP_PORT", "1025"))
    with smtplib.SMTP(host, port) as smtp:
        smtp.send_message(msg)