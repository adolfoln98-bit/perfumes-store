import json
import smtplib
import ssl
import sys
from email.message import EmailMessage


def main():
    credenciales = json.load(sys.stdin)

    correo = credenciales["correo"]
    password = credenciales["password"]
    error_backup = credenciales["error"]
    fecha_backup = credenciales["fecha"]

    mensaje = EmailMessage()

    mensaje["From"] = correo
    mensaje["To"] = correo
    mensaje["Subject"] = "[Perfumes Store] ERROR - Backup PostgreSQL"

    mensaje.set_content(
        f"""El proceso de backup automatico ha fallado.

        DETALLES DEL INCIDENTE

        Proyecto: Perfumes Store
        Servicio: Backup PostgreSQL
        Fecha: {fecha_backup}
        Estado: ERROR

        Descripcion del error:
        {error_backup}

        ACCION RECOMENDADA

        Revisar el archivo backups/logs/backup.log
        y comprobar el estado del contenedor PostgreSQL.

        ---
        Notificacion automatica de Perfumes Store.
        """
    )

    contexto_ssl = ssl.create_default_context()

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as servidor:
        servidor.ehlo()
        servidor.starttls(context=contexto_ssl)
        servidor.ehlo()

        servidor.user = correo
        servidor.password = password

        servidor.auth("LOGIN", servidor.auth_login, initial_response_ok=False)

        servidor.send_message(mensaje)

        print("Correo enviado correctamente")


if __name__ == "__main__":
    main()