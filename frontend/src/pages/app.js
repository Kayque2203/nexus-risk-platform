import { getToken, clearToken, getCurrentUser, getDashboardStats, listProcesses, listRisks } from "../api/client.js";

if (!getToken()) {
  window.location.href = "index.html";
}

const userNameEl = document.getElementById("user-name");
const userRoleEl = document.getElementById("user-role");
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

function renderStats(stats) {
  statsGrid.innerHTML = `
    <div class="stat-card">
      <div class="stat-card__value">${stats.total_processes}</div>
      <div class="stat-card__label">Processos ativos</div>
    </div>
    <div class="stat-card ${stats.overdue_processes > 0 ? "stat-card--alert" : ""}">
      <div class="stat-card__value">${stats.overdue_processes}</div>
      <div class="stat-card__label">Processos atrasados</div>
    </div>
    <div class="stat-card">
      <div class="stat-card__value">${stats.total_risks}</div>
      <div class="stat-card__label">Riscos registrados</div>
    </div>
    <div class="stat-card ${stats.critical_risks > 0 ? "stat-card--alert" : ""}">
      <div class="stat-card__value">${stats.critical_risks}</div>
      <div class="stat-card__label">Riscos críticos</div>
    </div>
  `;
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

logoutBtn.addEventListener("click", () => {
  clearToken();
  window.location.href = "index.html";
});

loadEverything();
