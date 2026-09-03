from django.urls import path
from . import views

urlpatterns = [
    # Páginas Principais e Institucionais
    path("", views.home, name="home"),
    path("vitrine/", views.showcase_view, name="showcase"),
    path("cursos/", views.courses_view, name="courses"),
    path("canal-seguro/", views.safe_report, name="safe_report"),

    # Autenticação e Usuários Separados
    path("cadastro/", views.register_view, name="register"),
    path("entrar/", views.login_aluno_view, name="login"),
    path("entrar/aluno/", views.login_aluno_view, name="login_aluno"),
    path("admin-login/", views.login_admin_view, name="login_admin"),
    path("sair/", views.logout_view, name="logout"),

    # Portais segregados por RBAC
    path("painel/", views.dashboard, name="dashboard"),
    path("painel/professor/", views.teacher_dashboard, name="teacher_dashboard"),
    path("painel/recrutador/", views.recruiter_dashboard, name="recruiter_dashboard"),
    path("painel/professor/desafios/novo/", views.challenge_create, name="challenge_create"),
    path("painel/professor/entregas/<int:submission_id>/", views.submission_review, name="submission_review"),
    path("painel/professor/alunos/<int:student_id>/soft-skills/", views.soft_skill_assess, name="soft_skill_assess"),
    path("projetos/novo/", views.project_create, name="project_create"),
    path("projetos/<int:project_id>/editar/", views.project_edit, name="project_edit"),
    path("projetos/<int:project_id>/excluir/", views.project_delete, name="project_delete"),
    path("desafios/<int:challenge_id>/entregar/", views.challenge_submit, name="challenge_submit"),
    path("oficinas/<int:workshop_id>/inscrever/", views.workshop_enroll, name="workshop_enroll"),
    path("vagas/<int:job_id>/candidatar/", views.job_apply, name="job_apply"),
    path("vagas/nova/", views.job_create, name="job_create"),

    # Painel de Controle Administrativo (Exclusivo Gestores)
    path("painel/admin/", views.admin_dashboard_view, name="admin_dashboard"),
    path("painel/admin/oficinas/nova/", views.admin_workshop_create, name="admin_workshop_create"),
    path("painel/admin/oficinas/<int:workshop_id>/", views.admin_workshop_detail, name="admin_workshop_detail"),
    path("painel/admin/oficinas/<int:workshop_id>/editar/", views.admin_workshop_edit, name="admin_workshop_edit"),
    path("painel/admin/oficinas/<int:workshop_id>/excluir/", views.admin_workshop_delete, name="admin_workshop_delete"),
    path("painel/admin/usuarios/novo/", views.admin_user_create, name="admin_user_create"),
    path("painel/admin/usuarios/<int:user_id>/editar/", views.admin_user_edit, name="admin_user_edit"),
    path("painel/admin/usuarios/<int:user_id>/status/", views.admin_user_toggle_active, name="admin_user_toggle_active"),
    path("painel/admin/usuarios/<int:user_id>/excluir/", views.admin_user_delete, name="admin_user_delete"),
    path("painel/admin/relatos/<int:report_id>/tratar/", views.admin_safe_report_toggle, name="admin_safe_report_toggle"),
    path("painel/admin/relatorios/impacto.<str:format>", views.impact_export, name="impact_export"),

    # Certificados
    path("certificados/<uuid:code>/", views.certificate_verify, name="certificate_verify"),
    path("certificados/<uuid:code>/qr.png", views.certificate_qr, name="certificate_qr"),
    path("curriculo.pdf", views.resume_pdf, name="resume_pdf"),
    path("curriculos/validar/<str:token>/", views.resume_verify, name="resume_verify"),

    # APIs e Integrações (Tutor PIEM Inteligente)
    path("api/tutor-chat/", views.tutor_api, name="tutor_api"),
    path("api/bridge/tutor/", views.php_bridge_tutor_api, name="php_bridge_tutor_api"),
]
