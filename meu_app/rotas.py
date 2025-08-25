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
        resposta = MessagingResponse()

        # Inicializa estado da sessão
        if "estado" not in session:
            session["estado"] = "inicio"

        # Estado inicial → mostra o menu principal
        if session["estado"] == "inicio":
            resposta.message("📌 MENU PRINCIPAL\n\n"
                             "1️⃣ Inserir ganho\n"
                             "2️⃣ Ver saldo\n"
                             "3️⃣ Sair")
            session["estado"] = "menu"
            return str(resposta)

        # Estado menu → decide o que fazer
        elif session["estado"] == "menu":
            if msg == "1":
                resposta.message("💰 Digite o valor do ganho bruto:")
                session["estado"] = "aguardando_ganho"

            elif msg == "2":
                try:
                    # Busca os dados no Supabase
                    dados = supabase.table("ganhos").select("bruto", "combustivel").execute()

                    if not dados or not hasattr(dados, "data") or not dados.data:
                        resposta.message("📌 Nenhum registro encontrado.")
                    else:
                        total_liquido = sum(item.get("bruto", 0) - item.get("combustivel", 0)
                                            for item in dados.data)
                        resposta.message(f"📊 Ganho líquido total: R$ {total_liquido:.2f}")
                except Exception as e:
                    resposta.message(f"❌ Erro ao acessar o banco: {e}")

                session["estado"] = "inicio"

            elif msg == "3":
                resposta.message("✅ Bot encerrado. Até logo!")
                session.clear()

            else:
                resposta.message("⚠️ Opção inválida! Digite 1, 2 ou 3.")
            return str(resposta)

        # Estado aguardando ganho bruto
        elif session["estado"] == "aguardando_ganho":
            ganho = tentar_converter_para_float(msg)
            if ganho is not None:
                session["ganho"] = ganho
                resposta.message("⛽ Agora digite o valor gasto com combustível:")
                session["estado"] = "aguardando_combustivel"
            else:
                resposta.message("⚠️ Por favor, envie um número válido. Exemplo: 100 ou 100.50")
            return str(resposta)

        # Estado aguardando combustível
        elif session["estado"] == "aguardando_combustivel":
            combustivel = tentar_converter_para_float(msg)
            if combustivel is not None:
                ganho = session.get("ganho", 0)

                try:
                    # Salva os dados no Supabase
                    resultado = supabase.table("ganhos").insert({
                        "bruto": ganho,
                        "combustivel": combustivel
                    }).execute()

                    # Verifica se houve erro na resposta
                    if not resultado or hasattr(resultado, "error") and resultado.error:
                        resposta.message("❌ Erro ao salvar no banco. Tente novamente mais tarde.")
                    else:
                        resposta.message("✅ Dados salvos com sucesso!")
                except Exception as e:
                    resposta.message(f"❌ Erro inesperado: {e}")

                session.clear()
            else:
                resposta.message("⚠️ Por favor, envie um número válido para o combustível.")
            return str(resposta)

        # Caso inesperado → reseta a sessão
        else:
            resposta.message("⚠️ Erro inesperado. Vamos recomeçar.")
            session.clear()
            return str(resposta)
