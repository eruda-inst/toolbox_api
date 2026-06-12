from brevo import AsyncBrevo
from pydantic import EmailStr
from brevo.core.api_error import ApiError
from app.api.v1 import cores
from brevo.transactional_emails import (
    SendTransacEmailRequestSender,
    SendTransacEmailRequestToItem,
)


class EmailSender:
    subject = "Verificação de código OTP"
    client = AsyncBrevo(
        api_key=cores.settings.brevo_api_key.get_secret_value(), timeout=15.0
    )
    sender = SendTransacEmailRequestSender(
        name=cores.settings.brevo_from_name, email=cores.settings.brevo_from_email
    )
    content = """
    <html>
        <body>
            <p>Seu código de verificação é: <strong>{}</strong>.</p>
            <p>Esse código expira em <strong>10 minutos</strong>.</p>
        </body>
    </html>
    """

    @classmethod
    async def send(cls, otp: str, to_name: str, to_email: EmailStr) -> None:
        full_content = cls.content.format(otp)
        to = SendTransacEmailRequestToItem(email=to_email, name=to_name)
        try:
            await cls.client.transactional_emails.send_transac_email(
                subject=cls.subject,
                html_content=full_content,
                sender=cls.sender,
                to=[to],
                request_options={"max_retries": 3},
            )
        except ApiError as e:
            raise e
