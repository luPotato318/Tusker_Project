import uuid

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone


class School(models.Model):
    nome = models.CharField(max_length=180)
    codigo = models.SlugField(max_length=40, unique=True)
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2, blank=True)
    ativa = models.BooleanField(default=True)

    class Meta:
        ordering = ("nome",)

    def __str__(self):
        return self.nome


class UserManager(BaseUserManager):
    def create_user(self, identifier, password=None, **extra_fields):
        if not identifier:
            raise ValueError("CPF ou e-mail é obrigatório")
        identifier = identifier.strip().lower()
        if "@" in identifier:
            extra_fields.setdefault("email", identifier)
        if extra_fields.get("email"):
            extra_fields["email"] = extra_fields["email"].strip().lower()
        user = self.model(identifier=identifier, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, identifier, password, **extra_fields):
        extra_fields.setdefault("perfil_acesso", User.Role.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(identifier, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        STUDENT = "student", "Aluno"
        TEACHER = "teacher", "Professor / Colaborador"
        ADMIN = "admin", "Administrador"
        RECRUITER = "recruiter", "Recrutador / Empresa"

    identifier = models.CharField("CPF ou e-mail", max_length=150, unique=True)
    email = models.EmailField("E-mail de contato", blank=True, default="")
    nome = models.CharField(max_length=150)
    perfil_acesso = models.CharField(max_length=16, choices=Role.choices, default=Role.STUDENT)
    area_interesse = models.CharField(max_length=100, blank=True, default="Tecnologia da Informação")
    escola = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True, related_name="usuarios")
    turma = models.ForeignKey("SchoolClass", on_delete=models.SET_NULL, null=True, blank=True, related_name="alunos")
    biografia = models.TextField(blank=True)
    competencias = models.CharField(max_length=500, blank=True, help_text="Competências separadas por vírgula")
    linkedin_url = models.URLField(blank=True)
    consentimento_vitrine = models.BooleanField(default=False)
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "identifier"
    REQUIRED_FIELDS = ["nome"]
    objects = UserManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("email",),
                condition=~Q(email=""),
                name="core_user_unique_nonempty_email",
            )
        ]

    @property
    def competencies_list(self):
        return [item.strip() for item in self.competencias.split(",") if item.strip()]

    @property
    def talent_code(self):
        return f"PIEM-{str(self.public_id).split('-')[0].upper()}"

    def __str__(self):
        return f"{self.nome} ({self.identifier})"


class SchoolClass(models.Model):
    escola = models.ForeignKey(School, on_delete=models.CASCADE, related_name="turmas")
    nome = models.CharField(max_length=80)
    ano_letivo = models.PositiveIntegerField(default=2026)
    serie = models.PositiveSmallIntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(3)])
    professores = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="turmas_docentes")

    class Meta:
        ordering = ("-ano_letivo", "nome")
        unique_together = ("escola", "nome", "ano_letivo")

    def __str__(self):
        return f"{self.escola} · {self.nome}/{self.ano_letivo}"


class Workshop(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Rascunho"
        PUBLISHED = "published", "Publicado"
        CANCELLED = "cancelled", "Cancelado"
        COMPLETED = "completed", "Concluído"

    class Modality(models.TextChoices):
        ONSITE = "onsite", "Presencial"
        ONLINE = "online", "On-line"
        HYBRID = "hybrid", "Híbrido"

    AREAS = [(x, x) for x in [
        "Tecnologia da Informação", "Psicologia", "Saúde", "Engenharia", "Educação",
        "Arte", "Ciência", "Empreendedorismo", "Educação Física", "Nutrição",
        "Medicina Veterinária", "Inglês",
    ]]
    titulo = models.CharField(max_length=160)
    area = models.CharField(max_length=100, choices=AREAS)
    data = models.DateTimeField()
    mentor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="oficinas")
    escola = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True, related_name="oficinas")
    descricao = models.TextField()
    vagas = models.PositiveIntegerField(default=30)
    imagem_query = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PUBLISHED)
    modalidade = models.CharField(max_length=12, choices=Modality.choices, default=Modality.ONSITE)
    local = models.CharField(max_length=180, blank=True)
    duracao_minutos = models.PositiveSmallIntegerField(
        default=120,
        validators=[MinValueValidator(30), MaxValueValidator(600)],
    )
    inscricoes_ate = models.DateTimeField(null=True, blank=True)
    class Meta:
        ordering = ("data", "titulo")

    def __str__(self):
        return self.titulo

    @property
    def vagas_restantes(self):
        return max(0, self.vagas - self.inscricoes.count())

    @property
    def aceita_inscricoes(self):
        now = timezone.now()
        prazo_aberto = not self.inscricoes_ate or self.inscricoes_ate >= now
        return (
            self.status == self.Status.PUBLISHED
            and self.data >= now
            and prazo_aberto
            and self.vagas_restantes > 0
        )


class WorkshopEnrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="inscricoes_oficinas")
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, related_name="inscricoes")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "workshop")

    def __str__(self):
        return f"{self.user.nome} -> {self.workshop.titulo}"


class Attendance(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="frequencias")
    data = models.DateField(default=timezone.localdate)
    presente = models.BooleanField(default=True)
    registrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="frequencias_registradas")

    class Meta:
        unique_together = ("user", "data")


