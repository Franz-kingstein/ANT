import smtplib
from email.message import EmailMessage
import config
from utils import log_message


def send_attendance_report(rows, to_email):
    """
    Send attendance report via email. rows is a list of [date, time, name, regno, status].
    """
    try:
        # Determine recipient
        recipient = to_email if to_email else config.TO_EMAIL
        # Compose CSV body
        csv_lines = ['Date,Time,Name,Registration Number,Status']
        for r in rows:
            csv_lines.append(','.join(r))
        body = "\n".join(csv_lines)

        msg = EmailMessage()
        msg['Subject'] = f"Attendance Report -- {config.SHEET_NAME}"
        msg['From'] = config.SMTP_USER
        msg['To'] = recipient
        msg.set_content(body)

        # Send via SMTP
        with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(config.SMTP_USER, config.SMTP_PASS)
            smtp.send_message(msg)
        log_message(f"Attendance report emailed successfully to {recipient}")
    except Exception as e:
        log_message(f"Failed to send attendance report: {e}", "ERROR")
