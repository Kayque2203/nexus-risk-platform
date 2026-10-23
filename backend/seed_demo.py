"""Popula a API do NEXUS com dados de demonstracao 100% sinteticos.

Usa apenas a API publica (HTTPS), entao a severidade dos riscos e a
auditoria sao geradas pelas regras normais do sistema.

Uso (dentro da pasta backend):
    python seed_demo.py
    python seed_demo.py http://127.0.0.1:8000   (para testar no backend local)

O script e idempotente por processo: se um processo com o mesmo nome ja
existir, ele e pulado (junto com seus riscos e acoes).
"""
import getpass
import sys
from datetime import datetime, timedelta

import httpx
import ssl

DEFAULT_URL = "https://nexus-risk-platform.onrender.com"


def due(days):
    """Data de prazo relativa a hoje (negativo = no passado), sem fuso."""
    return (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")


PROCESSES = [
    {
        "name": "Controle de Mudanças",
        "description": "Avaliação, aprovação e rastreabilidade de mudanças em processos, sistemas e instalações.",
        "category": "Qualidade",
        "department": "Garantia da Qualidade",
        "status": "em_andamento",
        "priority": "alta",
        "due_days": 45,
        "risks": [
            {
                "description": "Mudança implementada sem avaliação de impacto prévia",
                "category": "Compliance",
                "probability": "media",
                "impact": "alta",
                "priority": "alta",
                "status": "em_mitigacao",
                "due_days": 30,
                "actions": [
                    {"description": "Revisar o fluxo de aprovação e exigir avaliação de impacto antes da implementação", "status": "em_andamento", "due_days": 20},
                    {"description": "Treinar os solicitantes no novo formulário de mudança", "status": "aberta", "due_days": 35},
                ],
            },
            {
                "description": "Mudanças emergenciais sem registro formal posterior",
                "category": "Compliance",
                "probability": "baixa",
                "impact": "alta",
                "priority": "media",
                "status": "aberto",
                "due_days": 60,
                "actions": [],
            },
        ],
    },
    {
        "name": "Gestão de Desvios e CAPA",
        "description": "Registro, investigação de causa raiz e ações corretivas e preventivas para desvios.",
        "category": "Qualidade",
        "department": "Garantia da Qualidade",
        "status": "atrasado",
        "priority": "critica",
        "due_days": -10,
        "risks": [
            {
                "description": "Investigações de desvios concluídas fora do prazo estabelecido",
                "category": "Compliance",
                "probability": "alta",
                "impact": "critica",
                "priority": "critica",
                "status": "em_mitigacao",
                "due_days": -5,
                "actions": [
                    {"description": "Definir prazo máximo por classe de desvio e monitorar semanalmente", "status": "em_andamento", "due_days": 7},
                    {"description": "Alocar investigador adicional para a fila de desvios críticos", "status": "atrasada", "due_days": -3},
                ],
            },
            {
                "description": "Ações corretivas encerradas sem verificação de eficácia",
                "category": "Compliance",
                "probability": "media",
                "impact": "media",
                "priority": "media",
                "status": "aberto",
                "due_days": 40,
                "actions": [
                    {"description": "Incluir etapa obrigatória de verificação de eficácia no procedimento de CAPA", "status": "aberta", "due_days": 25},
                ],
            },
        ],
    },
    {
        "name": "Qualificação de Fornecedores",
        "description": "Avaliação inicial e reavaliação periódica de fornecedores de materiais críticos.",
        "category": "Suprimentos",
        "department": "Suprimentos",
        "status": "em_andamento",
        "priority": "alta",
        "due_days": 90,
        "risks": [
            {
                "description": "Fornecedor único para matéria-prima estratégica",
                "category": "Operacional",
                "probability": "media",
                "impact": "critica",
                "priority": "alta",
                "status": "em_mitigacao",
                "due_days": 75,
                "actions": [
                    {"description": "Homologar um fornecedor alternativo para a matéria-prima", "status": "em_andamento", "due_days": 70},
                ],
            },
            {
                "description": "Reavaliação periódica de fornecedores em atraso",
                "category": "Compliance",
                "probability": "alta",
                "impact": "media",
                "priority": "alta",
                "status": "aberto",
                "due_days": 20,
                "actions": [
                    {"description": "Elaborar cronograma anual de reavaliações com responsáveis definidos", "status": "concluida", "due_days": -5},
                ],
            },
            {
                "description": "Reajuste de preços de fornecedor sem cláusula de proteção contratual",
                "category": "Financeiro",
                "probability": "media",
                "impact": "media",
                "priority": "media",
                "status": "aceito",
                "due_days": 100,
                "actions": [],
            },
        ],
    },
    {
        "name": "Treinamento e Qualificação de Pessoal",
        "description": "Garantia de que os colaboradores estejam treinados e qualificados nas atividades que executam.",
        "category": "Pessoas",
        "department": "Recursos Humanos",
        "status": "em_andamento",
        "priority": "media",
        "due_days": 60,
        "risks": [
            {
                "description": "Colaboradores executando tarefas sem treinamento vigente",
                "category": "Compliance",
                "probability": "media",
                "impact": "alta",
                "priority": "alta",
                "status": "aberto",
                "due_days": 30,
                "actions": [
                    {"description": "Gerar relatório mensal de treinamentos vencidos por área", "status": "em_andamento", "due_days": 15},
                ],
            },
            {
                "description": "Matriz de treinamento desatualizada após mudanças de função",
                "category": "Operacional",
                "probability": "alta",
                "impact": "baixa",
                "priority": "media",
                "status": "aberto",
                "due_days": 50,
                "actions": [],
            },
        ],
    },
    {
        "name": "Gestão de Documentos Controlados",
        "description": "Elaboração, revisão, aprovação e distribuição de procedimentos e registros.",
        "category": "Qualidade",
        "department": "Documentação",
        "status": "aberto",
        "priority": "media",
        "due_days": 120,
        "risks": [
            {
                "description": "Uso de versões obsoletas de procedimentos na operação",
                "category": "Compliance",
                "probability": "baixa",
                "impact": "alta",
                "priority": "media",
                "status": "aberto",
                "due_days": 90,
                "actions": [
                    {"description": "Implantar controle de cópias impressas com carimbo de documento controlado", "status": "aberta", "due_days": 60},
                ],
            },
        ],
    },
    {
        "name": "Validação de Sistemas Computadorizados",
        "description": "Validação e manutenção do estado validado de sistemas que impactam a qualidade.",
        "category": "TI",
        "department": "Tecnologia da Informação",
        "status": "em_andamento",
        "priority": "alta",
        "due_days": 100,
        "risks": [
            {
                "description": "Ausência de trilha de auditoria em sistema com dados críticos",
                "category": "Tecnologia",
                "probability": "media",
                "impact": "critica",
                "priority": "alta",
                "status": "em_mitigacao",
                "due_days": 55,
                "actions": [
                    {"description": "Habilitar e validar o registro de trilha de auditoria no sistema", "status": "em_andamento", "due_days": 40},
                ],
            },
            {
                "description": "Compartilhamento de credenciais de acesso em sistema validado",
                "category": "Segurança",
                "probability": "alta",
                "impact": "alta",
                "priority": "alta",
                "status": "aberto",
                "due_days": 25,
                "actions": [
                    {"description": "Desativar contas genéricas e criar acessos individuais", "status": "aberta", "due_days": 18},
                    {"description": "Revisar trimestralmente a lista de usuários ativos", "status": "aberta", "due_days": 80},
                ],
            },
        ],
    },
    {
        "name": "Calibração de Equipamentos",
        "description": "Controle de calibração e manutenção preventiva de instrumentos de medição.",
        "category": "Operações",
        "department": "Manutenção",
        "status": "concluido",
        "priority": "baixa",
        "due_days": -15,
        "risks": [
            {
                "description": "Instrumento utilizado com calibração vencida",
                "category": "Operacional",
                "probability": "baixa",
                "impact": "alta",
                "priority": "media",
                "status": "mitigado",
                "due_days": -20,
                "actions": [
                    {"description": "Bloquear o uso de instrumentos vencidos por etiqueta e controle em sistema", "status": "concluida", "due_days": -25},
                ],
            },
        ],
    },
    {
        "name": "Gestão de Reclamações de Clientes",
        "description": "Recebimento, investigação e resposta a reclamações relacionadas a produtos e serviços.",
        "category": "Qualidade",
        "department": "Atendimento ao Cliente",
        "status": "em_andamento",
        "priority": "media",
        "due_days": 30,
        "risks": [
            {
                "description": "Reclamações recorrentes sem análise de tendência",
                "category": "Operacional",
                "probability": "media",
                "impact": "media",
                "priority": "media",
                "status": "aberto",
                "due_days": 45,
                "actions": [
                    {"description": "Criar painel mensal de reclamações por categoria e causa", "status": "aberta", "due_days": 40},
                ],
            },
            {
                "description": "Dados pessoais de clientes armazenados em planilhas compartilhadas",
                "category": "Segurança",
                "probability": "baixa",
                "impact": "critica",
                "priority": "media",
                "status": "aberto",
                "due_days": 70,
                "actions": [],
            },
        ],
    },
]


def check(response, what):
    if response.status_code >= 400:
        print("ERRO em", what, "-> HTTP", response.status_code)
        print(response.text[:300])
        sys.exit(1)


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    print("Servidor:", base)
    email = input("E-mail do usuario: ").strip()
    password = getpass.getpass("Senha: ")

    # Usa o repositorio de certificados do Windows e desliga apenas a checagem estrita (VERIFY_X509_STRICT); necessario em maquinas com inspecao de HTTPS. A verificacao da cadeia e do hostname continua ativa.
    ctx = ssl.create_default_context()
    ctx.verify_flags &= ~ssl.VERIFY_X509_STRICT
    with httpx.Client(base_url=base, timeout=180, verify=ctx) as client:
        print("Acordando o servidor (pode levar ate 1 minuto)...")
        client.get("/health")

        r = client.post("/api/auth/login", data={"username": email, "password": password})
        check(r, "login")
        client.headers["Authorization"] = "Bearer " + r.json()["access_token"]

        r = client.get("/api/processes/", params={"limit": 1000})
        check(r, "listar processos")
        existing = {p["name"] for p in r.json()}

        n_proc = n_risk = n_act = 0
        for spec in PROCESSES:
            if spec["name"] in existing:
                print("Ja existe, pulando:", spec["name"])
                continue

            body = {
                k: spec[k]
                for k in ("name", "description", "category", "department", "status", "priority")
            }
            body["due_date"] = due(spec["due_days"])
            r = client.post("/api/processes/", json=body)
            check(r, "criar processo " + spec["name"])
            process_id = r.json()["id"]
            n_proc += 1
            print("Processo criado:", spec["name"])

            for rk in spec["risks"]:
                rbody = {
                    k: rk[k]
                    for k in ("description", "category", "probability", "impact", "priority", "status")
                }
                rbody["process_id"] = process_id
                rbody["due_date"] = due(rk["due_days"])
                r = client.post("/api/risks/", json=rbody)
                check(r, "criar risco")
                risk_id = r.json()["id"]
                n_risk += 1

                for ac in rk["actions"]:
                    abody = {
                        "risk_id": risk_id,
                        "description": ac["description"],
                        "status": ac["status"],
                        "due_date": due(ac["due_days"]),
                    }
                    r = client.post("/api/actions/", json=abody)
                    check(r, "criar acao")
                    n_act += 1

    print("Concluido: %d processos, %d riscos, %d acoes criados." % (n_proc, n_risk, n_act))


if __name__ == "__main__":
    main()
