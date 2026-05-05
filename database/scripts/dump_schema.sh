#!/usr/bin/env bash
#
# dump_schema.sh — Gera dump do schema (DDL) do banco Supabase
# Uso: ./database/scripts/dump_schema.sh
# Pré-requisitos:
#   - pg_dump instalado (postgresql-client)
#   - Variáveis SUPABASE_DB_HOST e SUPABASE_DB_PASSWORD definidas em .env
#

# Configurações de segurança do bash (fail-fast):
# -e : sai imediatamente se algum comando falhar
# -u : trata variável não definida como erro
# -o pipefail : se algum comando de um pipe falhar, o pipe inteiro falha

set -euo pipefail

# ----------------------------------------------------------------------------
# DETECTAR pg_dump COMPATÍVEL COM A VERSÃO DO SERVIDOR (Supabase = PostgreSQL 17+)
# Prioridade: pg_dump 17 > pg_dump 18 > pg_dump padrão do PATH
# ----------------------------------------------------------------------------

if [[ -x /usr/lib/postgresql/17/bin/pg_dump ]]; then
    PG_DUMP_BIN="/usr/lib/postgresql/17/bin/pg_dump"
elif [[ -x /usr/lib/postgresql/18/bin/pg_dump ]]; then
    PG_DUMP_BIN="/usr/lib/postgresql/18/bin/pg_dump"
else
    PG_DUMP_BIN="$(command -v pg_dump || true)"
    if [[ -z "$PG_DUMP_BIN" ]]; then
        echo "❌ Erro: pg_dump não encontrado. Instale postgresql-client-17."
        exit 1
    fi
fi

# ----------------------------------------------------------------------------
# RESOLVER CAMINHOS (funciona de qualquer diretório que você chamar o script)
# ----------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

ENV_FILE="$PROJECT_ROOT/.env"
OUTPUT_DIR="$PROJECT_ROOT/database/migrations"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
OUTPUT_FILE="$OUTPUT_DIR/${TIMESTAMP}_schema.sql"

# ----------------------------------------------------------------------------
# CARREGAR VARIÁVEIS DO .ENV
# ----------------------------------------------------------------------------

if [[ ! -f "$ENV_FILE" ]]; then
    echo "❌ Erro: arquivo .env não encontrado em $ENV_FILE"
    exit 1
fi

# 'set -a' faz com que toda variável atribuída seja automaticamente exportada
set -a

# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

# Valida que as variáveis necessárias existem (sintaxe `${VAR:?mensagem}`)
: "${SUPABASE_DB_HOST:?variável SUPABASE_DB_HOST não definida no .env}"
: "${SUPABASE_DB_PASSWORD:?variável SUPABASE_DB_PASSWORD não definida no .env}"

# ----------------------------------------------------------------------------
# EXECUTAR O DUMP
# ----------------------------------------------------------------------------

mkdir -p "$OUTPUT_DIR"

echo "🔄 Gerando dump do schema..."
echo "   pg_dump: $PG_DUMP_BIN ($("$PG_DUMP_BIN" --version | awk '{print $3}'))"
echo "   Host:    $SUPABASE_DB_HOST"
echo "   Output:  $OUTPUT_FILE"
echo ""

# PGPASSWORD na frente do comando = passa só para esse processo
PGPASSWORD="$SUPABASE_DB_PASSWORD" "$PG_DUMP_BIN" \
    --host="$SUPABASE_DB_HOST" \
    --port=5432 \
    --username=postgres \
    --dbname=postgres \
    --schema=public \
    --schema-only \
    --no-owner \
    --no-privileges \
    --file="$OUTPUT_FILE"

# ----------------------------------------------------------------------------
# RESUMO DO QUE FOI GERADO
# ----------------------------------------------------------------------------

echo "✅ Dump gerado com sucesso!"
echo ""
echo "📊 Resumo do schema:"
printf "   Tabelas:   %s\n" "$(grep -c '^CREATE TABLE' "$OUTPUT_FILE" || echo 0)"
printf "   Triggers:  %s\n" "$(grep -c '^CREATE TRIGGER' "$OUTPUT_FILE" || echo 0)"
printf "   Functions: %s\n" "$(grep -c '^CREATE FUNCTION' "$OUTPUT_FILE" || echo 0)"
echo ""
echo "📁 Arquivo: $OUTPUT_FILE"
