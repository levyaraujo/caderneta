from flask_restful import Resource, request
from twilio.twiml.messaging_response import MessagingResponse

from src.dominio.bot.services import responder_usuario


class TwilioWebhook(Resource):
    def post(self):
        dados = request.form
        twiml = MessagingResponse()
        usuario = dados["From"]
        resposta = responder_usuario(dados["Body"], usuario)
        twiml.message(resposta.body)
        return str(twiml)

    def get(self):
        return {"message": "Hello, World!"}