class StudentProject(models.Model):
    class Status(models.TextChoices):
        IDEIA = "ideia", "Ideia"
        DESENVOLVIMENTO = "desenvolvimento", "Em desenvolvimento"
        CONCLUIDO = "concluido", "Concluído"

    aluno = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projetos")
    titulo = models.CharField(max_length=160)
    area = models.CharField(max_length=100, choices=Workshop.AREAS)
    resumo = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IDEIA)
    publico = models.BooleanField(default=False)
    link_projeto = models.URLField("Link do Protótipo", blank=True, default="")
    link_github = models.URLField("Repositório / Documentação", blank=True, default="")
    destaque = models.BooleanField("Destaque na Vitrine", default=False)
    updated_at = models.DateTimeField(auto_now=True)


class Certificate(models.Model):
    aluno = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="certificados")
    projeto = models.OneToOneField(StudentProject, on_delete=models.CASCADE, related_name="certificado")
    codigo = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    emitido_em = models.DateTimeField(auto_now_add=True)


class PracticalChallenge(models.Model):
    titulo = models.CharField(max_length=180)
    descricao = models.TextField()
    area = models.CharField(max_length=100, choices=Workshop.AREAS)
    pontos = models.PositiveSmallIntegerField(default=100, validators=[MinValueValidator(1), MaxValueValidator(350)])
    prazo = models.DateTimeField(null=True, blank=True)
    turma = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, null=True, blank=True, related_name="desafios")
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="desafios_criados")
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("prazo", "-criado_em")

    def __str__(self):
        return self.titulo


class ChallengeSubmission(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Aguardando correção"
        REVISION = "revision", "Revisão solicitada"
        APPROVED = "approved", "Aprovado"

    desafio = models.ForeignKey(PracticalChallenge, on_delete=models.CASCADE, related_name="entregas")
    aluno = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="entregas_desafios")
    resposta = models.TextField()
    anexo_url = models.URLField(blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    pontos_atribuidos = models.PositiveSmallIntegerField(default=0)
    feedback = models.TextField(blank=True)
    avaliado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="entregas_avaliadas")
    enviado_em = models.DateTimeField(auto_now_add=True)
    avaliado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-enviado_em",)
        unique_together = ("desafio", "aluno")


class SoftSkillAssessment(models.Model):
    aluno = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="avaliacoes_soft_skills")
    avaliador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="soft_skills_avaliadas")
    comunicacao = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    proatividade = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    trabalho_equipe = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    feedback = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-criado_em",)

    @property
    def media(self):
        return round((self.comunicacao + self.proatividade + self.trabalho_equipe) / 3, 2)


class JobOpportunity(models.Model):
    class Type(models.TextChoices):
        APPRENTICE = "apprentice", "Jovem Aprendiz"
        INTERNSHIP = "internship", "Estágio"
        ENTRY = "entry", "Primeiro emprego"

    titulo = models.CharField(max_length=180)
    empresa = models.CharField(max_length=160)
    descricao = models.TextField()
    competencias = models.CharField(max_length=500, blank=True)
    modalidade = models.CharField(max_length=20, default="Presencial")
    tipo = models.CharField(max_length=16, choices=Type.choices, default=Type.APPRENTICE)
    localidade = models.CharField(max_length=140, blank=True)
    publicada_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="vagas_publicadas")
    escola = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True, related_name="vagas")
    ativa = models.BooleanField(default=True)
    criada_em = models.DateTimeField(auto_now_add=True)
    encerra_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-criada_em",)


class JobApplication(models.Model):
    class Stage(models.TextChoices):
        APPLIED = "applied", "Candidatura enviada"
        SCREENING = "screening", "Triagem"
        INTERVIEW = "interview", "Entrevista"
        OFFER = "offer", "Proposta"
        HIRED = "hired", "Contratado"
        REJECTED = "rejected", "Encerrado"

    vaga = models.ForeignKey(JobOpportunity, on_delete=models.CASCADE, related_name="candidaturas")
    aluno = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="candidaturas")
    etapa = models.CharField(max_length=16, choices=Stage.choices, default=Stage.APPLIED)
    carta_apresentacao = models.TextField(blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-atualizada_em",)
        unique_together = ("vaga", "aluno")


class MentorshipSession(models.Model):
    titulo = models.CharField(max_length=180)
    mentor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="mentorias_conduzidas")
    aluno = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mentorias")
    inicio = models.DateTimeField()
    duracao_minutos = models.PositiveSmallIntegerField(default=45)
    link_reuniao = models.URLField(blank=True)
    observacoes = models.TextField(blank=True)
    confirmada = models.BooleanField(default=False)

    class Meta:
        ordering = ("inicio",)


class ChatSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sessoes_tutor")
    titulo = models.CharField(max_length=120, default="Conversa com Tutor PIEM")
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)


class ChatMessage(models.Model):
    class Role(models.TextChoices):
        USER = "user", "Usuário"
        ASSISTANT = "assistant", "Tutor"

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="mensagens")
    role = models.CharField(max_length=12, choices=Role.choices)
    content = models.TextField()
    provider = models.CharField(max_length=24, blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("criada_em",)


class SafeReport(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Recebido"
        IN_PROGRESS = "in_progress", "Em acolhimento"
        RESOLVED = "resolved", "Resolvido"

    protocolo = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    escola = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True, related_name="relatos")
    categoria = models.CharField(max_length=80, default="Acolhimento")
    mensagem = models.TextField(help_text="Conteúdo cifrado em repouso")
    contato_seguro = models.TextField(blank=True, help_text="Conteúdo cifrado em repouso")
    criado_em = models.DateTimeField(auto_now_add=True)
    tratado = models.BooleanField(default=False)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)


class AuditLog(models.Model):
    ator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="auditorias")
    acao = models.CharField(max_length=80)
    entidade = models.CharField(max_length=80)
    entidade_id = models.CharField(max_length=64, blank=True)
    detalhes = models.JSONField(default=dict, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-criado_em",)
