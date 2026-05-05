--
-- PostgreSQL database dump
--

\restrict 1I1Ju0QfSIk9VXDLcC8XVHadei4MqbChchD0v6Lldl80IXCwW79kHwmik8WonQ5

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.9 (Ubuntu 17.9-1.pgdg24.04+1)

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
-- Name: client; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.client (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    whatsapp_number text NOT NULL,
    cpf text NOT NULL,
    birth_date date NOT NULL,
    client_status text DEFAULT 'prospecto'::text NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    marketing_consent boolean DEFAULT true NOT NULL,
    CONSTRAINT client_client_status_check CHECK ((client_status = ANY (ARRAY['prospecto'::text, 'ativo'::text, 'inativo'::text])))
);


--
-- Name: instructor; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.instructor (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    has_credential boolean DEFAULT false NOT NULL,
    credential_number text,
    specialty text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    instructor_status text DEFAULT 'ativo'::text NOT NULL,
    CONSTRAINT instructor_instructor_status_check CHECK ((instructor_status = ANY (ARRAY['ativo'::text, 'ferias'::text, 'afastado'::text, 'banco_de_vagas'::text, 'inativo'::text])))
);


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
-- Name: instructor instructor_credential_number_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.instructor
    ADD CONSTRAINT instructor_credential_number_key UNIQUE (credential_number);


--
-- Name: instructor instructor_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.instructor
    ADD CONSTRAINT instructor_pkey PRIMARY KEY (id);


--
-- Name: client trg_client_created_at_immutable; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_client_created_at_immutable BEFORE UPDATE ON public.client FOR EACH ROW EXECUTE FUNCTION public.prevent_created_at_update();


--
-- Name: instructor trg_instructor_created_at_immutable; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_instructor_created_at_immutable BEFORE UPDATE ON public.instructor FOR EACH ROW EXECUTE FUNCTION public.prevent_created_at_update();


--
-- PostgreSQL database dump complete
--

\unrestrict 1I1Ju0QfSIk9VXDLcC8XVHadei4MqbChchD0v6Lldl80IXCwW79kHwmik8WonQ5

