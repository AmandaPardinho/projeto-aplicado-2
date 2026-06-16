-- ============================================================
-- client_plan — matrícula da aluna num plano (entidade de junção).
--
-- Rode este script UMA VEZ no SQL Editor do Supabase. Depois, gere o dump
-- canônico com ./database/scripts/dump_schema.sh e versione o resultado.
--
-- Regras embutidas (fonte da verdade no banco):
--   - start_date imutável após a criação (trigger), igual ao created_at.
--   - end_date NOT NULL e posterior ao início (a matrícula vale 1 ano; quem
--     calcula end_date = start_date + 1 ano é o service).
--   - 1 aluna -> 1 plano ATIVO: índice único parcial em client_id WHERE is_active.
--   - soft-delete (is_active + deleted_at) + auditoria (created_at/updated_at).
-- ============================================================

begin;

-- Função: impede alterar o start_date depois de criado (espelha a de created_at).
create or replace function public.prevent_start_date_update() returns trigger
    language plpgsql
    as $$
begin
  if new.start_date is distinct from old.start_date then
    new.start_date := old.start_date;
  end if;
  return new;
end;
$$;

create table public.client_plan (
    id uuid default gen_random_uuid() not null,
    client_id uuid not null,
    plan_id uuid not null,
    start_date date default current_date not null,
    end_date date not null,
    renewal_date date,
    is_active boolean default true not null,
    deleted_at timestamp with time zone,
    created_at timestamp with time zone default now() not null,
    updated_at timestamp with time zone default now() not null,
    constraint client_plan_pkey primary key (id),
    constraint client_plan_end_after_start_check check ((end_date > start_date)),
    constraint client_plan_client_id_fkey foreign key (client_id)
        references public.client(id) on delete restrict,
    constraint client_plan_plan_id_fkey foreign key (plan_id)
        references public.plan(id) on delete restrict
);

-- 1 plano ATIVO por aluna. Índice parcial: só conta quando is_active = true,
-- então matrículas antigas (inativas) não bloqueiam uma nova.
create unique index client_plan_one_active_per_client
    on public.client_plan (client_id) where (is_active = true);

-- created_at imutável (reusa a função que já existe no schema).
create trigger trg_client_plan_created_at_immutable
    before update on public.client_plan
    for each row execute function public.prevent_created_at_update();

-- start_date imutável.
create trigger trg_client_plan_start_date_immutable
    before update on public.client_plan
    for each row execute function public.prevent_start_date_update();

-- O event trigger rls_auto_enable já liga RLS em tabelas novas; deixo explícito
-- por clareza (o backend usa service_role e passa por cima do RLS).
alter table public.client_plan enable row level security;

commit;
