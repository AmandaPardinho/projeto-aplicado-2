"""
Carrega as variáveis de ambiente do .env e expõe pro resto do app.
"""

import os
from dotenv import load_dotenv

# carrega o .env
load_dotenv()

# validação
try:
    SUPABASE_URL = os.environ["SUPABASE_URL"]
    SUPABASE_ANON_KEY = os.environ["SUPABASE_ANON_KEY"]
except KeyError as e:
    raise RuntimeError(
        f"Environment variable {e} is required but not found in .env file."
    )from e
