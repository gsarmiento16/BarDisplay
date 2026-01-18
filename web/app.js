const state = {
  config: null,
  menu: null,
  view: "menu",
  arrivals: new Map(),
};

const appEl = document.getElementById("app");
const boardTitleEl = document.getElementById("board-title");
const boardClockEl = document.getElementById("board-clock");
const arrivalsBody = document.getElementById("arrivals-body");
const menuTitleEl = document.getElementById("menu-title");
const menuTextEl = document.getElementById("menu-text");
const menuImageEl = document.getElementById("menu-image");
const imageCaptionEl = document.getElementById("image-caption");
const menuViewEl = document.getElementById("menu-view");
const imageViewEl = document.getElementById("image-view");
const menuViewsEl = document.querySelector(".menu-views");

function getTenantCode() {
  const parts = window.location.pathname.split("/").filter(Boolean);
  if (parts.length >= 2 && parts[0] === "t") {
    return parts[1];
  }
  return "";
}

function getLayoutOverride() {
  const params = new URLSearchParams(window.location.search);
  const layout = params.get("layout");
  if (layout === "horizontal" || layout === "vertical") {
    return layout;
  }
  return null;
}

function applyLayout(layout) {
  appEl.classList.remove("layout-horizontal", "layout-vertical");
  appEl.classList.add(`layout-${layout}`);
}

function applyTheme(theme) {
  appEl.classList.remove("theme-purple", "theme-amber", "theme-dark");
  appEl.classList.add(`theme-${theme}`);
}

async function fetchJson(url) {
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return await response.json();
}

function updateClock() {
  const now = new Date();
  boardClockEl.textContent = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function updateArrivals(items) {
  const existing = new Map();
  arrivalsBody.querySelectorAll("tr").forEach((row) => {
    existing.set(row.dataset.key, row);
  });

  const seen = new Set();

  items.forEach((item) => {
    const key = `${item.stop}-${item.line}-${item.destination}`;
    let row = existing.get(key);
    if (!row) {
      row = document.createElement("tr");
      row.dataset.key = key;
      row.innerHTML = `
        <td class="cell-stop"></td>
        <td class="cell-line"></td>
        <td class="cell-destination"></td>
        <td class="cell-eta"></td>
      `;
      arrivalsBody.appendChild(row);
    }

    row.querySelector(".cell-stop").textContent = item.stop;
    row.querySelector(".cell-line").textContent = item.line;
    row.querySelector(".cell-destination").textContent = item.destination;

    row.dataset.etaBase = String(item.etaSeconds);
    row.dataset.etaFetchedAt = String(Date.now());
    renderEta(row);

    seen.add(key);
  });

  existing.forEach((row, key) => {
    if (!seen.has(key)) {
      row.remove();
    }
  });
}

function renderEta(row) {
  const etaCell = row.querySelector(".cell-eta");
  const base = Number(row.dataset.etaBase || 0);
  const fetchedAt = Number(row.dataset.etaFetchedAt || Date.now());
  const elapsedSeconds = Math.floor((Date.now() - fetchedAt) / 1000);
  const remaining = base - elapsedSeconds;
  if (remaining <= 0) {
    updateEtaCell(etaCell, "Now");
    return;
  }

  const minutes = Math.ceil(remaining / 60);
  if (minutes >= 60) {
    const hours = Math.ceil(minutes / 60);
    updateEtaCell(etaCell, `${hours} Hrs`);
    return;
  }

  updateEtaCell(etaCell, `${minutes} min`);
}

function updateEtaCell(etaCell, label) {
  if (etaCell.dataset.etaLabel !== label) {
    etaCell.textContent = label;
    etaCell.dataset.etaLabel = label;
    etaCell.classList.remove("eta-bump");
    void etaCell.offsetWidth;
    etaCell.classList.add("eta-bump");
  }
}

function tickEtaCountdown() {
  arrivalsBody.querySelectorAll("tr").forEach((row) => {
    if (row.dataset.etaBase) {
      renderEta(row);
    }
  });
}

async function loadConfig(code) {
  const config = await fetchJson(`/api/tenants/${code}/config`);
  state.config = config;
  const layout = getLayoutOverride() || config.layout || "horizontal";
  applyLayout(layout);
  applyTheme(config.theme || "purple");
  boardTitleEl.textContent = config.boardHeaderText || "Bus arriving at nearby stops";
  return config;
}

async function loadArrivals(code) {
  const arrivals = await fetchJson(`/api/tenants/${code}/arrivals`);
  updateArrivals(arrivals.items || []);
}

function renderMenu(menu) {
  state.menu = menu;
  menuTitleEl.textContent = menu.title || "Menu of the day";
  menuTextEl.textContent = menu.textRaw || "Menu will appear here.";
  if (menu.featuredImageUrl) {
    menuImageEl.src = menu.featuredImageUrl;
    imageCaptionEl.textContent = "";
  }
}

async function loadMenu(code) {
  const menu = await fetchJson(`/api/tenants/${code}/menu`);
  renderMenu(menu);
}

function swapMenuView() {
  if (!state.config || state.config.menuMode !== "menuAndImage") {
    menuViewEl.classList.add("is-active");
    imageViewEl.classList.remove("is-active");
    return;
  }

  if (!state.menu || !state.menu.featuredImageUrl) {
    menuViewEl.classList.add("is-active");
    imageViewEl.classList.remove("is-active");
    return;
  }

  state.view = state.view === "menu" ? "image" : "menu";
  if (state.view === "menu") {
    menuViewEl.classList.add("is-active");
    imageViewEl.classList.remove("is-active");
  } else {
    menuViewEl.classList.remove("is-active");
    imageViewEl.classList.add("is-active");
  }
}

async function init() {
  const code = getTenantCode();
  if (!code) {
    menuTextEl.textContent = "Missing tenant code.";
    return;
  }

  try {
    const config = await loadConfig(code);
    await Promise.all([loadArrivals(code), loadMenu(code)]);
    updateClock();

    setInterval(() => updateClock(), 1000 * 30);
    setInterval(() => loadArrivals(code), config.refreshSeconds * 1000);
    setInterval(() => loadMenu(code), config.refreshSeconds * 1000);
    setInterval(() => swapMenuView(), config.swapSeconds * 1000);
    setInterval(() => tickEtaCountdown(), 1000 * 10);
  } catch (error) {
    menuTextEl.textContent = "Failed to load tenant data.";
  }
}

init();
