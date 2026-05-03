"""
Script de validação: prova que o Python conversa com o Supabase.
"""
from supabase import create_client, Client
from app.core.config import SUPABASE_URL, SUPABASE_ANON_KEY

# Cria o cliente Supabase (= conexão)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Testa: pega TODOS os instructors da tabela (deve voltar lista vazia)
response = supabase.table("instructor").select("*").execute()

print("✅ Conectou no Supabase!")
print(f"Registros encontrados: {len(response.data)}")
print(f"Dados: {response.data}")
