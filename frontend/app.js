const state = {
  metaProjects: [],
  metaSelectedProjects: [],
  zones: [],
  dailyNewsText: "",
  flightText: "",
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

async function loadZones() {
  state.zones = await api("/api/traffic_monitor/zones");
  renderZones({
    count: $("#flightZoneCount"),
    container: $("#flightZones"),
    enabledKey: "aircraft_enabled",
    disabledText: "항공 제외",
  });
}

async function loadMetaSettings() {
  const payload = await api("/api/meta_project/settings");
  state.metaProjects = payload.projects || [];
  state.metaSelectedProjects = payload.settings?.selected_projects || [];
  renderDailyNewsManager();
}

function dailyMonitorProjects() {
  return state.metaProjects.filter((project) => project.category === "project");
}

function renderDailyNewsManager() {
  const projects = dailyMonitorProjects();
  $("#dailyNewsProjectCount").textContent = `${projects.length}개`;
  const container = $("#dailyNewsProjectList");
  container.innerHTML = "";
  projects.forEach((project) => {
    const checked = state.metaSelectedProjects.includes(project.id) ? "checked" : "";
    const item = document.createElement("label");
    item.className = "checkbox-card";
    item.innerHTML = `
      <input type="checkbox" value="${escapeHtml(project.id)}" ${checked} />
      <span>
        <strong>${escapeHtml(project.name)}</strong>
        <small>${escapeHtml(project.description)}</small>
      </span>
    `;
    container.appendChild(item);
  });
}

function selectedDailyMonitorProjectIds() {
  const selected = [...document.querySelectorAll("#dailyNewsProjectList input[type='checkbox']:checked")].map(
    (input) => input.value
  );
  if (selected.length) return selected;
  return dailyMonitorProjects().map((project) => project.id);
}

function setupDailyNewsManager() {
  $("#dailyNewsScrapeButton")?.addEventListener("click", async () => {
    await runDailyNewsScrape({
      path: "/api/meta_project/scrape",
      loading: "Daily Monitor 프로젝트를 수집하고 요약하는 중입니다...",
      telegram: false,
    });
  });

  $("#dailyNewsTelegramButton")?.addEventListener("click", async () => {
    await runDailyNewsScrape({
      path: "/api/meta_project/scrape-and-send",
      loading: "Daily Monitor 프로젝트를 수집하고 요약한 뒤 텔레그램으로 전송하는 중입니다...",
      telegram: true,
    });
  });

  $("#dailyNewsCopyButton")?.addEventListener("click", async () => {
    await navigator.clipboard.writeText(state.dailyNewsText);
    $("#dailyNewsStatus").textContent = "텍스트를 클립보드에 복사했습니다.";
  });
}

async function runDailyNewsScrape({ path, loading, telegram }) {
  const scrapeButton = $("#dailyNewsScrapeButton");
  const telegramButton = $("#dailyNewsTelegramButton");
  const copyButton = $("#dailyNewsCopyButton");
  scrapeButton.disabled = true;
  telegramButton.disabled = true;
  copyButton.disabled = true;
  $("#dailyNewsStatus").textContent = loading;
  $("#dailyNewsTextOutput").value = "";
  $("#dailyNewsResults").innerHTML = "";

  try {
    const selectedProjects = selectedDailyMonitorProjectIds();
    const result = await api(path, {
      method: "POST",
      body: JSON.stringify({ selected_projects: selectedProjects }),
    });
    state.metaSelectedProjects = result.selected_projects || selectedProjects;
    state.dailyNewsText = formatMetaReport(result);
    $("#dailyNewsTextOutput").value = state.dailyNewsText;
    renderMetaResults(result.results || [], $("#dailyNewsResults"));
    const errorText = result.errors?.length ? `, 오류 ${result.errors.length}건` : "";
    const telegramText = telegram && result.telegram ? ` 텔레그램 ${result.telegram.message_count || 0}건 전송 완료.` : "";
    $("#dailyNewsStatus").textContent = `${result.count}개 구역의 통합 결과를 정리했습니다${errorText}.${telegramText}`;
    copyButton.disabled = !state.dailyNewsText;
    renderDailyNewsManager();
  } catch (error) {
    $("#dailyNewsStatus").textContent = error.message;
  } finally {
    scrapeButton.disabled = false;
    telegramButton.disabled = false;
  }
}

function renderZones({ count, container, enabledKey, disabledText }) {
  count.textContent = `${state.zones.length}개`;
  container.innerHTML = "";
  state.zones.forEach((zone) => {
    const enabled = zone.enabled && zone[enabledKey];
    const item = document.createElement("article");
    item.className = "item-card";
    item.innerHTML = `
      <div class="item-title">${escapeHtml(zone.name)}</div>
      <div class="article-meta">${escapeHtml(zone.region)} · ${zone.refresh_minutes}분 주기</div>
      <div class="article-summary">${escapeHtml(zone.notes || "모니터링 메모가 없습니다.")}</div>
      <div class="item-actions">
        <span class="badge ${enabled ? "" : "off"}">${enabled ? "사용 중" : disabledText}</span>
      </div>
    `;
    container.appendChild(item);
  });
}

function setupMonitorProject(config) {
  config.button.addEventListener("click", async () => {
    config.button.disabled = true;
    config.copy.disabled = true;
    config.status.textContent = `${config.name} 모니터링 스캐폴드를 평가하는 중입니다...`;
    config.output.value = "";
    config.snapshots.innerHTML = "";

    try {
      const result = await api(config.path, { method: "POST", body: JSON.stringify({}) });
      const text = formatMonitorReport(config.name, result);
      config.setText(text);
      config.output.value = text;
      renderSnapshots(result.snapshots || [], config.snapshots);
      config.status.textContent = `${result.count}개 구역의 ${config.name} 모니터링 계획을 정리했습니다.`;
      config.copy.disabled = !text;
    } catch (error) {
      config.status.textContent = error.message;
    } finally {
      config.button.disabled = false;
    }
  });

  config.copy.addEventListener("click", async () => {
    await navigator.clipboard.writeText(config.getText());
    config.status.textContent = "텍스트를 클립보드에 복사했습니다.";
  });
}

function renderSnapshots(snapshots, container) {
  container.innerHTML = "";
  snapshots.forEach((snapshot) => {
    const item = document.createElement("article");
    item.className = "item-card";
    const sources = (snapshot.sources || [])
      .map((source) => `${escapeHtml(source.label || source.provider)}: ${escapeHtml(source.status)}`)
      .join(" · ");
    item.innerHTML = `
      <div class="item-title">${escapeHtml(snapshot.zone_name)}</div>
      <div class="article-meta">${escapeHtml(snapshot.region)} · ${snapshot.refresh_minutes}분 주기</div>
      <div class="article-summary">${escapeHtml(snapshot.notes || "모니터링 메모가 없습니다.")}</div>
      <div class="muted">${sources || "활성화된 데이터 소스가 없습니다."}</div>
    `;
    container.appendChild(item);
  });
}

function renderMetaResults(results, container) {
  container.innerHTML = "";
  results.forEach((projectResult) => {
    const group = document.createElement("section");
    group.className = "source-group";
    group.innerHTML = `
      <div class="source-head">
        <div>
          <div class="source-title">${escapeHtml(projectResult.project_name)}</div>
          <div class="muted">${projectResult.result?.count || 0}개 구역</div>
        </div>
      </div>
    `;
    const body = document.createElement("div");
    body.className = "source-articles";
    renderSnapshots(projectResult.result?.snapshots || [], body);
    group.appendChild(body);
    container.appendChild(group);
  });
}

function formatMetaReport(result) {
  const lines = ["# Daily Monitor 통합 보고서", `생성 시각: ${formatKstTime(result.generated_at)}`, `구역 수: ${result.count}`, ""];
  (result.results || []).forEach((projectResult, index) => {
    if (index > 0) {
      lines.push("============================================================");
      lines.push("");
    }
    lines.push(`## ${projectResult.project_name}`);
    lines.push(formatMonitorReport(projectResult.project_name, projectResult.result));
    lines.push("");
  });
  if (result.errors?.length) {
    lines.push("## 오류");
    result.errors.forEach((error) => lines.push(`- ${error.project}: ${error.message}`));
  }
  return lines.join("\n");
}

function formatMonitorReport(name, result) {
  const lines = [`# ${name} 모니터링`, `생성 시각: ${formatKstTime(result.generated_at)}`, `구역 수: ${result.count}`, ""];
  (result.snapshots || []).forEach((snapshot, index) => {
    lines.push(`${index + 1}. ${snapshot.zone_name}`);
    lines.push(`   - 지역: ${snapshot.region}`);
    lines.push(`   - 갱신 주기: ${snapshot.refresh_minutes}분`);
    (snapshot.sources || []).forEach((source) => {
      lines.push(`   - ${source.label || source.provider}: ${source.status} (${source.summary})`);
    });
    if (snapshot.notes) lines.push(`   - 메모: ${snapshot.notes}`);
    lines.push("");
  });
  if (result.telegram?.summary) {
    lines.push(`Telegram: ${result.telegram.status} - ${result.telegram.summary}`);
  }
  return lines.join("\n");
}

function formatKstTime(value) {
  return `${new Date(value).toLocaleString("ko-KR", { timeZone: "Asia/Seoul" })} KST (UTC+9)`;
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
setupDailyNewsManager();
setupMonitorProject({
  name: "FlightRadar24",
  path: "/api/flightradar24/monitor",
  button: $("#flightMonitorButton"),
  copy: $("#flightCopyButton"),
  status: $("#flightStatus"),
  output: $("#flightTextOutput"),
  snapshots: $("#flightSnapshots"),
  setText: (text) => {
    state.flightText = text;
  },
  getText: () => state.flightText,
});
loadZones().catch((error) => {
  $("#flightStatus").textContent = error.message;
});
loadMetaSettings().catch((error) => {
  $("#dailyNewsStatus").textContent = error.message;
});
