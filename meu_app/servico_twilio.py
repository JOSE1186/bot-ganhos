from twilio.rest import Client
import os

class TwilioService:
    def __init__(self):
        self.sid = os.getenv("TWILIO_SID")
        self.token = os.getenv("TWILIO_TOKEN")
        self.numero_envio = os.getenv("TWILIO_NUMBER")
        self.client = Client(self.sid, self.token)

    def enviar_resposta(self, numero, liquido):
        mensagem = f"Seu ganho líquido foi R$ {liquido:.2f}"
        self.client.messages.create(
            to=numero,
            from_=self.numero_envio,
            body=mensagem
        )
