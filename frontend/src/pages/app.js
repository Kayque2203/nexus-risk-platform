import { getToken, clearToken, getCurrentUser, getDashboardStats, listProcesses, listRisks } from "../api/client.js";
import { renderSidebar } from "./sidebar.js";

if (!getToken()) {
  window.location.href = "index.html";
}

document.getElementById("sidebar-container").innerHTML = renderSidebar("dashboard");

const userNameEl = document.getElementById("user-name");
const userRoleEl = document.getElementById("user-role");
const greetingNameEl = document.getElementById("greeting-name");
const logoutBtn = document.getElementById("logout-btn");
const statsGrid = document.getElementById("stats-grid");
const processesBody = document.getElementById("processes-table-body");
const risksBody = document.getElementById("risks-table-body");

const STATUS_LABELS = {
  aberto: "Aberto",
  em_andamento: "Em andamento",
  concluido: "Concluído",
  atrasado: "Atrasado",
  cancelado: "Cancelado",
  em_mitigacao: "Em mitigação",
  mitigado: "Mitigado",
  aceito: "Aceito",
};

// Icones inline (mesmo padrao do sidebar.js) -- evita depender de uma
// biblioteca de icones externa, mantendo o projeto sem novas dependencias.
const ICONS = {
  processes: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/></svg>`,
  overdue: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>`,
  risks: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,
  critical: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 9v4"/><path d="M12 17h.01"/><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/></svg>`,
};

function renderStats(stats) {
  const cards = [
    {
      icon: ICONS.processes,
      value: stats.total_processes,
      label: "Processos ativos",
      alert: false,
    },
    {
      icon: ICONS.overdue,
      value: stats.overdue_processes,
      label: "Processos atrasados",
      alert: stats.overdue_processes > 0,
    },
    {
      icon: ICONS.risks,
      value: stats.total_risks,
      label: "Riscos registrados",
      alert: false,
    },
    {
      icon: ICONS.critical,
      value: stats.critical_risks,
      label: "Riscos críticos",
      alert: stats.critical_risks > 0,
    },
  ];

  statsGrid.innerHTML = cards.map((card) => `
    <div class="kpi-card ${card.alert ? "kpi-card--alert" : ""}">
      <div class="kpi-card__top">
        <div class="kpi-card__icon">${card.icon}</div>
      </div>
      <div class="kpi-card__value">${card.value}</div>
      <div class="kpi-card__label">${card.label}</div>
    </div>
  `).join("");
}

function renderProcesses(processes) {
  if (processes.length === 0) {
    processesBody.innerHTML = `<tr><td colspan="4" class="empty-state">Nenhum processo cadastrado ainda.</td></tr>`;
    return;
  }
  processesBody.innerHTML = processes.map((p) => `
    <tr>
      <td>${p.name}</td>
      <td>${p.department || "—"}</td>
      <td>${STATUS_LABELS[p.status] || p.status}</td>
      <td>${p.priority}</td>
    </tr>
  `).join("");
}

function renderRisks(risks) {
  if (risks.length === 0) {
    risksBody.innerHTML = `<tr><td colspan="4" class="empty-state">Nenhum risco cadastrado ainda.</td></tr>`;
    return;
  }
  risksBody.innerHTML = risks.map((r) => `
    <tr>
      <td>${r.description}</td>
      <td>${r.category || "—"}</td>
      <td><span class="badge badge--${r.severity || "media"}">${(r.severity || "—").toUpperCase()}</span></td>
      <td>${STATUS_LABELS[r.status] || r.status}</td>
    </tr>
  `).join("");
}

async function loadEverything() {
  try {
    const user = await getCurrentUser();
    userNameEl.textContent = user.name;
    userRoleEl.textContent = user.role;
    greetingNameEl.textContent = user.name.split(" ")[0];
  } catch (err) {
    clearToken();
    window.location.href = "index.html";
    return;
  }

  try {
    const stats = await getDashboardStats();
    renderStats(stats);
  } catch (err) {
    statsGrid.innerHTML = `<div class="empty-state">Não foi possível carregar os indicadores.</div>`;
  }

  try {
    const processes = await listProcesses();
    renderProcesses(processes);
  } catch (err) {
    processesBody.innerHTML = `<tr><td colspan="4" class="empty-state">Erro ao carregar processos.</td></tr>`;
  }

  try {
    const risks = await listRisks();
    renderRisks(risks);
  } catch (err) {
    risksBody.innerHTML = `<tr><td colspan="4" class="empty-state">Erro ao carregar riscos.</td></tr>`;
  }
}

document.getElementById("logout-btn").addEventListener("click", () => {
  clearToken();
  window.location.href = "index.html";
});

loadEverything();
