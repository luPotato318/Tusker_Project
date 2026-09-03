"""
Módulo de Versionamento Oficial do PIEM Tusker Power
"""

VERSION = "3.1.0"
BUILD_NUMBER = "20260831.2"
RELEASE_NAME = "Operational Command"
RELEASE_DATE = "31/08/2026"
EDITION = "Tusker Power Enterprise Edition"

CHANGELOG_SUMMARY = [
    {
        "version": "3.1.0",
        "date": "31/08/2026",
        "title": "Operational Command",
        "highlights": [
            "Catálogo público e pesquisável de cursos com filtros por área e modalidade.",
            "Gestão administrativa de usuários, e-mails, permissões, status e exclusão protegida.",
            "Ciclo completo de cursos: rascunho, publicação, edição, vagas, inscritos, cancelamento e exclusão.",
            "Inscrições com prazo, capacidade transacional e preservação do histórico.",
            "Edição e exclusão de projetos pelo estudante, novo fluxo de acolhimento e testes ampliados.",
        ],
    },
    {
        "version": "3.0.0",
        "date": "31/08/2026",
        "title": "Enterprise Horizon",
        "highlights": [
            "Portais segregados para aluno, professor, administrador e recrutador com RBAC.",
            "Score de Empregabilidade 0–1000, ranking seletivo e vitrine anônima de talentos.",
            "Desafios, correção docente, soft skills, vagas, candidaturas e currículo PDF validável.",
            "Tutor PIEM 2.0 com persistência e fallback OpenAI, Gemini, Anthropic e modo local.",
            "Multi-tenancy escolar, trilha de auditoria, relatórios e Canal Seguro cifrado.",
        ],
    },
    {
        "version": "2.2.0",
        "date": "27/08/2026",
        "title": "Apex Evolution Release",
        "highlights": [
            "Refatoração do visual com Glassmorphism, gradientes e micro-animações.",
            "Separação completa dos portais de login para Alunos e Administradores.",
            "Novo Painel Administrativo (/painel/admin/) para controle de usuários e oficinas.",
            "Evolução do Tutor PIEM com recomendador de oficinas e gerador de tarefas práticas.",
            "Suporte nativo a PostgreSQL, documentação Supabase e conector PHP.",
            "Sistema de versionamento integrado em toda a aplicação."
        ]
    },
    {
        "version": "2.1.2",
        "date": "15/07/2026",
        "title": "Tusker Power Initial Release",
        "highlights": [
            "Painel de controle de frequência com cálculo de risco prudencial.",
            "Vitrine pública de projetos com certificados com QR Code em tempo real.",
            "Canal seguro de relatos de apoio escolar."
        ]
    }
]

def get_version_info():
    return {
        "version": VERSION,
        "build": BUILD_NUMBER,
        "release_name": RELEASE_NAME,
        "release_date": RELEASE_DATE,
        "edition": EDITION,
        "changelog": CHANGELOG_SUMMARY,
    }
