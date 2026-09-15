import { getToken, clearToken, getCurrentUser, getProcess } from "../api/client.js";
import { renderSidebar } from "./sidebar.js";

if (!getToken()) window.location.href = "index.html";

document.getElementById("sidebar-container").innerHTML = renderSidebar("processes");

const params = new URLSearchParams(window.location.search);
const processId = params.get("id");
const content = document.getElementById("detail-content");

const STATUS_LABELS = {
  aberto: "Aberto",
  em_andamento: "Em andamento",
  concluido: "Concluído",
  atrasado: "Atrasado",
  cancelado: "Cancelado",
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
    const p = await getProcess(processId);
    content.innerHTML = `
      <h1>${p.name}</h1>
      <p class="lead">${p.description || "Sem descrição."}</p>
      <div class="ai-panel">
        <div class="ai-result__box">
          <div class="ai-result__box-label">Categoria</div>
          <div>${p.category || "—"}</div>
        </div>
        <div class="ai-result__box">
          <div class="ai-result__box-label">Departamento</div>
          <div>${p.department || "—"}</div>
        </div>
        <div class="ai-result__box">
          <div class="ai-result__box-label">Status</div>
          <div>${STATUS_LABELS[p.status] || p.status}</div>
        </div>
        <div class="ai-result__box">
          <div class="ai-result__box-label">Prioridade</div>
          <div>${p.priority}</div>
        </div>
        <div class="ai-result__box">
          <div class="ai-result__box-label">Prazo</div>
          <div>${p.due_date ? p.due_date.slice(0, 10) : "—"}</div>
        </div>
      </div>
    `;
  } catch (err) {
    content.innerHTML = `<div class="empty-state">${err.message}</div>`;
  }
}

load();
