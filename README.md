<<<<<<< HEAD
# PIEM Tusker Power 3.1 — Operational Command

Plataforma Django para inserção de estudantes do 3º ano no mercado de trabalho. A versão 3.1 completa a operação dos quatro portais RBAC e transforma o painel do gestor em uma central funcional de usuários, e-mails, cursos, inscrições e acolhimento.

## Entregas principais

- Score de Empregabilidade transparente (0–1000) por frequência, soft skills e entregas.
- Portal do professor em `/painel/professor/`, com desafios, correção, feedback e risco escolar.
- Portal corporativo em `/painel/recrutador/`, com vitrine anônima consentida e vagas.
- Currículo PDF com QR e assinatura de validação, certificados e relatórios JSON/XLSX/PDF.
- Tutor PIEM 2.0 com histórico e fallback OpenAI → Gemini → Anthropic → orientação local.
- Escolas e turmas para segmentação, auditoria de ações sensíveis e Canal Seguro cifrado em repouso.
- Imagens contextuais via Unsplash/Pexels, cache de 24 horas e fallback automático.
- Catálogo público em `/cursos/`, com busca, filtros, prazo e controle transacional de vagas.
- CRUD administrativo de usuários e cursos, preservação de histórico e trilha de auditoria.
- Pasta `versionamento/` com notas completas das versões 2.1.2, 2.2.0, 3.0.0 e 3.1.0.

## Rodar localmente

Requer Python 3.11 ou superior.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt / pip install psycopg2-binary --only-binary :all:
Copy-Item .env.example .env
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Ao atualizar uma instalação 3.0 existente, execute obrigatoriamente `python manage.py migrate`. A migração 0004 adiciona e-mails de contato e os novos campos operacionais de cursos sem apagar os registros atuais.

Acesse `http://127.0.0.1:8000/`. Contas demonstrativas criadas por `seed_data` usam a senha `senha123`:

- Aluno: `12345678900`
- Professor: `professor@piem.edu.br`
- Recrutador: `talentos@empresa.com`

Crie o administrador com `python manage.py createsuperuser`. Contas de professor e recrutador são provisionadas por gestores; o cadastro público cria somente estudantes.

## Configuração

Copie `.env.example` e preencha apenas os serviços utilizados. Sem chaves de LLM ou imagem, a aplicação continua funcional em modo local. Para produção, configure PostgreSQL/Supabase, Redis, uma `SECRET_KEY` exclusiva e uma chave Fernet em `SAFE_REPORT_ENCRYPTION_KEY`.

O Canal Seguro é cifrado no navegador-servidor via HTTPS em produção e cifrado em repouso no banco. A chave deve ser mantida fora do repositório e gerenciada pelo ambiente de implantação.

## Qualidade

```powershell
python manage.py check
python manage.py test
python manage.py makemigrations --check
```