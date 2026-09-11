import { getToken, clearToken, getCurrentUser, analyzeText } from "../api/client.js";
import { renderSidebar } from "./sidebar.js";

if (!getToken()) {
  window.location.href = "index.html";
}

document.getElementById("sidebar-container").innerHTML = renderSidebar("ai");

const userNameEl = document.getElementById("user-name");
const userRoleEl = document.getElementById("user-role");
const textInput = document.getElementById("ai-text-input");
const analyzeBtn = document.getElementById("analyze-btn");
const errorBox = document.getElementById("ai-error");
const resultBox = document.getElementById("ai-result");

// Mapeia cada nivel qualitativo para quantos dos 4 segmentos da barra
// devem ficar preenchidos -- e uma escala visual fixa (1 a 4), nunca
// um numero calculado ou inventado pelo frontend.
const LEVEL_TO_SEGMENTS = {
  baixa: 1,
  media: 2,
  alta: 3,
  critica: 4,
};

const LEVEL_LABELS = {
  baixa: "Baixa",
  media: "Média",
  alta: "Alta",
  critica: "Crítica",
};

function renderLevelBar(containerId, valueId, level) {
  const filledCount = LEVEL_TO_SEGMENTS[level] || 0;
  const container = document.getElementById(containerId);

  container.innerHTML = Array.from({ length: 4 }, (_, i) => {
    const filledClass = i < filledCount ? `level-bar__segment--filled-${level}` : "";
    return `<div class="level-bar__segment ${filledClass}"></div>`;
  }).join("");

  document.getElementById(valueId).textContent = LEVEL_LABELS[level] || "—";
}

async function handleAnalyze() {
  const text = textInput.value.trim();
  errorBox.classList.remove("visible");

  if (!text) {
    errorBox.textContent = "Descreva a situação de risco antes de analisar.";
    errorBox.classList.add("visible");
    return;
  }

  analyzeBtn.disabled = true;
  analyzeBtn.textContent = "Analisando...";

  try {
    const result = await analyzeText(text);

    document.getElementById("result-category").textContent = result.category;
    renderLevelBar("bar-probability", "value-probability", result.probability);
    renderLevelBar("bar-impact", "value-impact", result.impact);
    renderLevelBar("bar-severity", "value-severity", result.severity);
    document.getElementById("result-reason").textContent = result.reason;
    document.getElementById("result-action").textContent = result.recommended_action;

    resultBox.classList.add("visible");
  } catch (err) {
    errorBox.textContent = err.message;
    errorBox.classList.add("visible");
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a5 5 0 0 1 5 5v2a5 5 0 0 1-10 0V7a5 5 0 0 1 5-5z"/><path d="M8 14v2a4 4 0 0 0 8 0v-2"/><line x1="12" y1="20" x2="12" y2="22"/></svg>
      Analisar com IA
    `;
  }
}

analyzeBtn.addEventListener("click", handleAnalyze);

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
  }
}

init();
