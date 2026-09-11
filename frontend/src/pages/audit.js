import { getToken, clearToken, getCurrentUser, listAuditLogs } from "../api/client.js";
import { renderSidebar } from "./sidebar.js";

if (!getToken()) {
  window.location.href = "index.html";
}

document.getElementById("sidebar-container").innerHTML = renderSidebar("audit");

const userNameEl = document.getElementById("user-name");
const userRoleEl = document.getElementById("user-role");
const timeline = document.getElementById("audit-timeline");

const ACTION_ICONS = {
  create: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>`,
  update: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>`,
  delete: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>`,
};

const ACTION_LABELS = {
  create: "criou",
  update: "atualizou",
  delete: "excluiu",
};

const ENTITY_LABELS = {
  Process: "processo",
  Risk: "risco",
};

function formatDate(isoString) {
  const date = new Date(isoString);
  return date.toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function renderTimeline(logs) {
  if (logs.length === 0) {
    timeline.innerHTML = `<div class="empty-state">Nenhuma ação registrada ainda.</div>`;
    return;
  }

  timeline.innerHTML = logs.map((log) => {
    const entityLabel = ENTITY_LABELS[log.entity_type] || log.entity_type;
    const actionLabel = ACTION_LABELS[log.action] || log.action;
    const shortId = log.entity_id.slice(0, 8);

    return `
      <div class="audit-entry">
        <div class="audit-entry__icon audit-entry__icon--${log.action}">
          ${ACTION_ICONS[log.action] || ""}
        </div>
        <div class="audit-entry__content">
          <div class="audit-entry__title">
            Usuário <strong>${log.user_name || "desconhecido"}</strong>
            ${actionLabel} o ${entityLabel} <strong>#${shortId}</strong>
          </div>
          ${log.changes ? `<div class="audit-entry__changes">${log.changes}</div>` : ""}
          <div class="audit-entry__meta">${formatDate(log.created_at)}</div>
        </div>
      </div>
    `;
  }).join("");
}

async function loadLogs() {
  try {
    const logs = await listAuditLogs();
    renderTimeline(logs);
  } catch (err) {
    timeline.innerHTML = `<div class="empty-state">Erro ao carregar auditoria.</div>`;
  }
}

document.getElementById("logout-btn").addEventListener("click", () => {
  clearToken();
  window.location.href = "index.html";
});

async function init() {
  try {
    const user = await getCurrentUser();
    userNameEl.textContent = user.name;
    userRoleEl.textContent = user.role;
  } catch (err) {
    clearToken();
    window.location.href = "index.html";
    return;
  }
  await loadLogs();
}

init();
