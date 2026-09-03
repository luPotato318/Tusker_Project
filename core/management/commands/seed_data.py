# pyrefly: ignore [missing-import]
from django.core.management.base import BaseCommand
# pyrefly: ignore [missing-import]
from django.utils import timezone
from datetime import timedelta
from core.models import (
    Attendance, Certificate, ChallengeSubmission, JobOpportunity, PracticalChallenge,
    School, SchoolClass, SoftSkillAssessment, StudentProject, User, Workshop,
)

class Command(BaseCommand):
    help = "Popula o banco de dados com dados demonstrativos para o PIEM"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Iniciando população de dados demonstrativos do PIEM..."))

        # 1. Usuários
        aluno, created = User.objects.get_or_create(
            identifier="12345678900",
            defaults={
                "nome": "Lucas Polidori",
                "perfil_acesso": User.Role.STUDENT,
                "area_interesse": "Tecnologia da Informação",
            }
        )
        if created:
            aluno.set_password("senha123")
            aluno.save()
            self.stdout.write(f"Criado usuário aluno: {aluno.nome} (CPF: 12345678900 / Senha: senha123)")

        aluno2, created2 = User.objects.get_or_create(
            identifier="aluno@piem.edu.br",
            defaults={
                "nome": "Mariana Silva",
                "perfil_acesso": User.Role.STUDENT,
                "area_interesse": "Engenharia",
            }
        )
        if created2:
            aluno2.set_password("senha123")
            aluno2.save()

        escola, _ = School.objects.get_or_create(codigo="senai-tusker", defaults={"nome": "Escola SENAI Tusker", "cidade": "São Paulo", "estado": "SP"})
        turma, _ = SchoolClass.objects.get_or_create(escola=escola, nome="3º A", ano_letivo=2026)
        aluno.escola = escola
        aluno.turma = turma
        aluno.competencias = "Python, Django, comunicação, resolução de problemas"
        aluno.consentimento_vitrine = True
        aluno.save()
        aluno2.escola = escola
        aluno2.turma = turma
        aluno2.competencias = "prototipagem, trabalho em equipe, sustentabilidade"
        aluno2.consentimento_vitrine = True
        aluno2.save()

        mentor, created_m = User.objects.get_or_create(
            identifier="professor@piem.edu.br",
            defaults={
                "nome": "Prof. Roberto Mendes",
                "perfil_acesso": User.Role.TEACHER,
                "area_interesse": "Tecnologia da Informação",
                "escola": escola,
            }
        )
        if created_m:
            mentor.set_password("senha123")
            mentor.save()
        turma.professores.add(mentor)

        recruiter, created_r = User.objects.get_or_create(
            identifier="talentos@empresa.com",
            defaults={"nome": "Empresa Parceira PIEM", "perfil_acesso": User.Role.RECRUITER, "escola": escola},
        )
        if created_r:
            recruiter.set_password("senha123")
            recruiter.save()

        # 2. Frequências para o aluno teste
        hoje = timezone.localdate()
        for i in range(20):
            data_freq = hoje - timedelta(days=i)
            # Simular 90% de presença (2 faltas em 20 dias)
            presente = i not in (3, 11)
            Attendance.objects.get_or_create(
                user=aluno,
                data=data_freq,
                defaults={"presente": presente}
            )

        # 3. Oficinas Demonstrativas
        oficinas_data = [
            {
                "titulo": "Desenvolvimento Web & Inteligência Artificial",
                "area": "Tecnologia da Informação",
                "descricao": "Aprenda a construir soluções full-stack com Django e integrar agentes autônomos de IA.",
                "dias": 3,
                "vagas": 25,
            },
            {
                "titulo": "Introdução à Robótica e Mecatrônica",
                "area": "Engenharia",
                "descricao": "Prática com controladores, sensores e automação de protótipos em escala.",
                "dias": 7,
                "vagas": 20,
            },
            {
                "titulo": "Empreendedorismo Social e Modelagem de Negócios",
                "area": "Empreendedorismo",
                "descricao": "Valide ideias com impacto social, crie canvas de negócios e estruture pitches.",
                "dias": 12,
                "vagas": 30,
            },
            {
                "titulo": "Comunicação Eficiente e Oratória para Mercado",
                "area": "Educação",
                "descricao": "Técnicas de expressão oral, apresentações de projetos e entrevistas corporativas.",
                "dias": 15,
                "vagas": 35,
            },
            {
                "titulo": "Saúde Mental e Gestão de Rotina Acadêmica",
                "area": "Psicologia",
                "descricao": "Estratégias de autocuidado, equilíbrio emocional e hábitos de estudo saudáveis.",
                "dias": 18,
                "vagas": 40,
            },
            {
                "titulo": "Design Gráfico e UI/UX no Figma",
                "area": "Arte",
                "descricao": "Criação de marcas, interfaces de sistemas e prototipagem de produtos digitais.",
                "dias": 22,
                "vagas": 25,
            },
        ]

        for item in oficinas_data:
            data_oficina = timezone.now() + timedelta(days=item["dias"])
            Workshop.objects.get_or_create(
                titulo=item["titulo"],
                defaults={
                    "area": item["area"],
                    "data": data_oficina,
                    "mentor": mentor,
                    "escola": escola,
                    "descricao": item["descricao"],
                    "vagas": item["vagas"],
                }
            )

        # 4. Projetos Estudantis em Destaque na Vitrine
        p1, _ = StudentProject.objects.get_or_create(
            titulo="Sistema Integrado de Monitoramento Hídrico Comunitário",
            defaults={
                "aluno": aluno,
                "area": "Engenharia",
                "resumo": "Protótipo IoT de baixo custo para medição de qualidade e vazão da água em comunidades rurais.",
                "status": StudentProject.Status.CONCLUIDO,
                "publico": True,
                "destaque": True,
                "link_projeto": "https://github.com/exemplo/hidro-monitor",
                "link_github": "https://github.com/exemplo/hidro-monitor",
            }
        )
        Certificate.objects.get_or_create(aluno=aluno, projeto=p1)

        p2, _ = StudentProject.objects.get_or_create(
            titulo="Portal de Mentoria Estudantil PIEM (Tusker Power)",
            defaults={
                "aluno": aluno,
                "area": "Tecnologia da Informação",
                "resumo": "Plataforma web para conectar estudantes a mentores corporativos com tutor de inteligência artificial.",
                "status": StudentProject.Status.CONCLUIDO,
                "publico": True,
                "destaque": True,
                "link_projeto": "https://github.com/exemplo/piem-tusker",
                "link_github": "https://github.com/exemplo/piem-tusker",
            }
        )
        Certificate.objects.get_or_create(aluno=aluno, projeto=p2)

        StudentProject.objects.get_or_create(
            titulo="Aplicativo de Apoio Emocional e Acolhimento Jovem",
            defaults={
                "aluno": aluno2,
                "area": "Psicologia",
                "resumo": "Interface segura para registro diário de sentimentos e solicitação discreta de apoio psicossocial.",
                "status": StudentProject.Status.DESENVOLVIMENTO,
                "publico": True,
                "destaque": False,
                "link_projeto": "",
                "link_github": "",
            }
        )

        challenge, _ = PracticalChallenge.objects.get_or_create(
            titulo="Pitch profissional de 90 segundos",
            turma=turma,
            defaults={"descricao": "Apresente um problema, sua solução e a contribuição pessoal de forma objetiva.", "area": "Educação", "pontos": 120, "prazo": timezone.now() + timedelta(days=8), "criado_por": mentor},
        )
        submission, _ = ChallengeSubmission.objects.get_or_create(
            desafio=challenge,
            aluno=aluno,
            defaults={"resposta": "Estruturei meu pitch em contexto, ação e resultado, destacando o monitoramento hídrico.", "status": ChallengeSubmission.Status.APPROVED, "pontos_atribuidos": 108, "feedback": "Boa clareza. Quantifique melhor o impacto na próxima versão.", "avaliado_por": mentor, "avaliado_em": timezone.now()},
        )
        SoftSkillAssessment.objects.get_or_create(
            aluno=aluno,
            avaliador=mentor,
            defaults={"comunicacao": 4, "proatividade": 5, "trabalho_equipe": 4, "feedback": "Demonstra autonomia e acolhe feedback."},
        )
        JobOpportunity.objects.get_or_create(
            titulo="Jovem Aprendiz em Tecnologia",
            empresa="Tusker Tech",
            defaults={"descricao": "Apoio a projetos digitais, testes e documentação com mentoria de carreira.", "competencias": "comunicação, lógica, colaboração", "modalidade": "Híbrido", "tipo": JobOpportunity.Type.APPRENTICE, "localidade": "São Paulo/SP", "publicada_por": recruiter, "escola": escola},
        )

        self.stdout.write(self.style.SUCCESS("Massa de dados demonstrativa gerada com sucesso!"))
