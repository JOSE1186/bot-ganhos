class CalculosService:
    def extrair_dados(self, mensagem):
        try:
            partes = mensagem.split()
            ganhos = float(partes[0])
            combustivel = float(partes[1])
            return ganhos, combustivel
        except:
            return 0, 0

    def calcular_liquido(self, ganhos, combustivel):
        return ganhos - combustivel
