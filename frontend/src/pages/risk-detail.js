import { getToken, clearToken, getCurrentUser, getRisk } from "../api/client.js";
import { renderSidebar } from "./sidebar.js";

if (!getToken()) window.location.href = "index.html";

document.getElementById("sidebar-container").innerHTML = renderSidebar("risks");

const params = new URLSearchParams(window.location.search);
const riskId = params.get("id");
const content = document.getElementById("detail-content");

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
      <h1>${r.description}</h1>
      <p class="lead">Categoria: ${r.category || "—"}</p>
      <div class="ai-panel">
        <div class="ai-result__box">
          <div class="ai-result__box-label">Severidade</div>
          <span class="badge badge--${r.severity}">${r.severity.toUpperCase()}</span>
        </div>
        <div class="ai-result__box">
          <div class="ai-result__box-label">Probabilidade / Impacto</div>
          <div>${r.probability} / ${r.impact}</div>
        </div>
        <div class="ai-result__box">
          <div class="ai-result__box-label">Status</div>
          <div>${r.status}</div>
        </div>
        <div class="ai-result__box">
          <div class="ai-result__box-label">Prioridade</div>
          <div>${r.priority}</div>
        </div>
      </div>
    `;
  } catch (err) {
    content.innerHTML = `<div class="empty-state">${err.message}</div>`;
  }
}

load();

