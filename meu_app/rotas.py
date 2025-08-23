from flask import Blueprint, request, jsonify
from meu_app.servico_twilio import TwilioService
from meu_app.servico_supabase import SupabaseService
from meu_app.servico_calculos import CalculosService

bp = Blueprint("rotas", __name__)
twilio_service = TwilioService()
supabase_service = SupabaseService()
calculos_service = CalculosService()

@bp.route("/webhook", methods=["POST"])
def webhook():
    data = request.form
    mensagem = data.get("Body")
    numero = data.get("From")

    ganhos, combustivel = calculos_service.extrair_dados(mensagem)
    liquido = calculos_service.calcular_liquido(ganhos, combustivel)

    supabase_service.salvar_dados(numero, ganhos, combustivel, liquido)
    twilio_service.enviar_resposta(numero, liquido)

    return jsonify({"status": "ok"})
