-- PIEM Tusker Power 3.1 — hardening opcional para Supabase/PostgreSQL.
-- A fonte de verdade do schema são as migrações Django. Execute antes:
--   python manage.py migrate
-- Este arquivo adiciona restrições, índices operacionais e bloqueia tabelas sensíveis
-- para os papéis REST públicos do Supabase.

ALTER TABLE public.core_user
    DROP CONSTRAINT IF EXISTS core_user_enterprise_role_check;
ALTER TABLE public.core_user
    ADD CONSTRAINT core_user_enterprise_role_check
    CHECK (perfil_acesso IN ('student', 'teacher', 'admin', 'recruiter'));

CREATE INDEX IF NOT EXISTS core_user_school_role_idx
    ON public.core_user (escola_id, perfil_acesso);
CREATE INDEX IF NOT EXISTS core_workshop_catalog_idx
    ON public.core_workshop (status, data, area, modalidade);
CREATE INDEX IF NOT EXISTS core_submission_status_idx
    ON public.core_challengesubmission (status, enviado_em DESC);
CREATE INDEX IF NOT EXISTS core_job_school_active_idx
    ON public.core_jobopportunity (escola_id, ativa, criada_em DESC);
CREATE INDEX IF NOT EXISTS core_audit_created_idx
    ON public.core_auditlog (criado_em DESC);

-- O Django acessa o banco pelo usuário de servidor configurado em DB_USER. As chaves
-- anon/authenticated do Supabase não recebem acesso direto a dados escolares ou sigilosos.
REVOKE ALL ON TABLE public.core_safereport FROM anon, authenticated;
REVOKE ALL ON TABLE public.core_auditlog FROM anon, authenticated;
REVOKE ALL ON TABLE public.core_softskillassessment FROM anon, authenticated;
REVOKE ALL ON TABLE public.core_challengesubmission FROM anon, authenticated;
REVOKE ALL ON TABLE public.core_attendance FROM anon, authenticated;

ALTER TABLE public.core_studentproject ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "piem_public_projects" ON public.core_studentproject;
CREATE POLICY "piem_public_projects"
ON public.core_studentproject
FOR SELECT
TO anon, authenticated
USING (publico = TRUE);

-- A vitrine de talentos deve passar pelo backend Django, que aplica consentimento,
-- anonimização, filtros de tenant e AuditLog; não exponha core_user via PostgREST.
REVOKE SELECT ON TABLE public.core_user FROM anon, authenticated;
