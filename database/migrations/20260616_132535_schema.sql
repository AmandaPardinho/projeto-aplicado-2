--
-- PostgreSQL database dump
--

\restrict hCF5GX6KReNhHc08keaxWho89VPXdUviAlGplAae0rMucSMeHKqU0sQT31HvR5l

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.10 (Ubuntu 17.10-1.pgdg24.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA public;


--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA public IS 'standard public schema';


--
-- Name: prevent_created_at_update(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.prevent_created_at_update() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
begin
  if new.created_at is distinct from old.created_at then
    new.created_at := old.created_at;
  end if;
  return new;
end;
$$;


--
-- Name: prevent_start_date_update(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.prevent_start_date_update() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
begin
  if new.start_date is distinct from old.start_date then
    new.start_date := old.start_date;
  end if;
  return new;
end;
$$;


--
-- Name: rls_auto_enable(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.rls_auto_enable() RETURNS event_trigger
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO 'pg_catalog'
    AS $$
DECLARE
  cmd record;
BEGIN
  FOR cmd IN
    SELECT *
    FROM pg_event_trigger_ddl_commands()
    WHERE command_tag IN ('CREATE TABLE', 'CREATE TABLE AS', 'SELECT INTO')
      AND object_type IN ('table','partitioned table')
  LOOP
     IF cmd.schema_name IS NOT NULL AND cmd.schema_name IN ('public') AND cmd.schema_name NOT IN ('pg_catalog','information_schema') AND cmd.schema_name NOT LIKE 'pg_toast%' AND cmd.schema_name NOT LIKE 'pg_temp%' THEN
      BEGIN
        EXECUTE format('alter table if exists %s enable row level security', cmd.object_identity);
        RAISE LOG 'rls_auto_enable: enabled RLS on %', cmd.object_identity;
      EXCEPTION
        WHEN OTHERS THEN
          RAISE LOG 'rls_auto_enable: failed to enable RLS on %', cmd.object_identity;
      END;
     ELSE
        RAISE LOG 'rls_auto_enable: skip % (either system schema or not in enforced list: %.)', cmd.object_identity, cmd.schema_name;
     END IF;
  END LOOP;
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: anamnesis; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.anamnesis (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    client_id uuid NOT NULL,
    previous_illness boolean DEFAULT false NOT NULL,
    illness_description text,
    specific_complaint boolean DEFAULT false NOT NULL,
    complaint_description text,
    medication_use boolean DEFAULT false NOT NULL,
    medication_description text,
    physical_restriction boolean DEFAULT false NOT NULL,
    restriction_description text,
    cleared_for_activity boolean DEFAULT false NOT NULL,
    filled_at timestamp with time zone DEFAULT now() NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: client; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.client (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    whatsapp_number text NOT NULL,
    cpf text NOT NULL,
    email text NOT NULL,
    birth_date date NOT NULL,
    client_status text DEFAULT 'prospect'::text NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    marketing_consent boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT client_client_status_check CHECK ((client_status = ANY (ARRAY['prospect'::text, 'active'::text, 'inactive'::text]))),
    CONSTRAINT client_email_format_check CHECK ((email ~* '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$'::text))
);


--
-- Name: client_plan; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.client_plan (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    client_id uuid NOT NULL,
    plan_id uuid NOT NULL,
    start_date date DEFAULT CURRENT_DATE NOT NULL,
    end_date date NOT NULL,
    renewal_date date,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT client_plan_end_after_start_check CHECK ((end_date > start_date))
);


--
-- Name: instructor; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.instructor (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    email text NOT NULL,
    has_credential boolean DEFAULT false NOT NULL,
    credential_number text,
    specialty text,
    instructor_status text DEFAULT 'active'::text NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT instructor_email_format_check CHECK ((email ~* '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$'::text)),
    CONSTRAINT instructor_instructor_status_check CHECK ((instructor_status = ANY (ARRAY['active'::text, 'vacation'::text, 'on_leave'::text, 'standby'::text, 'inactive'::text])))
);


--
-- Name: plan; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.plan (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    sessions_per_month integer NOT NULL,
    monthly_fee numeric(10,2) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT plan_monthly_fee_check CHECK ((monthly_fee >= (0)::numeric)),
    CONSTRAINT plan_sessions_per_month_check CHECK ((sessions_per_month > 0))
);


--
-- Name: anamnesis anamnesis_client_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.anamnesis
    ADD CONSTRAINT anamnesis_client_id_key UNIQUE (client_id);


--
-- Name: anamnesis anamnesis_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.anamnesis
    ADD CONSTRAINT anamnesis_pkey PRIMARY KEY (id);


--
-- Name: client client_cpf_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client
    ADD CONSTRAINT client_cpf_key UNIQUE (cpf);


--
-- Name: client client_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client
    ADD CONSTRAINT client_pkey PRIMARY KEY (id);


--
-- Name: client_plan client_plan_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_plan
    ADD CONSTRAINT client_plan_pkey PRIMARY KEY (id);


--
-- Name: instructor instructor_credential_number_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.instructor
    ADD CONSTRAINT instructor_credential_number_key UNIQUE (credential_number);


--
-- Name: instructor instructor_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.instructor
    ADD CONSTRAINT instructor_email_key UNIQUE (email);


--
-- Name: instructor instructor_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.instructor
    ADD CONSTRAINT instructor_pkey PRIMARY KEY (id);


--
-- Name: plan plan_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.plan
    ADD CONSTRAINT plan_pkey PRIMARY KEY (id);


--
-- Name: client_plan_one_active_per_client; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX client_plan_one_active_per_client ON public.client_plan USING btree (client_id) WHERE (is_active = true);


--
-- Name: anamnesis trg_anamnesis_created_at_immutable; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_anamnesis_created_at_immutable BEFORE UPDATE ON public.anamnesis FOR EACH ROW EXECUTE FUNCTION public.prevent_created_at_update();


--
-- Name: client trg_client_created_at_immutable; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_client_created_at_immutable BEFORE UPDATE ON public.client FOR EACH ROW EXECUTE FUNCTION public.prevent_created_at_update();


--
-- Name: client_plan trg_client_plan_created_at_immutable; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_client_plan_created_at_immutable BEFORE UPDATE ON public.client_plan FOR EACH ROW EXECUTE FUNCTION public.prevent_created_at_update();


--
-- Name: client_plan trg_client_plan_start_date_immutable; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_client_plan_start_date_immutable BEFORE UPDATE ON public.client_plan FOR EACH ROW EXECUTE FUNCTION public.prevent_start_date_update();


--
-- Name: instructor trg_instructor_created_at_immutable; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_instructor_created_at_immutable BEFORE UPDATE ON public.instructor FOR EACH ROW EXECUTE FUNCTION public.prevent_created_at_update();


--
-- Name: plan trg_plan_created_at_immutable; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_plan_created_at_immutable BEFORE UPDATE ON public.plan FOR EACH ROW EXECUTE FUNCTION public.prevent_created_at_update();


--
-- Name: anamnesis anamnesis_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.anamnesis
    ADD CONSTRAINT anamnesis_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.client(id) ON DELETE RESTRICT;


--
-- Name: client_plan client_plan_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_plan
    ADD CONSTRAINT client_plan_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.client(id) ON DELETE RESTRICT;


--
-- Name: client_plan client_plan_plan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_plan
    ADD CONSTRAINT client_plan_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES public.plan(id) ON DELETE RESTRICT;


--
-- Name: anamnesis; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.anamnesis ENABLE ROW LEVEL SECURITY;

--
-- Name: client; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.client ENABLE ROW LEVEL SECURITY;

--
-- Name: client_plan; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.client_plan ENABLE ROW LEVEL SECURITY;

--
-- Name: instructor; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.instructor ENABLE ROW LEVEL SECURITY;

--
-- Name: plan; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.plan ENABLE ROW LEVEL SECURITY;

--
-- PostgreSQL database dump complete
--

\unrestrict hCF5GX6KReNhHc08keaxWho89VPXdUviAlGplAae0rMucSMeHKqU0sQT31HvR5l

