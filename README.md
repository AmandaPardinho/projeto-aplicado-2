# projeto-aplicado-2

Repositório contendo códigos e demais materiais desenvolvidos na disciplina de Projeto Aplicado 2.

## Sobre o projeto

Sistema de **automatização de atendimento para Studio de Pilates** — backend em Python (FastAPI) integrado ao Supabase (PostgreSQL), com agente conversacional via WhatsApp e orquestração de fluxos com n8n.

## Stack

- **Backend:** Python 3.12+ · FastAPI · Pydantic v2 · Uvicorn
- **Banco de dados:** Supabase (PostgreSQL 17) — acesso via `supabase-py`
- **Orquestração de fluxos:** n8n
- **Mensageria:** WhatsApp Business API / Evolution API
- **Infraestrutura:** AWS

## Arquitetura

O backend segue separação em camadas (DDD lite):

| Camada | Pasta | Responsabilidade |
|---|---|---|
| **API** | `app/api/` | Routers FastAPI — recebe requisições HTTP, delega ao service e devolve a resposta |
| **Service** | `app/services/` | Regras de negócio — orquestra repository, valida regras complexas, prepara dados |
| **Repository** | `app/repositories/` | Única camada que conversa com o Supabase (encapsula o SDK) |
| **Schemas (DTOs)** | `app/schemas/` | Modelos Pydantic — entidade do banco + DTOs de Create/Read/Update |
| **Core** | `app/core/` | Configuração (`.env`), validators reutilizáveis (CPF, WhatsApp) |

Padrões aplicados:
- **Soft-delete** em todas as entidades (`is_active` + `deleted_at`) — LGPD compliance e auditoria.
- **Reativação automática** via `PUT {is_active: true}` (limpa `deleted_at` no service).
- **Imutabilidade de `created_at`** via trigger PostgreSQL (regra no banco, não no app).
- **Validação em duas camadas:** `CHECK` no banco (fonte da verdade) + Enum/Pydantic no app (UX e fail-fast).

## Estrutura do projeto

```
projeto-aplicado-2/
├── app/
│   ├── api/                # Routers FastAPI (controllers HTTP)
│   ├── services/           # Regras de negócio
│   ├── repositories/       # Acesso ao Supabase
│   ├── schemas/            # Pydantic DTOs (entidade + Create/Read/Update)
│   ├── core/               # Config, validators
│   └── main.py             # Entrypoint da app + middlewares + routers
├── database/
│   ├── scripts/            # Scripts auxiliares (bash) — ex.: dump_schema.sh
│   └── migrations/         # Histórico de DDL versionado (gerado por pg_dump)
├── tests/                  # Scripts de validação manual / testes automatizados
├── logs/                   # Logs da aplicação
├── requirements.txt        # Dependências Python
├── .env                    # Variáveis de ambiente (NÃO versionado)
└── .env.example            # Template das variáveis (versionado)
```

## Configuração inicial

### 1. Clonar e instalar dependências

