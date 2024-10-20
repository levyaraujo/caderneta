from flask import Blueprint
from flask_restful import Api
from src.dominio.bot.resources import TwilioWebhook

api_bp = Blueprint("api", __name__)
api = Api(api_bp)


def init_app(app):
    api.add_resource(TwilioWebhook, "/twilio")
    app.register_blueprint(api_bp)
