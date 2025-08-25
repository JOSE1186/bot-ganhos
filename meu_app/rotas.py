from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
from supabase import create_client
import os

app = Flask(__name__)
app.secret_key = 'chave-secreta-super-segura'

# Configuração do Supabase
url = "https://mbyuhxjbwmvbhpieywjm.supabase.co"
key = "SUA_CHAVE_API"  # Substitua pela sua chave real
supabase = create_client(url, key)

@app.route("/bot", methods=["POST"])
def bot():
    try:
        # Pega a mensagem do usuário
        msg_usuario = request.form.get("Body", "").strip()
        resposta = MessagingResponse()

        # Recupera o estado da conversa
        if "estado" not in session:
            session["estado"] = "aguardando_ganho"

        # ------------------------------
        # 1. Entrada do ganho bruto
        # ------------------------------
        if session["estado"] == "aguardando_ganho":
            try:
                ganho = float(msg_usuario.replace(",", "."))
                session["ganho"] = ganho
                session["estado"] = "aguardando_combustivel"
                resposta.message("⛽ Informe o valor gasto com combustível:")
            except ValueError:
                resposta.message("❌ Valor inválido! Por favor, insira um número.")
            return str(resposta)

        # ------------------------------
        # 2. Entrada do combustível
        # ------------------------------
        elif session["estado"] == "aguardando_combustivel":
            try:
                combustivel = float(msg_usuario.replace(",", "."))
                ganho = session.get("ganho", 0.0)

                # Insere os dados no Supabase com tratamento seguro
                try:
                    resultado = supabase.table("ganhos").insert({
                        "bruto": ganho,
                        "combustivel": combustivel
                    }).execute()

                    # Caso a resposta venha vazia
                    if not resultado or not hasattr(resultado, "data") or resultado.data is None:
                        resposta.message("✅ Dados salvos com sucesso!")
                    elif hasattr(resultado, "error") and resultado.error:
                        resposta.message("❌ Erro ao salvar no banco. Tente novamente.")
                    else:
                        resposta.message("✅ Dados salvos com sucesso!")

                except Exception as e:
                    resposta.message(f"❌ Erro inesperado ao salvar: {e}")

                # Calcula o valor líquido e mostra para o usuário
                liquido = ganho - combustivel
                resposta.message(f"💰 Ganho líquido: R$ {liquido:.2f}")

                # Volta para o estado inicial
                session["estado"] = "aguardando_ganho"
                return str(resposta)

            except ValueError:
                resposta.message("❌ Valor inválido! Por favor, insira um número.")
                return str(resposta)

        # ------------------------------
        # 3. Consulta de saldo total
        # ------------------------------
        elif msg_usuario.lower() == "saldo":
            try:
                dados = supabase.table("ganhos").select("bruto", "combustivel").execute()

                # Caso não tenha dados
                if not dados or not hasattr(dados, "data") or not dados.data:
                    resposta.message("📌 Nenhum registro encontrado.")
                else:
                    total_liquido = sum(
                        item.get("bruto", 0) - item.get("combustivel", 0)
                        for item in dados.data
                    )
                    resposta.message(f"📊 Ganho líquido total: R$ {total_liquido:.2f}")

            except Exception as e:
                resposta.message(f"❌ Erro inesperado ao buscar saldo: {e}")
            return str(resposta)

        else:
            resposta.message("💬 Envie o valor bruto ou digite 'saldo' para ver o total.")
            return str(resposta)

    except Exception as e:
        return f"❌ Erro inesperado: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
