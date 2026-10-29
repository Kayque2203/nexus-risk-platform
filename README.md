# NEXUS — Intelligent Process & Risk Platform

![CI](https://github.com/Kayque2203/nexus-risk-platform/actions/workflows/ci.yml/badge.svg)

Plataforma inteligente de gestão de processos e riscos corporativos, com cálculo automático de severidade, autenticação segura e trilha de auditoria completa.

> Projeto de portfólio construído do zero, incluindo diagnóstico de ambiente restrito, arquitetura adaptativa, backend, frontend e testes automatizados.

> **Demo ao vivo:** https://nexus-frontend-m1gb.onrender.com
> O backend está no plano gratuito do Render, então a primeira visita pode levar cerca de 1 minuto para responder (cold start).

## 📸 Screenshots

<table>
  <tr>
    <td><strong>Login</strong></td>
    <td><strong>Dashboard</strong></td>
  </tr>
  <tr>
    <td><img src="docs/screenshots/login.png" width="400"/></td>
    <td><img src="docs/screenshots/dashboard.png" width="400"/></td>
  </tr>
  <tr>
    <td colspan="2" align="center"><strong>Gestão de riscos com severidade calculada automaticamente</strong></td>
  </tr>
  <tr>
    <td colspan="2"><img src="docs/screenshots/riscos.png" width="820"/></td>
  </tr>
</table>

## 🎯 Problema

Ambientes corporativos lidam constantemente com processos operacionais e os riscos associados a eles — prazos, responsáveis, prioridades, e a necessidade de identificar rapidamente onde estão as maiores ameaças. Sem uma ferramenta centralizada, essa informação fica dispersa em planilhas, sem cálculo consistente de severidade e sem rastreabilidade de quem alterou o quê.

## 💡 Solução

O NEXUS centraliza processos e riscos em uma única plataforma, com:

- **Cálculo automático de severidade** via matriz de risco (Probabilidade × Impacto), eliminando julgamento manual inconsistente
- **Autenticação JWT** e controle de acesso
- **Trilha de auditoria** completa — toda criação, edição e exclusão é registrada com autor, data e o que mudou
- **Dashboard visual** com indicadores em tempo real e destaque automático para riscos críticos
- **API REST documentada** (OpenAPI/Swagger), pronta para integrações futuras

## 🏗️ Arquitetura

```mermaid
flowchart TD
    subgraph Client["Frontend"]
        UI[HTML + CSS + JavaScript ES Modules]
    end

    subgraph Server["Backend — FastAPI"]
        API[API REST]
        AUTH[Autenticação JWT]
        PROC[Processos]
        RISK[Riscos]
        ENGINE[Risk Engine]
        AUDIT[Audit Trail]
    end

    subgraph Data["Persistência"]
        DB[(SQLite via SQLAlchemy)]
    end

    UI -- fetch/JSON --> API
    API --> AUTH
    API --> PROC
    API --> RISK
    RISK --> ENGINE
    API --> AUDIT
    AUTH --> DB
    PROC --> DB
    RISK --> DB
    AUDIT --> DB
```

A aplicação segue arquitetura em camadas (API → Service → Repository → Model), separando claramente regras de negócio, acesso a dados e apresentação. Essa separação permite trocar o banco de dados (SQLite → PostgreSQL) sem reescrever a lógica de negócio.

### Uma nota sobre as decisões técnicas

Este projeto foi desenvolvido em um **ambiente corporativo com restrições reais**: sem Node.js, sem Docker, sem PostgreSQL, e com políticas de execução (AppLocker) bloqueando até mesmo binários instalados via `pip` em alguns casos. Em vez de contornar essas restrições, a arquitetura foi adaptada para funcionar dentro delas — o que resultou em decisões deliberadas, documentadas ao longo do código:

- **Backend em Python/FastAPI** (não Node/NestJS) — único runtime confirmado disponível
- **Frontend sem build step** (HTML/CSS/JS puro com ES Modules, servido via `python -m http.server`) — sem depender de Node/npm
- **SQLite com SQLAlchemy + Alembic** — abstração que permite migrar para PostgreSQL trocando apenas a connection string

## ✨ Funcionalidades

- Autenticação JWT com hash de senha (bcrypt)
- CRUD completo de Processos (nome, categoria, departamento, status, prioridade, prazo)
- CRUD completo de Riscos, vinculados a processos
- **Risk Engine**: cálculo automático de severidade via matriz Probabilidade × Impacto (baseada em princípios da ISO 31000)
- Recálculo automático de severidade ao atualizar probabilidade/impacto
- **AI Risk Analyzer**: análise de texto livre para sugestão automática de categoria, probabilidade, impacto e severidade — arquitetura desacoplada de qualquer API externa de IA, com fallback seguro
- Dashboard com indicadores (processos ativos, atrasados, riscos críticos) e badges visuais de severidade
- Trilha de auditoria (quem, quando, o quê mudou) para toda ação de escrita
- 43 testes automatizados (unitários e de integração)

## 🛠️ Stack técnica

**Backend:** Python, FastAPI, SQLAlchemy, Alembic, python-jose (JWT), passlib (bcrypt), Pydantic

**Frontend:** HTML5, CSS3, JavaScript (ES Modules) — sem framework/bundler

**Banco de dados:** SQLite (desenvolvimento), com caminho de migração para PostgreSQL

**Testes:** pytest, httpx, pytest-cov

## 📦 Estrutura do projeto

nexus/

├── backend/

│   ├── app/

│   │   ├── main.py

│   │   ├── core/          # configurações, segurança/JWT

│   │   ├── db/             # engine, sessão, base do SQLAlchemy

│   │   ├── models/         # entidades (User, Process, Risk, AuditLog)

│   │   ├── schemas/        # validação Pydantic

│   │   ├── repositories/   # acesso a dados

│   │   ├── services/       # regras de negócio (inclui o Risk Engine)

│   │   └── api/v1/         # rotas HTTP

│   ├── tests/

│   └── alembic/            # migrations versionadas

├── frontend/

│   ├── index.html          # login

│   ├── app.html            # dashboard

│   ├── processes.html

│   ├── risks.html

│   └── src/

│       ├── api/            # cliente HTTP

│       ├── pages/          # lógica de cada tela

│       └── styles/

└── docs/

├── ARCHITECTURE.md

└── screenshots/

## 🚀 Como executar

### Pré-requisitos

- Python 3.11+

### Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt

# Configurar variáveis de ambiente
copy .env.example .env      # Windows
cp .env.example .env         # Linux/Mac
# Edite o .env e defina uma SECRET_KEY própria

# Rodar migrations
python -m alembic upgrade head

# Iniciar o servidor
python -m uvicorn app.main:app --reload
```

A API estará em `http://127.0.0.1:8000`, com documentação interativa em `http://127.0.0.1:8000/docs`.

### Frontend

Em outro terminal:

```bash
cd frontend
python -m http.server 5500
```

Acesse `http://127.0.0.1:5500`.

### Dados de demonstração

O script `backend/seed_demo.py` popula uma API em execução (local ou publicada) com 8 processos de qualidade e compliance, 15 riscos e 14 ações, todos sintéticos. Como usa a própria API, a severidade vem do Risk Engine e a auditoria é registrada.

```bash
cd backend
python seed_demo.py                         # usa a API padrão
python seed_demo.py http://127.0.0.1:8000   # ou informe outra URL
```

O script pede e-mail e senha e é idempotente por processo (pula os que já existem).

## 🗄️ Banco de dados

O desenvolvimento local usa SQLite, e a produção usa PostgreSQL no Neon. Todo o acesso a dados passa pelo SQLAlchemy, então a troca de banco exige apenas alterar a variável `DATABASE_URL` (com o prefixo `postgresql+psycopg://` para PostgreSQL) e rodar `alembic upgrade head`.

## 🧪 Testes

```bash
cd backend
python -m pytest -v
```

São 43 testes automatizados (autenticação, processos, riscos e análise de IA), executados a cada push pelo GitHub Actions. Cobrem CRUD, regras de negócio (e-mail duplicado, processo inexistente) e a matriz completa do Risk Engine via `@pytest.mark.parametrize`. Os testes usam um SQLite isolado, independente do `.env`.

Documentação completa e interativa em `/docs` (Swagger UI).

## 📋 API — principais endpoints

| Método      | Endpoint                | Descrição                      |
| ------------ | ----------------------- | -------------------------------- |
| POST         | `/api/auth/login`     | Login (retorna JWT)              |
| GET          | `/api/users/me`       | Usuário autenticado             |
| GET/POST     | `/api/processes/`     | Listar/criar processos           |
| PATCH/DELETE | `/api/processes/{id}` | Atualizar/excluir processo       |
| GET/POST     | `/api/risks/`         | Listar/criar riscos              |
| PATCH/DELETE | `/api/risks/{id}`     | Atualizar/excluir risco          |
| GET          | `/api/dashboard/`     | Indicadores agregados            |
| GET          | `/api/audit-logs/`    | Trilha de auditoria              |
| POST         | `/api/ai/analyze`     | Análise de risco por texto (IA) |

## ☁️ Hospedagem

| Componente | Serviço |
| ---------- | ------- |
| Frontend (estático, sem build) | Render Static Site |
| Backend (FastAPI) | Render Web Service (plano Free) |
| Banco de dados | Neon (PostgreSQL, região São Paulo) |

> **Cold start:** no plano gratuito o backend hiberna após cerca de 15 minutos sem acesso. A primeira requisição pode levar de 30 a 60 segundos.

## 🔐 Segurança e limitações conhecidas

- O cadastro de usuários (`POST /api/users/`) é público, escolha consciente para um projeto de portfólio. Em um cenário real seria restrito a administradores.
- O JWT fica em `localStorage` e o logout é apenas no cliente (trade-off do modelo stateless).
- A autorização é binária (autenticado ou não): o campo `role` existe, mas ainda não é aplicado.
- O frontend escapa o texto vindo da API (escapeHtml, em rontend/src/utils/escape.js) antes de interpolá-lo em innerHTML, prevenindo XSS armazenado. Os demais pontos de HTML dinâmico usam apenas valores controlados pelo servidor (IDs e enums).
- Todos os dados da demonstração são sintéticos.

## 🗺️ Roadmap

- [ ] Detecção de anomalias (crescimento de ocorrências por categoria)
- [ ] Copiloto conversacional sobre os dados
- [ ] Automação via webhooks (Teams, Power Automate)
- [ ] Exportação de relatórios (CSV, Excel, PDF)
- [x] CI via GitHub Actions (43 testes a cada push)
- [ ] Validar o Docker Compose (escrito, ainda não testado em ambiente com Docker)
- [x] PostgreSQL em produção (Neon)
- [ ] Portar frontend para React + TypeScript + Vite (atualmente vanilla JS por restrição de ambiente)
- [ ] Controle de acesso por papéis (roles) na API e na interface

## 👤 Autor

Desenvolvido por Kayque Attico da Silva como projeto de portfólio.
