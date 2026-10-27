import { escapeHtml } from "../utils/escape.js";
import { getToken, clearToken, getCurrentUser, getRisk, listActionsByRisk, createAction } from "../api/client.js";
import { renderSidebar } from "./sidebar.js";

if (!getToken()) window.location.href = "index.html";

document.getElementById("sidebar-container").innerHTML = renderSidebar("risks");

const params = new URLSearchParams(window.location.search);
const riskId = params.get("id");
const content = document.getElementById("detail-content");

const LEVEL_LABELS = {
  baixa: "Baixa",
  media: "M\u00e9dia",
  alta: "Alta",
  critica: "Cr\u00edtica",
};

const IMPACT_LABELS = {
  baixa: "Baixo",
  media: "M\u00e9dio",
  alta: "Alto",
  critica: "Cr\u00edtico",
};

const RISK_STATUS_LABELS = {
  aberto: "Aberto",
  em_mitigacao: "Em mitiga\u00e7\u00e3o",
  mitigado: "Mitigado",
  aceito: "Aceito",
  cancelado: "Cancelado",
};

const ACTION_STATUS_LABELS = {
  aberta: "Aberta",
  em_andamento: "Em andamento",
  concluida: "Conclu\u00edda",
  atrasada: "Atrasada",
  cancelada: "Cancelada",
};

async function load() {
  try {
    const user = await getCurrentUser();
    document.getElementById("user-name").textContent = user.name;
    document.getElementById("user-role").textContent = user.role;
  } catch {
    clearToken();
    window.location.href = "index.html";
    return;
  }

  document.getElementById("logout-btn").addEventListener("click", () => {
    clearToken();
    window.location.href = "index.html";
  });

  try {
    const r = await getRisk(riskId);
    content.innerHTML = `
      <h1>${escapeHtml(r.description)}</h1>
      <p class="lead">Categoria: ${escapeHtml(r.category) || "—"}</p>
      <div class="ai-panel">
        <div class="ai-result__box">
          <div class="ai-result__box-label">Severidade</div>
          <span class="badge badge--${r.severity}">${(LEVEL_LABELS[r.severity] || r.severity).toUpperCase()}</span>
        </div>
        <div class="ai-result__box">
          <div class="ai-result__box-label">Probabilidade / Impacto</div>
          <div>${LEVEL_LABELS[r.probability] || r.probability} / ${IMPACT_LABELS[r.impact] || r.impact}</div>
        </div>
        <div class="ai-result__box">
          <div class="ai-result__box-label">Status</div>
          <div>${RISK_STATUS_LABELS[r.status] || r.status}</div>
        </div>
        <div class="ai-result__box">
          <div class="ai-result__box-label">Prioridade</div>
          <div>${LEVEL_LABELS[r.priority] || r.priority}</div>
        </div>
      </div>
    `;
  } catch (err) {
    content.innerHTML = `<div class="empty-state">${escapeHtml(err.message)}</div>`;
  }
}

async function loadActions() {
  try {
    const actions = await listActionsByRisk(riskId);
    document.getElementById("actions-section").style.display = "block";
    const list = document.getElementById("actions-list");
    if (actions.length === 0) {
      list.innerHTML = `<p class="empty-state">Nenhuma ação cadastrada.</p>`;
    } else {
      list.innerHTML = actions.map(a => `
        <div class="ai-result__box">
          <div>${escapeHtml(a.description)}</div>
          <div style="font-size:12px;color:var(--color-ink-soft);margin-top:4px;">${ACTION_STATUS_LABELS[a.status] || a.status}</div>
        </div>
      `).join("");
    }
  } catch (err) {
    console.error(err);
  }
}

document.getElementById("new-action-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const desc = document.getElementById("new-action-desc").value;
  try {
    await createAction({ risk_id: riskId, description: desc, status: "aberta" });
    document.getElementById("new-action-desc").value = "";
    await loadActions();
  } catch (err) {
    alert(err.message);
  }
});

load();
loadActions();



