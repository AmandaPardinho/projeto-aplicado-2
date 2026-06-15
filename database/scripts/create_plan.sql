-- ============================================================================
-- Tabela `plan` (o catálogo de planos do studio).
--
-- Rodar uma vez no SQL Editor do Supabase pra criar a tabela. Depois, gerar a
-- migration com ./database/scripts/dump_schema.sh.
--
-- Veio do MER v8 (entidade PLAN), mas além dos campos do diagrama (name,
-- sessions_per_month, monthly_fee) a gente segue o padrão das outras tabelas:
-- soft-delete (is_active + deleted_at) e timestamps. A função
-- prevent_created_at_update() já foi criada junto com a tabela `client`, então
-- aqui só criamos a tabela e o trigger que reusa ela.
-- ============================================================================

CREATE TABLE public.plan (
    id                 uuid                     DEFAULT gen_random_uuid() NOT NULL,
    name               text                     NOT NULL,
    sessions_per_month integer                  NOT NULL,
    monthly_fee        numeric(10,2)            NOT NULL,
    is_active          boolean                  DEFAULT true NOT NULL,
    deleted_at         timestamp with time zone,
    created_at         timestamp with time zone DEFAULT now() NOT NULL,
    updated_at         timestamp with time zone DEFAULT now() NOT NULL,

    CONSTRAINT plan_pkey PRIMARY KEY (id),
    -- Travas de sanidade: o banco é a fonte da verdade, e o Pydantic repete pra
    -- avisar cedo o usuário. Não dá pra ter sessão negativa nem mensalidade negativa.
    CONSTRAINT plan_sessions_per_month_check CHECK (sessions_per_month > 0),
    CONSTRAINT plan_monthly_fee_check        CHECK (monthly_fee >= 0)
);

-- Trava o created_at pra não ser alterado, reusando a função do `client`.
CREATE TRIGGER trg_plan_created_at_immutable
    BEFORE UPDATE ON public.plan
    FOR EACH ROW EXECUTE FUNCTION public.prevent_created_at_update();

-- RLS ligado (o backend usa a service_role e passa por cima; é a nossa postura de segurança).
ALTER TABLE public.plan ENABLE ROW LEVEL SECURITY;
