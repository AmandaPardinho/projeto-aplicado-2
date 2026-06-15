-- ============================================================================
-- Tabela `anamnesis` (a ficha de saúde do cliente).
--
-- Rodar uma vez no SQL Editor do Supabase pra criar a tabela. Depois, gerar a
-- migration com ./database/scripts/dump_schema.sh.
--
-- ATENÇÃO: rodar SÓ depois que a tabela `client` existir, porque tem uma FK
-- apontando pra client.id.
--
-- Veio do MER v8 (entidade ANAMNESIS) e segue o padrão das outras tabelas:
-- soft-delete + timestamps. Como anamnese é dado de saúde (sensível pela LGPD),
-- guardar o histórico em vez de apagar importa ainda mais. A relação 1:1 com o
-- cliente é garantida pelo UNIQUE(client_id). A função prevent_created_at_update()
-- já foi criada junto com a tabela `client`.
-- ============================================================================

CREATE TABLE public.anamnesis (
    id                      uuid                     DEFAULT gen_random_uuid() NOT NULL,
    client_id               uuid                     NOT NULL,
    previous_illness        boolean                  DEFAULT false NOT NULL,
    illness_description     text,
    specific_complaint      boolean                  DEFAULT false NOT NULL,
    complaint_description   text,
    medication_use          boolean                  DEFAULT false NOT NULL,
    medication_description  text,
    physical_restriction    boolean                  DEFAULT false NOT NULL,
    restriction_description text,
    cleared_for_activity    boolean                  DEFAULT false NOT NULL,
    filled_at               timestamp with time zone DEFAULT now() NOT NULL,
    is_active               boolean                  DEFAULT true NOT NULL,
    deleted_at              timestamp with time zone,
    created_at              timestamp with time zone DEFAULT now() NOT NULL,
    updated_at              timestamp with time zone DEFAULT now() NOT NULL,

    CONSTRAINT anamnesis_pkey PRIMARY KEY (id),
    -- Um cliente tem no máximo uma anamnese (é o que faz a relação ser 1:1).
    CONSTRAINT anamnesis_client_id_key UNIQUE (client_id),
    -- A anamnese pertence a um cliente. Uso RESTRICT porque o client nunca é
    -- apagado de verdade (soft-delete), então não faz sentido apagar em cascata.
    CONSTRAINT anamnesis_client_id_fkey FOREIGN KEY (client_id)
        REFERENCES public.client (id) ON DELETE RESTRICT
);

-- Trava o created_at pra não ser alterado, reusando a função do `client`.
CREATE TRIGGER trg_anamnesis_created_at_immutable
    BEFORE UPDATE ON public.anamnesis
    FOR EACH ROW EXECUTE FUNCTION public.prevent_created_at_update();

-- RLS ligado (o backend usa a service_role e passa por cima; é a nossa postura de segurança).
ALTER TABLE public.anamnesis ENABLE ROW LEVEL SECURITY;
