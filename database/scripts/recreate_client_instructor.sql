-- ============================================================================
-- Recriação das tabelas `client` e `instructor` no estado FINAL.
--
-- Uso pontual: rodar UMA vez no SQL Editor do Supabase para dropar e recriar
-- as duas tabelas já com (1) coluna `email`, (2) status em inglês.
-- Depois, gerar a migration oficial com ./database/scripts/dump_schema.sh.

-- ===================================================================
-- CLIENT
-- ===================================================================
DROP TABLE IF EXISTS public.client CASCADE;

CREATE TABLE public.client (
    id                uuid                     DEFAULT gen_random_uuid() NOT NULL,
    name              text                     NOT NULL,
    whatsapp_number   text                     NOT NULL,
    cpf               text                     NOT NULL,
    email             text                     NOT NULL,
    birth_date        date                     NOT NULL,
    client_status     text                     DEFAULT 'prospect'::text NOT NULL,
    is_active         boolean                  DEFAULT true NOT NULL,
    marketing_consent boolean                  DEFAULT true NOT NULL,
    deleted_at        timestamp with time zone,
    created_at        timestamp with time zone DEFAULT now() NOT NULL,
    updated_at        timestamp with time zone DEFAULT now() NOT NULL,

    CONSTRAINT client_pkey PRIMARY KEY (id),
    CONSTRAINT client_cpf_key UNIQUE (cpf),
    -- email NÃO é único: studio aceita menores (MIN_AGE_YEARS=4) que usam o e-mail do responsável.
    CONSTRAINT client_client_status_check
        CHECK (client_status = ANY (ARRAY['prospect'::text, 'active'::text, 'inactive'::text])),
    CONSTRAINT client_email_format_check
        CHECK (email ~* '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$')
);

-- created_at imutável (mesmo trigger de antes)
CREATE TRIGGER trg_client_created_at_immutable
    BEFORE UPDATE ON public.client
    FOR EACH ROW EXECUTE FUNCTION public.prevent_created_at_update();

-- RLS (o backend usa service_role e ignora; mantém a postura de segurança)
ALTER TABLE public.client ENABLE ROW LEVEL SECURITY;


-- ===================================================================
-- INSTRUCTOR
-- ===================================================================
DROP TABLE IF EXISTS public.instructor CASCADE;

CREATE TABLE public.instructor (
    id                uuid                     DEFAULT gen_random_uuid() NOT NULL,
    name              text                     NOT NULL,
    email             text                     NOT NULL,
    has_credential    boolean                  DEFAULT false NOT NULL,
    credential_number text,
    specialty         text,
    instructor_status text                     DEFAULT 'active'::text NOT NULL,
    is_active         boolean                  DEFAULT true NOT NULL,
    deleted_at        timestamp with time zone,
    created_at        timestamp with time zone DEFAULT now() NOT NULL,
    updated_at        timestamp with time zone DEFAULT now() NOT NULL,

    CONSTRAINT instructor_pkey PRIMARY KEY (id),
    CONSTRAINT instructor_credential_number_key UNIQUE (credential_number),
    CONSTRAINT instructor_email_key UNIQUE (email),
    CONSTRAINT instructor_instructor_status_check
        CHECK (instructor_status = ANY (ARRAY['active'::text, 'vacation'::text, 'on_leave'::text, 'standby'::text, 'inactive'::text])),
    CONSTRAINT instructor_email_format_check
        CHECK (email ~* '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$')
);

CREATE TRIGGER trg_instructor_created_at_immutable
    BEFORE UPDATE ON public.instructor
    FOR EACH ROW EXECUTE FUNCTION public.prevent_created_at_update();

ALTER TABLE public.instructor ENABLE ROW LEVEL SECURITY;
