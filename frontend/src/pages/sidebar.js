// Componente reutilizavel de sidebar -- gerado via JS para evitar
// duplicar o mesmo HTML em cada pagina (problema identificado na
// auditoria: nav duplicada manualmente em app.html/processes.html/risks.html).

const ICONS = {
  dashboard: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="9"/><rect x="14" y="3" width="7" height="5"/><rect x="14" y="12" width="7" height="9"/><rect x="3" y="16" width="7" height="5"/></svg>`,
  processes: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/></svg>`,
  risks: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,
  ai: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a5 5 0 0 1 5 5v2a5 5 0 0 1-10 0V7a5 5 0 0 1 5-5z"/><path d="M8 14v2a4 4 0 0 0 8 0v-2"/><line x1="12" y1="20" x2="12" y2="22"/></svg>`,
  audit: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>`,
};

const NAV_ITEMS = [
  { key: "dashboard", label: "Dashboard", href: "app.html" },
  { key: "processes", label: "Processos", href: "processes.html" },
  { key: "risks", label: "Riscos", href: "risks.html" },
  { key: "ai", label: "AI Risk Analyzer", href: "ai-analyzer.html" },
  { key: "audit", label: "Auditoria", href: "audit.html" },
];

export function renderSidebar(activeKey) {
  const links = NAV_ITEMS.map((item) => {
    const activeClass = item.key === activeKey ? "sidebar__link--active" : "";
    return `
      <a href="${item.href}" class="sidebar__link ${activeClass}">
        ${ICONS[item.key]}
        <span>${item.label}</span>
      </a>
    `;
  }).join("");

  return `
    <aside class="sidebar">
      <div>
        <div class="sidebar__brand">NEXUS</div>
        <nav class="sidebar__nav">${links}</nav>
      </div>
      <div class="sidebar__footer">
        <div class="sidebar__user-name" id="user-name">Carregando...</div>
        <div class="sidebar__user-role" id="user-role"></div>
        <button class="btn-logout" id="logout-btn" style="width:100%;">Sair</button>
      </div>
    </aside>
  `;
}
