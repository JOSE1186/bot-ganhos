from flask import request, session
from twilio.twiml.messaging_response import MessagingResponse
from .servico_calculos import tentar_converter_para_float
from .servico_supabase import supabase

def registrar_rotas(app):

    @app.route("/")
def home():
    return "Bot está ativo!"

@app.route("/sms", methods=["POST"])
def responder_sms():
    msg = request.form.get("Body", "").strip()
    if "estado" not in session:
        session["estado"] = "inicio"

    if session["estado"] == "inicio":
        resposta = MessagingResponse()
        resposta.message("Olá! Digite 1 para inserir o ganho de hoje, 2 para ver saldo, 3 para sair.")
        session["estado"] = "menu"
        return str(resposta)

    elif session["estado"] == "menu":
        resposta = MessagingResponse()
        if msg == "1":
            resposta.message("Digite o valor do seu ganho bruto:")
            session["estado"] = "aguardando_ganho"
        elif msg == "2":
            dados = supabase.table("ganhos").select("bruto", "liquido").execute()
            if not dados.data:
                resposta.message("Nenhum registro encontrado.")
            else:
                total_bruto = sum(item.get("bruto", 0) for item in dados.data)
                total_liquido = sum(item.get("liquido", 0) for item in dados.data)
                resposta.message(f"🔢 Totais:\nBruto total: R$ {total_bruto:.2f}\nLíquido total: R$ {total_liquido:.2f}")
            session["estado"] = "inicio"
        elif msg == "3":
            resposta.message("Bot encerrado. Até logo!")
            session.clear()
        else:
            resposta.message("Opção inválida. Digite 1, 2 ou 3.")
        return str(resposta)

    elif session["estado"] == "aguardando_ganho":
        ganho = tentar_converter_para_float(msg)
        resposta = MessagingResponse()
        if ganho is not None:
            session["ganho"] = ganho
            resposta.message("Agora digite o valor gasto com combustível:")
            session["estado"] = "aguardando_combustivel"
        else:
            resposta.message("Por favor, envie um número válido. Ex: 100 ou 100.50")
        return str(resposta)

    elif session["estado"] == "aguardando_combustivel":
        combustivel = tentar_converter_para_float(msg)
        resposta = MessagingResponse()
        if combustivel is not None:
            ganho = session.get("ganho", 0)
            liquido = ganho - combustivel

            resultado = supabase.table("ganhos").insert({
                "bruto": ganho,
                "liquido": liquido
            }).execute()
            

            # Verificação aprimorada do resultado
            if resultado.error and str(resultado.error).strip() != "":
                resposta.message("Erro ao salvar no banco. Tente novamente mais tarde.")
            elif not resultado.data:
                resposta.message("Erro: nenhum dado retornado do banco. Tente novamente.")
            else:
                resposta.message(f"Seu ganho líquido hoje é: R$ {liquido:.2f}")

            session.clear()
        else:
            resposta.message("Por favor, envie um número válido para o combustível.")
        return str(resposta)

    else:
        resposta = MessagingResponse()
        resposta.message("Erro inesperado. Vamos recomeçar.")
        session.clear()
        return str(resposta)
