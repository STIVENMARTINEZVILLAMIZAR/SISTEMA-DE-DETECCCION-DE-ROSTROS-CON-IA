import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

# Configuración desde variables de entorno o valores por defecto
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "tu_correo@gmail.com")
SMTP_PASS = os.getenv("SMTP_PASS", "clave_app")

def send_alert_email(to_email: str, subject: str, body: str, snapshot_bytes: bytes | None = None):
    if not to_email:
        print("[EMAIL] No se envió porque no hay destinatario configurado")
        return

    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    if snapshot_bytes:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(snapshot_bytes)
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment; filename=snapshot.jpg")
        msg.attach(part)

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls(context=ssl.create_default_context())
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, to_email, msg.as_string())
        server.quit()
        print(f"[EMAIL] Alerta enviada a {to_email}")
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
