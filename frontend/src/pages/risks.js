import { getToken, clearToken, getCurrentUser, listRisks, createRisk, updateRisk, deleteRisk, listAllProcessesForSelect } from "../api/client.js";

if (!getToken()) {
  window.location.href = "index.html";
}

const userNameEl = document.getElementById("user-name");
const userRoleEl = document.getElementById("user-role");
const logoutBtn = document.getElementById("logout-btn");
const tableBody = document.getElementById("risks-table-body");
const formPanel = document.getElementById("risk-form-panel");
const form = document.getElementById("risk-form");
const formTitle = document.getElementById("form-title");
const formError = document.getElementById("risk-form-error");
const newBtn = document.getElementById("new-risk-btn");
const cancelBtn = document.getElementById("cancel-risk-btn");
const processSelect = document.getElementById("r-process");

const STATUS_LABELS = {
  aberto: "Aberto",
  em_mitigacao: "Em mitigação",
  mitigado: "Mitigado",
  aceito: "Aceito",
  cancelado: "Cancelado",
};

let currentRisks = [];
let availableProcesses = [];

function populateProcessSelect() {
  processSelect.innerHTML = availableProcesses
    .map((p) => `<option value="${p.id}">${p.name}</option>`)
    .join("");
}

function openForm(risk = null) {
  form.reset();
  formError.classList.remove("visible");
  populateProcessSelect();

  if (risk) {
    formTitle.textContent = "Editar risco";
    document.getElementById("risk-id").value = risk.id;
    document.getElementById("r-process").value = risk.process_id;
    document.getElementById("r-description").value = risk.description;
    document.getElementById("r-category").value = risk.category || "";
    document.getElementById("r-status").value = risk.status;
    document.getElementById("r-probability").value = risk.probability;
    document.getElementById("r-impact").value = risk.impact;
    document.getElementById("r-priority").value = risk.priority;
  } else {
    formTitle.textContent = "Novo risco";
    document.getElementById("risk-id").value = "";
  }

  formPanel.classList.add("visible");
}

function closeForm() {
  formPanel.classList.remove("visible");
  form.reset();
}

function renderTable(risks) {
  if (risks.length === 0) {
    tableBody.innerHTML = `<tr><td colspan="5" class="empty-state">Nenhum risco cadastrado ainda.</td></tr>`;
    return;
  }

  tableBody.innerHTML = risks.map((r) => `
    <tr>
      <td>${r.description}</td>
      <td>${r.category || "—"}</td>
      <td><span class="badge badge--${r.severity || "media"}">${(r.severity || "—").toUpperCase()}</span></td>
      <td>${STATUS_LABELS[r.status] || r.status}</td>
      <td>
        <button class="btn-small" data-edit="${r.id}">Editar</button>
        <button class="btn-small btn-small--danger" data-delete="${r.id}">Excluir</button>
      </td>
    </tr>
  `).join("");
}

async function loadRisks() {
  try {
    currentRisks = await listRisks();
    renderTable(currentRisks);
  } catch (err) {
    tableBody.innerHTML = `<tr><td colspan="5" class="empty-state">Erro ao carregar riscos.</td></tr>`;
  }
}

async function loadProcessesForSelect() {
  try {
    availableProcesses = await listAllProcessesForSelect();
  } catch (err) {
    availableProcesses = [];
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  formError.classList.remove("visible");

  const id = document.getElementById("risk-id").value;

  const data = {
    process_id: document.getElementById("r-process").value,
    description: document.getElementById("r-description").value,
    category: document.getElementById("r-category").value || null,
    status: document.getElementById("r-status").value,
    probability: document.getElementById("r-probability").value,
    impact: document.getElementById("r-impact").value,
    priority: document.getElementById("r-priority").value,
  };

  try {
    if (id) {
      await updateRisk(id, data);
    } else {
      await createRisk(data);
    }
    closeForm();
    await loadRisks();
  } catch (err) {
    formError.textContent = err.message;
    formError.classList.add("visible");
  }
});

tableBody.addEventListener("click", async (event) => {
  const editId = event.target.getAttribute("data-edit");
  const deleteId = event.target.getAttribute("data-delete");

  if (editId) {
    const risk = currentRisks.find((r) => r.id === editId);
    openForm(risk);
  }

  if (deleteId) {
    if (confirm("Tem certeza que deseja excluir este risco?")) {
      try {
        await deleteRisk(deleteId);
        await loadRisks();
      } catch (err) {
        alert(err.message);
      }
    }
  }
});

newBtn.addEventListener("click", async () => {
  if (availableProcesses.length === 0) {
    await loadProcessesForSelect();
  }
  openForm();
});

cancelBtn.addEventListener("click", closeForm);

logoutBtn.addEventListener("click", () => {
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
  await loadProcessesForSelect();
  await loadRisks();
}

init();
