from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import (
    Attendance, AuditLog, Certificate, ChallengeSubmission, ChatMessage, ChatSession,
    JobApplication, JobOpportunity, MentorshipSession, PracticalChallenge, SafeReport,
    School, SchoolClass, SoftSkillAssessment, StudentProject, User, Workshop,
    WorkshopEnrollment,
)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("identifier",)
    list_display = ("identifier", "email", "nome", "perfil_acesso", "escola", "turma", "is_active")
    list_filter = ("perfil_acesso", "escola", "is_active")
    search_fields = ("identifier", "email", "nome")
    fieldsets = (
        (None, {"fields": ("identifier", "password")}),
        ("Perfil PIEM", {"fields": ("nome", "email", "perfil_acesso", "area_interesse", "escola", "turma", "biografia", "competencias", "linkedin_url", "consentimento_vitrine")}),
        ("Permissões", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("identifier", "email", "nome", "perfil_acesso", "password1", "password2")}),)


@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = ("titulo", "area", "data", "status", "modalidade", "vagas", "vagas_restantes")
    list_filter = ("status", "modalidade", "area", "escola")
    search_fields = ("titulo", "descricao", "local")
    date_hierarchy = "data"


for model in (
    School, SchoolClass, WorkshopEnrollment, Attendance, StudentProject, Certificate,
    PracticalChallenge, ChallengeSubmission, SoftSkillAssessment, JobOpportunity, JobApplication,
    MentorshipSession, ChatSession, ChatMessage, SafeReport, AuditLog,
):
    admin.site.register(model)

admin.site.site_header = "PIEM Enterprise — Administração"
admin.site.site_title = "PIEM 3.1"
