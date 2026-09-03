from datetime import timedelta

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import (
    Attendance,
    ChallengeSubmission,
    PracticalChallenge,
    SafeReport,
    School,
    SchoolClass,
    SoftSkillAssessment,
    StudentProject,
    User,
    Workshop,
    WorkshopEnrollment,
)
from .services import decrypt_sensitive, employability_score


class EnterpriseFlowTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(nome="Escola Horizonte", codigo="horizonte")
        self.other_school = School.objects.create(nome="Escola Outra", codigo="outra")
        self.classroom = SchoolClass.objects.create(escola=self.school, nome="3º A", ano_letivo=2026)
        self.other_classroom = SchoolClass.objects.create(escola=self.other_school, nome="3º B", ano_letivo=2026)
        self.student = User.objects.create_user(
            "student@example.com", "test-password", nome="Ana Estudante", perfil_acesso=User.Role.STUDENT,
            escola=self.school, turma=self.classroom, consentimento_vitrine=True, competencias="Python, comunicação",
        )
        self.other_student = User.objects.create_user(
            "other@example.com", "test-password", nome="Nome que não pode vazar", perfil_acesso=User.Role.STUDENT,
            escola=self.other_school, turma=self.other_classroom, consentimento_vitrine=True,
        )
        self.teacher = User.objects.create_user(
            "teacher@example.com", "test-password", nome="Professora Bia", perfil_acesso=User.Role.TEACHER, escola=self.school,
        )
        self.classroom.professores.add(self.teacher)
        self.recruiter = User.objects.create_user(
            "recruiter@example.com", "test-password", nome="Empresa", perfil_acesso=User.Role.RECRUITER, escola=self.school,
        )
        self.admin = User.objects.create_superuser(
            "admin@example.com", "test-password", nome="Gestora PIEM",
        )

    def test_employability_score_reaches_1000_with_full_components(self):
        for day in range(10):
            Attendance.objects.create(user=self.student, data=timezone.localdate() - timedelta(days=day), presente=True)
        SoftSkillAssessment.objects.create(
            aluno=self.student, avaliador=self.teacher, comunicacao=5, proatividade=5, trabalho_equipe=5,
        )
        challenge = PracticalChallenge.objects.create(
            titulo="Entrega", descricao="Evidência", area="Tecnologia da Informação", pontos=100,
            turma=self.classroom, criado_por=self.teacher,
        )
        ChallengeSubmission.objects.create(
            desafio=challenge, aluno=self.student, resposta="Pronto", status=ChallengeSubmission.Status.APPROVED,
            pontos_atribuidos=100, avaliado_por=self.teacher,
        )
        score = employability_score(self.student)
        self.assertEqual(score["score"], 1000)
        self.assertEqual(score["components"], {"frequencia": 350, "soft_skills": 300, "entregas": 350})

    def test_role_segregation_blocks_student_from_teacher_portal(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("teacher_dashboard"))
        self.assertEqual(response.status_code, 403)
        self.client.force_login(self.teacher)
        response = self.client.get(reverse("teacher_dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_student_cannot_submit_challenge_from_another_tenant(self):
        challenge = PracticalChallenge.objects.create(
            titulo="Outro tenant", descricao="Não autorizado", area="Educação", pontos=50,
            turma=self.other_classroom, criado_por=self.teacher,
        )
        self.client.force_login(self.student)
        response = self.client.post(reverse("challenge_submit", args=[challenge.pk]), {"resposta": "tentativa"})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(ChallengeSubmission.objects.exists())

    def test_talent_showcase_is_anonymous_and_tenant_scoped(self):
        self.client.force_login(self.recruiter)
        response = self.client.get(reverse("recruiter_dashboard"))
        self.assertContains(response, self.student.talent_code)
        self.assertNotContains(response, self.student.nome)
        self.assertNotContains(response, self.other_student.nome)
        self.assertNotContains(response, self.other_student.talent_code)

    def test_safe_report_is_encrypted_at_rest(self):
        response = self.client.post(reverse("safe_report"), {
            "categoria": "Acolhimento", "mensagem": "Preciso conversar em segurança", "contato": "canal@seguro.test",
        })
        self.assertEqual(response.status_code, 302)
        report = SafeReport.objects.get()
        self.assertTrue(report.mensagem.startswith("enc:v1:"))
        self.assertNotIn("Preciso conversar", report.mensagem)
        self.assertEqual(decrypt_sensitive(report.mensagem), "Preciso conversar em segurança")

    def test_registration_uses_password_without_leaking_form_field_to_model(self):
        response = self.client.post(reverse("register"), {
            "nome": "Novo Aluno",
            "identifier": "novo@example.com",
            "perfil_acesso": User.Role.STUDENT,
            "area_interesse": "Engenharia",
            "senha": "uma-senha-segura",
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(identifier="novo@example.com")
        self.assertTrue(user.check_password("uma-senha-segura"))

    @override_settings(PHP_BRIDGE_SECRET="bridge-test-secret")
    def test_php_bridge_requires_shared_secret(self):
        url = reverse("php_bridge_tutor_api")
        denied = self.client.post(url, data='{"mensagem":"tarefa_dia"}', content_type="application/json")
        self.assertEqual(denied.status_code, 403)
        accepted = self.client.post(
            url,
            data='{"mensagem":"tarefa_dia","area":"Engenharia"}',
            content_type="application/json",
            HTTP_X_PIEM_BRIDGE_SECRET="bridge-test-secret",
        )
        self.assertEqual(accepted.status_code, 200)
        self.assertEqual(accepted.json()["resposta_tutor"]["provider"], "local")

    def test_public_course_catalog_filters_drafts_and_past_events(self):
        Workshop.objects.create(
            titulo="Curso publicado", area="Engenharia", data=timezone.now() + timedelta(days=3),
            descricao="Visível", status=Workshop.Status.PUBLISHED,
        )
        Workshop.objects.create(
            titulo="Curso rascunho", area="Engenharia", data=timezone.now() + timedelta(days=3),
            descricao="Oculto", status=Workshop.Status.DRAFT,
        )
        Workshop.objects.create(
            titulo="Curso encerrado", area="Engenharia", data=timezone.now() - timedelta(days=1),
            descricao="Passado", status=Workshop.Status.PUBLISHED,
        )
        response = self.client.get(reverse("courses"))
        self.assertContains(response, "Curso publicado")
        self.assertNotContains(response, "Curso rascunho")
        self.assertNotContains(response, "Curso encerrado")

    def test_course_enrollment_respects_capacity_and_can_be_cancelled(self):
        course = Workshop.objects.create(
            titulo="Laboratório", area="Ciência", data=timezone.now() + timedelta(days=3),
            descricao="Prática", vagas=1, status=Workshop.Status.PUBLISHED,
        )
        self.client.force_login(self.student)
        self.client.post(reverse("workshop_enroll", args=[course.pk]))
        self.assertTrue(WorkshopEnrollment.objects.filter(user=self.student, workshop=course).exists())
        self.client.force_login(self.other_student)
        response = self.client.post(reverse("workshop_enroll", args=[course.pk]), follow=True)
        self.assertFalse(WorkshopEnrollment.objects.filter(user=self.other_student, workshop=course).exists())
        self.assertContains(response, "encerradas ou sem vagas")
        self.client.force_login(self.student)
        self.client.post(reverse("workshop_enroll", args=[course.pk]))
        self.assertFalse(WorkshopEnrollment.objects.filter(user=self.student, workshop=course).exists())

    def test_admin_can_create_user_with_contact_email_and_email_login_works(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("admin_user_create"), {
            "identifier": "98765432100",
            "email": "novo.aluno@example.com",
            "nome": "Novo Aluno",
            "perfil_acesso": User.Role.STUDENT,
            "area_interesse": "Engenharia",
            "escola": self.school.pk,
            "turma": self.classroom.pk,
            "competencias": "organização",
            "senha_temporaria": "senha-temporaria",
            "is_active": "on",
        })
        self.assertEqual(response.status_code, 302)
        account = User.objects.get(identifier="98765432100")
        self.assertEqual(account.email, "novo.aluno@example.com")
        self.client.logout()
        response = self.client.post(reverse("login_aluno"), {
            "identifier": "novo.aluno@example.com", "senha": "senha-temporaria",
        })
        self.assertRedirects(response, reverse("dashboard"))

    def test_admin_cannot_delete_own_account(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("admin_user_delete", args=[self.admin.pk]), follow=True)
        self.assertTrue(User.objects.filter(pk=self.admin.pk).exists())
        self.assertContains(response, "não pode ser excluído")

    def test_admin_manages_course_and_preserves_enrollment_history_on_delete(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("admin_workshop_create"), {
            "titulo": "Preparação para entrevistas",
            "area": "Psicologia",
            "status": Workshop.Status.PUBLISHED,
            "data": (timezone.now() + timedelta(days=5)).strftime("%Y-%m-%dT%H:%M"),
            "duracao_minutos": 90,
            "modalidade": Workshop.Modality.HYBRID,
            "local": "Sala 3",
            "descricao": "Simulações orientadas",
            "vagas": 20,
            "mentor": self.teacher.pk,
        })
        course = Workshop.objects.get(titulo="Preparação para entrevistas")
        self.assertRedirects(response, reverse("admin_workshop_detail", args=[course.pk]))
        WorkshopEnrollment.objects.create(user=self.student, workshop=course)
        response = self.client.post(reverse("admin_workshop_delete", args=[course.pk]), follow=True)
        course.refresh_from_db()
        self.assertEqual(course.status, Workshop.Status.CANCELLED)
        self.assertTrue(course.inscricoes.filter(user=self.student).exists())
        self.assertContains(response, "foi cancelado")

    def test_admin_updates_safe_report_to_in_progress(self):
        report = SafeReport.objects.create(mensagem="teste")
        self.client.force_login(self.admin)
        response = self.client.post(reverse("admin_safe_report_toggle", args=[report.pk]), {"status": SafeReport.Status.IN_PROGRESS})
        self.assertRedirects(response, reverse("admin_dashboard") + "#acolhimento")
        report.refresh_from_db()
        self.assertEqual(report.status, SafeReport.Status.IN_PROGRESS)
        self.assertFalse(report.tratado)

    def test_student_can_edit_and_delete_only_own_project(self):
        project = StudentProject.objects.create(
            aluno=self.student, titulo="Meu projeto", area="Educação", resumo="Versão inicial",
        )
        other_project = StudentProject.objects.create(
            aluno=self.other_student, titulo="Projeto alheio", area="Educação", resumo="Privado",
        )
        self.client.force_login(self.student)
        response = self.client.post(reverse("project_edit", args=[project.pk]), {
            "titulo": "Meu projeto atualizado", "area": "Educação", "resumo": "Nova versão",
            "status": StudentProject.Status.DESENVOLVIMENTO,
        })
        self.assertRedirects(response, reverse("dashboard"))
        project.refresh_from_db()
        self.assertEqual(project.titulo, "Meu projeto atualizado")
        self.assertEqual(self.client.post(reverse("project_delete", args=[other_project.pk])).status_code, 404)
        self.client.post(reverse("project_delete", args=[project.pk]))
        self.assertFalse(StudentProject.objects.filter(pk=project.pk).exists())
