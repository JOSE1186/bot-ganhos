from supabase import create_client
import os

class SupabaseService:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        self.client = create_client(self.url, self.key)

    def salvar_dados(self, numero, ganhos, combustivel, liquido):
        self.client.table("ganhos").insert({
            "numero_usuario": numero,
            "ganhos": ganhos,
            "combustivel": combustivel,
            "liquido": liquido
        }).execute()