```bash
git clone https://github.com/AmandaPardinho/projeto-aplicado-2.git
cd projeto-aplicado-2

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente

Copie o template e preencha com seus valores reais:

```bash
cp .env.example .env
```

Variáveis necessárias:

| Variável | Descrição | Origem (Supabase Dashboard) |
|----------|-----------|----------------------------|
| `SUPABASE_URL` | URL do projeto | Settings → API → Project URL |
| `SUPABASE_ANON_KEY` | Chave pública (frontend / API com RLS) | Settings → API → `anon` `public` |
| `SUPABASE_KEY` | Chave admin (backend privilegiado) | Settings → API → `service_role` |
| `SUPABASE_DB_HOST` | Host do banco para conexão direta (pg_dump) | Settings → Database → Direct connection |
| `SUPABASE_DB_PASSWORD` | Senha do banco PostgreSQL | Settings → Database → Database password |

> ⚠️ **Nunca exponha `SUPABASE_KEY` (service_role) no frontend** — ela bypassa RLS e tem acesso total ao banco.

> ⚠️ Se a senha contiver caracteres especiais como `$`, envolva o valor em **aspas simples** no `.env`:
> ```
> SUPABASE_DB_PASSWORD='senha$com$cifrao'
> ```

### 3. Subir a aplicação

```bash
uvicorn app.main:app --reload
```

Acesse:
- **API:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Endpoints disponíveis

### Health

| Método | Rota | Descrição |
|---|---|---|
| GET | `/` | Health check |

### Clients (`/clients`)

| Método | Rota | Descrição |
|---|---|---|
| POST | `/clients` | Cria um novo cliente |
| GET | `/clients` | Lista todos os clientes |
| GET | `/clients/{id}` | Busca cliente por ID |
| PUT | `/clients/{id}` | Atualiza campos do cliente (partial update) |
| DELETE | `/clients/{id}` | Soft-delete (marca `is_active=false` e `deleted_at`) |

**Regras de validação no DTO:**
- `cpf`: aceita máscara — 11 dígitos verificados pelo algoritmo oficial da Receita.
- `whatsapp_number`: aceita máscara — número BR com DDD válido e celular (9 após DDD), normalizado para o formato `5511987654321`.
- `client_status`: enum de 3 valores (`prospecto`, `ativo`, `inativo`) — espelha `CHECK` do banco.

### Instructors (`/instructors`)

| Método | Rota | Descrição |
|---|---|---|
| POST | `/instructors` | Cria um novo instrutor |
| GET | `/instructors` | Lista todos os instrutores |
| GET | `/instructors/{id}` | Busca instrutor por ID |
| PUT | `/instructors/{id}` | Atualiza campos do instrutor (partial update) |
| DELETE | `/instructors/{id}` | Soft-delete |

**Regras de validação no DTO:**
- `credential_number` (CREFITO): regex de formato + cross-field — obrigatório se `has_credential=true`.
- `instructor_status`: enum de 5 valores (`ativo`, `ferias`, `afastado`, `banco_de_vagas`, `inativo`).

## Gerenciamento do schema do banco

O DDL completo do banco (tabelas, triggers, funções) é versionado em `database/migrations/` e gerado automaticamente pelo script `dump_schema.sh`.

### Pré-requisitos

- **`pg_dump`** instalado no sistema:
  ```bash
  # Ubuntu/Debian/Mint
  sudo apt install postgresql-client

  # Verificar instalação
  pg_dump --version
  ```
- Variáveis `SUPABASE_DB_HOST` e `SUPABASE_DB_PASSWORD` configuradas no `.env`.

> ℹ️ A versão do `pg_dump` precisa ser **igual ou superior** à versão do Postgres no Supabase (atualmente 17). Se sua distro vier com versão antiga, instale do repositório PGDG (apt.postgresql.org).

### Executar o dump do schema

A partir da raiz do projeto:

```bash
# Dar permissão de execução (apenas na primeira vez)
chmod +x database/scripts/dump_schema.sh

# Rodar o dump
./database/scripts/dump_schema.sh
```

O script:
1. Lê as credenciais do `.env`.
2. Conecta ao Supabase via porta 5432 (Direct connection).
3. Gera um arquivo SQL com toda a estrutura do schema `public` (sem dados).
4. Salva em `database/migrations/<timestamp>_schema.sql`.
5. Imprime resumo com contagem de tabelas, triggers e funções.

### Quando rodar

Sempre que houver mudanças na estrutura do banco:
- Criação/alteração de tabelas
- Adição/modificação de triggers ou funções
- Alteração de constraints

Após gerar o dump, faça commit do arquivo gerado para versionar a evolução do schema.

```bash
git add database/migrations/
git commit -m "feat(db): update schema dump after <descrição da mudança>"
```

## Convenções

- **Commits:** [Conventional Commits](https://www.conventionalcommits.org/) — `feat:`, `fix:`, `docs:`, `refactor:`, etc.
- **Docstrings:** funções públicas têm `"""..."""` (acessível via `__doc__` e exibido no Swagger).
- **Imports:** topo do arquivo, agrupados (stdlib → terceiros → locais), seguindo PEP 8.
- **Variáveis de ambiente:** sempre em `MAIÚSCULAS` (convenção Unix), validadas via fail-fast no `core/config.py`.

## Roadmap

### Em andamento
- [ ] Frontend simples (HTML + JS puro) para o CRUD do cliente
- [ ] Reativar RLS no Supabase com policies adequadas

### Pós-MVP
- [ ] Migrar `class Config` → `model_config = ConfigDict(...)` (Pydantic v2 idiomático)
- [ ] Logger estruturado (`app/core/logger.py`)
- [ ] Modelagem das entidades restantes: Anamnese, Plano, Aluno_Plano, Agenda, Agendamento, Lista_Espera
- [ ] Testes automatizados com `pytest` e `FastAPI TestClient`
- [ ] Trigger PostgreSQL para auto-update de `updated_at`
- [ ] Autenticação JWT
- [ ] Integração com n8n + LLM (agente conversacional WhatsApp)
- [ ] Migração do gerenciador de pacotes para `uv`

## Equipe

- Amanda Marques Pardinho
- Daiane Olete da Silva Maniçoba
- Fabíola Reginaldo Corrêa da Silva
- Marta Sayuri Mukai

**Disciplina:** Projeto Aplicado II — Curso Superior de Tecnologia em Análise e Desenvolvimento de Sistemas
**Instituição:** Centro Universitário SENAI Santa Catarina
**Professora:** Janice Ines Deters
