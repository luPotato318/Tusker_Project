import base64
import hashlib
import json

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.db.models import Avg, Sum

from .models import AuditLog, ChallengeSubmission, SoftSkillAssessment, User


def _cipher():
    configured = getattr(settings, "SAFE_REPORT_ENCRYPTION_KEY", "")
    if configured:
        key = configured.encode()
    else:
        key = base64.urlsafe_b64encode(hashlib.sha256(settings.SECRET_KEY.encode()).digest())
    return Fernet(key)


def encrypt_sensitive(value):
    if not value:
        return ""
    return "enc:v1:" + _cipher().encrypt(value.encode()).decode()


def decrypt_sensitive(value):
    if not value or not value.startswith("enc:v1:"):
        return value or ""
    try:
        return _cipher().decrypt(value[7:].encode()).decode()
    except (InvalidToken, ValueError):
        return "[conteúdo indisponível: chave de proteção divergente]"


def client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    return forwarded.split(",")[0].strip() or request.META.get("REMOTE_ADDR")


def audit(request, action, instance=None, details=None):
    return AuditLog.objects.create(
        ator=request.user if getattr(request, "user", None) and request.user.is_authenticated else None,
        acao=action,
        entidade=instance.__class__.__name__ if instance else "Sistema",
        entidade_id=str(getattr(instance, "pk", "")),
        detalhes=details or {},
        ip=client_ip(request),
    )


def employability_score(student):
    """Score transparente de 0–1000: frequência 35%, soft skills 30%, entregas 35%."""
    attendances = student.frequencias.all()
    total_attendance = attendances.count()
    attendance_ratio = attendances.filter(presente=True).count() / total_attendance if total_attendance else 0

    soft = SoftSkillAssessment.objects.filter(aluno=student).aggregate(
        comunicacao=Avg("comunicacao"),
        proatividade=Avg("proatividade"),
        equipe=Avg("trabalho_equipe"),
    )
    soft_values = [value for value in soft.values() if value is not None]
    soft_ratio = (sum(soft_values) / len(soft_values) / 5) if soft_values else 0

    deliveries = ChallengeSubmission.objects.filter(aluno=student)
    awarded = deliveries.aggregate(total=Sum("pontos_atribuidos"))["total"] or 0
    possible = sum(item.desafio.pontos for item in deliveries.select_related("desafio"))
    delivery_ratio = min(1, awarded / possible) if possible else 0

    components = {
        "frequencia": round(attendance_ratio * 350),
        "soft_skills": round(soft_ratio * 300),
        "entregas": round(delivery_ratio * 350),
    }
    score = min(1000, sum(components.values()))
    if score >= 800:
        level = "Pronto para oportunidades"
    elif score >= 550:
        level = "Em aceleração"
    elif score >= 300:
        level = "Em desenvolvimento"
    else:
        level = "Início da jornada"
    return {"score": score, "level": level, "components": components}


def ranked_students(queryset=None):
    students = queryset if queryset is not None else User.objects.filter(perfil_acesso=User.Role.STUDENT)
    ranking = [{"student": student, **employability_score(student)} for student in students]
    ranking.sort(key=lambda item: (-item["score"], item["student"].nome.lower()))
    for position, item in enumerate(ranking, start=1):
        item["position"] = position
    return ranking


def json_report_payload(students):
    return [
        {
            "codigo": item["student"].talent_code,
            "nome": item["student"].nome,
            "escola": item["student"].escola.nome if item["student"].escola else "",
            "turma": item["student"].turma.nome if item["student"].turma else "",
            "score": item["score"],
            "nivel": item["level"],
            **item["components"],
        }
        for item in ranked_students(students)
    ]
