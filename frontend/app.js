const state = {
  summaryText: "",
};

const $ = (selector) => document.querySelector(selector);

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const message = await response.text();
    let parsedError = "";
    try {
      parsedError = JSON.parse(message).error || "";
    } catch {
      // Use the plain response text below.
    }
    throw new Error(parsedError || message || `API 오류: ${response.status}`);
  }
  return response.json();
}

function setupNavigation() {
  $("#projectNavigation")?.addEventListener("click", (event) => {
    const button = event.target.closest(".nav-item");
    if (!button) return;
    document.querySelectorAll(".nav-item").forEach((item) => item.classList.remove("active"));
    document.querySelectorAll(".project-view").forEach((view) => view.classList.remove("active"));
    button.classList.add("active");
    document.getElementById(button.dataset.project)?.classList.add("active");
  });
}

function setupSidebarMenuToggle() {
  const button = $("#sidebarMenuButton");
  const nav = $("#projectNavigation");
  if (!button || !nav) return;
  nav.classList.remove("collapsed");
  button.setAttribute("aria-expanded", "true");
  updateProjectNavHeight();
  button.addEventListener("click", () => {
    const collapsed = nav.classList.toggle("collapsed");
    button.setAttribute("aria-expanded", String(!collapsed));
    updateProjectNavHeight();
  });
  window.addEventListener("resize", updateProjectNavHeight);
}

function updateProjectNavHeight() {
  const nav = $("#projectNavigation");
  if (!nav) return;
  nav.style.maxHeight = nav.classList.contains("collapsed") ? "0px" : `${nav.scrollHeight}px`;
}

function setupPanelToggles() {
  document.querySelectorAll(".panel-toggle").forEach((button) => {
    const target = document.getElementById(button.dataset.toggleTarget);
    button.setAttribute("aria-expanded", String(!target?.classList.contains("collapsed")));
    button.addEventListener("click", () => {
      const panelBody = document.getElementById(button.dataset.toggleTarget);
      if (!panelBody) return;
      const collapsed = panelBody.classList.toggle("collapsed");
      button.textContent = collapsed ? "펼치기" : "접기";
      button.setAttribute("aria-expanded", String(!collapsed));
    });
  });
}

function setupSummaryActions() {
  $("#summaryButton")?.addEventListener("click", () => runSummary(false));
  $("#sendSimulationButton")?.addEventListener("click", () => runSummary(true));
  $("#summaryCopyButton")?.addEventListener("click", async () => {
    await navigator.clipboard.writeText(state.summaryText);
    $("#summaryStatus").textContent = "요약을 클립보드에 복사했습니다.";
  });
}

async function runSummary(simulateSend) {
  const summaryButton = $("#summaryButton");
  const sendButton = $("#sendSimulationButton");
  const copyButton = $("#summaryCopyButton");
  summaryButton.disabled = true;
  sendButton.disabled = true;
  copyButton.disabled = true;
  $("#summaryStatus").textContent = simulateSend ? "전송 흐름을 시뮬레이션하는 중입니다..." : "전체 요약을 생성하는 중입니다...";
  $("#summaryTextOutput").value = "";

  try {
    const result = await api("/api/prototype/summary", {
      method: "POST",
      body: JSON.stringify({ simulate_send: simulateSend }),
    });
    state.summaryText = result.summary || "";
    $("#summaryTextOutput").value = state.summaryText;
    $("#summaryStatus").textContent = result.message || "완료되었습니다.";
    renderProjectList(result.projects || []);
    copyButton.disabled = !state.summaryText;
  } catch (error) {
    $("#summaryStatus").textContent = error.message;
  } finally {
    summaryButton.disabled = false;
    sendButton.disabled = false;
  }
}

function renderProjectList(projects) {
  const container = $("#summaryProjectList");
  const count = $("#summaryProjectCount");
  if (!container || !count) return;
  count.textContent = `${projects.length}개`;
  container.innerHTML = "";

  const groups = [
    {
      title: "META PROJECT",
      description: "프로젝트를 설명, 요약, 관리하는 메타 화면입니다.",
      projects: projects.filter((project) => project.category === "meta_project"),
    },
    {
      title: "NORMAL PROJECT",
      description: "일반 기능 구현과 사용자용 실험 프로젝트가 들어갑니다.",
      projects: projects.filter((project) => project.category === "normal_project"),
    },
  ];

  groups.forEach((group) => {
    if (!group.projects.length) return;
    const section = document.createElement("section");
    section.className = "project-list-group";
    section.innerHTML = `
      <div class="project-list-group-head">
        <strong>${escapeHtml(group.title)}</strong>
        <small>${escapeHtml(group.description)}</small>
      </div>
    `;
    group.projects.forEach((project) => {
      const item = document.createElement("article");
      item.className = "item-card";
      item.innerHTML = `
        <div class="item-title">${escapeHtml(project.name)}</div>
        <div class="article-summary">${escapeHtml(project.description)}</div>
        <div class="item-actions">
          <span class="badge">${escapeHtml(project.category)}</span>
        </div>
      `;
      section.appendChild(item);
    });
    container.appendChild(section);
  });
}

async function loadMetaSettings() {
  const payload = await api("/api/meta_project/settings");
  renderProjectList(payload.projects || []);
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

setupNavigation();
setupSidebarMenuToggle();
setupPanelToggles();
setupSummaryActions();
loadMetaSettings().catch((error) => {
  $("#summaryStatus").textContent = error.message;
});
