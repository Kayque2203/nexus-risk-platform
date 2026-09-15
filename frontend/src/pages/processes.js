import { getToken, clearToken, getCurrentUser, listProcesses, createProcess, updateProcess, deleteProcess } from "../api/client.js";
import { renderSidebar } from "./sidebar.js";

if (!getToken()) {
  window.location.href = "index.html";
}

document.getElementById("sidebar-container").innerHTML = renderSidebar("processes");

const userNameEl = document.getElementById("user-name");
const userRoleEl = document.getElementById("user-role");
const logoutBtn = document.getElementById("logout-btn");
const tableBody = document.getElementById("processes-table-body");
const formPanel = document.getElementById("process-form-panel");
const form = document.getElementById("process-form");
const formTitle = document.getElementById("form-title");
const formError = document.getElementById("process-form-error");
const newBtn = document.getElementById("new-process-btn");
const cancelBtn = document.getElementById("cancel-process-btn");

const STATUS_LABELS = {
  aberto: "Aberto",
  em_andamento: "Em andamento",
  concluido: "Concluído",
  atrasado: "Atrasado",
  cancelado: "Cancelado",
};

function openForm(process = null) {
  form.reset();
  formError.classList.remove("visible");

  if (process) {
    formTitle.textContent = "Editar processo";
    document.getElementById("process-id").value = process.id;
    document.getElementById("p-name").value = process.name;
    document.getElementById("p-description").value = process.description || "";
    document.getElementById("p-category").value = process.category || "";
    document.getElementById("p-department").value = process.department || "";
    document.getElementById("p-status").value = process.status;
    document.getElementById("p-priority").value = process.priority;
    document.getElementById("p-due-date").value = process.due_date ? process.due_date.slice(0, 10) : "";
  } else {
    formTitle.textContent = "Novo processo";
    document.getElementById("process-id").value = "";
  }

  formPanel.classList.add("visible");
}

function closeForm() {
  formPanel.classList.remove("visible");
  form.reset();
}

function renderTable(processes) {
  if (processes.length === 0) {
    tableBody.innerHTML = `<tr><td colspan="5" class="empty-state">Nenhum processo cadastrado ainda.</td></tr>`;
    return;
  }

  tableBody.innerHTML = processes.map((p) => `
    <tr>
      <td><a href="process-detail.html?id=${p.id}" style="color:inherit;">${p.name}</a></td>
      <td>${p.department || "—"}</td>
      <td>${STATUS_LABELS[p.status] || p.status}</td>
      <td>${p.priority}</td>
      <td>
        <button class="btn-small" data-edit="${p.id}">Editar</button>
        <button class="btn-small btn-small--danger" data-delete="${p.id}">Excluir</button>
      </td>
    </tr>
  `).join("");
}

let currentProcesses = [];

const filterSearch = document.getElementById("filter-search");
const filterStatus = document.getElementById("filter-status");

function applyFilters() {
  const searchTerm = filterSearch.value.toLowerCase().trim();
  const statusValue = filterStatus.value;

  const filtered = currentProcesses.filter((p) => {
    const matchesSearch = !searchTerm || p.name.toLowerCase().includes(searchTerm);
    const matchesStatus = !statusValue || p.status === statusValue;
    return matchesSearch && matchesStatus;
  });

  renderTable(filtered);
}

filterSearch.addEventListener("input", applyFilters);
filterStatus.addEventListener("change", applyFilters);

async function loadProcesses() {
  try {
    currentProcesses = await listProcesses();
    applyFilters();
  } catch (err) {
    tableBody.innerHTML = `<tr><td colspan="5" class="empty-state">Erro ao carregar processos.</td></tr>`;
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  formError.classList.remove("visible");

  const id = document.getElementById("process-id").value;
  const dueDateValue = document.getElementById("p-due-date").value;

  const data = {
    name: document.getElementById("p-name").value,
    description: document.getElementById("p-description").value || null,
    category: document.getElementById("p-category").value || null,
    department: document.getElementById("p-department").value || null,
    status: document.getElementById("p-status").value,
    priority: document.getElementById("p-priority").value,
    due_date: dueDateValue ? `${dueDateValue}T00:00:00` : null,
  };

  try {
    if (id) {
      await updateProcess(id, data);
    } else {
      await createProcess(data);
    }
    closeForm();
    await loadProcesses();
  } catch (err) {
    formError.textContent = err.message;
    formError.classList.add("visible");
  }
});

tableBody.addEventListener("click", async (event) => {
  const editId = event.target.getAttribute("data-edit");
  const deleteId = event.target.getAttribute("data-delete");

  if (editId) {
    const process = currentProcesses.find((p) => p.id === editId);
    openForm(process);
  }

  if (deleteId) {
    if (confirm("Tem certeza que deseja excluir este processo?")) {
      try {
        await deleteProcess(deleteId);
        await loadProcesses();
      } catch (err) {
        alert(err.message);
      }
    }
  }
});

newBtn.addEventListener("click", () => openForm());
cancelBtn.addEventListener("click", closeForm);

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
  await loadProcesses();
}

init();



