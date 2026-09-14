const API_BASE_URL = "http://127.0.0.1:8000";

export function getToken() {
  return localStorage.getItem("nexus_token");
}

export function setToken(token) {
  localStorage.setItem("nexus_token", token);
}

export function clearToken() {
  localStorage.removeItem("nexus_token");
}

export async function login(email, password) {
  const body = new URLSearchParams();
  body.set("username", email);
  body.set("password", password);

  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || "Não foi possível fazer login.");
  }

  return response.json();
}

export async function getCurrentUser() {
  const token = getToken();
  const response = await fetch(`${API_BASE_URL}/api/users/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!response.ok) {
    throw new Error("Sessão expirada.");
  }

  return response.json();
}


export async function getDashboardStats() {
  const token = getToken();
  const response = await fetch(`${API_BASE_URL}/api/dashboard/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Não foi possível carregar o dashboard.");
  return response.json();
}

export async function listProcesses() {
  const token = getToken();
  const response = await fetch(`${API_BASE_URL}/api/processes/?limit=10`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Não foi possível carregar os processos.");
  return response.json();
}

export async function listRisks() {
  const token = getToken();
  const response = await fetch(`${API_BASE_URL}/api/risks/?limit=10`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Não foi possível carregar os riscos.");
  return response.json();
}


export async function listAllProcessesForSelect() {
  const token = getToken();
  const response = await fetch(`${API_BASE_URL}/api/processes/?limit=1000`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Não foi possível carregar processos.");
  return response.json();
}

export async function createProcess(data) {
  const token = getToken();
  const response = await fetch(`${API_BASE_URL}/api/processes/`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || "Não foi possível criar o processo.");
  }
  return response.json();
}

export async function updateProcess(id, data) {
  const token = getToken();
  const response = await fetch(`${API_BASE_URL}/api/processes/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || "Não foi possível atualizar o processo.");
  }
  return response.json();
}

export async function deleteProcess(id) {
  const token = getToken();
  const response = await fetch(`${API_BASE_URL}/api/processes/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Não foi possível excluir o processo.");
}

export async function createRisk(data) {
  const token = getToken();
  const response = await fetch(`${API_BASE_URL}/api/risks/`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || "Não foi possível criar o risco.");
  }
  return response.json();
}

export async function updateRisk(id, data) {
  const token = getToken();
  const response = await fetch(`${API_BASE_URL}/api/risks/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || "Não foi possível atualizar o risco.");
  }
  return response.json();
}

export async function deleteRisk(id) {
  const token = getToken();
  const response = await fetch(`${API_BASE_URL}/api/risks/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Não foi possível excluir o risco.");
}


export async function analyzeText(text) {
  const token = getToken();
  const response = await fetch(`${API_BASE_URL}/api/ai/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify({ text }),
  });
  if (!response.ok) throw new Error("Não foi possível analisar o texto.");
  return response.json();
}


export async function listAuditLogs() {
  const token = getToken();
  const response = await fetch(`${API_BASE_URL}/api/audit-logs/?limit=50`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Não foi possível carregar a auditoria.");
  return response.json();
}


export async function getRisk(id) {
  const token = getToken();
  const response = await fetch(`${API_BASE_URL}/api/risks/${id}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Risco não encontrado.");
  return response.json();
}
