const state = {
  config: null,
  menu: null,
  view: "menu",
  arrivals: new Map(),
  currentYoutubeEmbedSrc: null,
  weatherTimerId: null,
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
const menuPanelEl = document.querySelector(".menu-panel");
const youtubePanelEl = document.getElementById("youtube-panel");
const youtubeFrameEl = document.getElementById("youtube-frame");
const youtubePlaceholderEl = document.getElementById("youtube-placeholder");
const weatherBarEl = document.getElementById("weather-bar");
const weatherIconEl = document.getElementById("weather-icon");
const weatherTempEl = document.getElementById("weather-temp");
const weatherFeelsEl = document.getElementById("weather-feels");
const weatherDescEl = document.getElementById("weather-desc");
const weatherHumidityEl = document.getElementById("weather-humidity");
const weatherWindEl = document.getElementById("weather-wind");
const weatherUpdatedEl = document.getElementById("weather-updated");

let youtubeIframeEl = null;

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

function buildYoutubeEmbedUrl(rawUrl) {
  if (!rawUrl) {
    return null;
  }
  let parsed;
  try {
    parsed = new URL(rawUrl);
  } catch (error) {
    return null;
  }

  const host = parsed.hostname.toLowerCase();
  const path = parsed.pathname.replace(/^\/+/, "");
  let videoId = null;

  if (host.includes("youtu.be")) {
    if (path) {
      videoId = path.split("/")[0];
    }
  } else if (host.includes("youtube.com")) {
    if (path === "watch") {
      videoId = parsed.searchParams.get("v");
    } else if (path.startsWith("embed/")) {
      videoId = path.split("/")[1];
    }
  }

  if (!videoId) {
    return null;
  }

  return `https://www.youtube.com/embed/${videoId}?autoplay=1&mute=1&controls=0&rel=0&modestbranding=1&playsinline=1&enablejsapi=1`;
}

function setYoutubePlaceholder(message) {
  youtubePlaceholderEl.textContent = message;
  youtubePanelEl.classList.remove("is-loaded");
}

function handleYoutubeLoad() {
  youtubePanelEl.classList.add("is-loaded");
}

function handleYoutubeError() {
  setYoutubePlaceholder("Video unavailable");
  console.warn("YouTube embed failed to load.");
}

function ensureYoutubeIframe() {
  if (youtubeIframeEl) {
    return youtubeIframeEl;
  }

  youtubeIframeEl = document.createElement("iframe");
  youtubeIframeEl.allow = "autoplay; encrypted-media; picture-in-picture";
  youtubeIframeEl.referrerPolicy = "strict-origin-when-cross-origin";
  youtubeIframeEl.setAttribute("allowfullscreen", "");
  youtubeIframeEl.addEventListener("load", handleYoutubeLoad);
  youtubeIframeEl.addEventListener("error", handleYoutubeError);
  youtubeFrameEl.appendChild(youtubeIframeEl);
  return youtubeIframeEl;
}

function teardownYoutubeIframe() {
  if (youtubeIframeEl) {
    youtubeIframeEl.removeEventListener("load", handleYoutubeLoad);
    youtubeIframeEl.removeEventListener("error", handleYoutubeError);
    youtubeIframeEl.src = "about:blank";
    youtubeIframeEl.remove();
    youtubeIframeEl = null;
  }
  state.currentYoutubeEmbedSrc = null;
  youtubePanelEl.classList.remove("is-loaded");
}

function updateYoutubePanel() {
  if (!state.config || !state.config.showYoutube) {
    menuPanelEl.classList.remove("has-youtube");
    youtubePanelEl.classList.add("is-hidden");
    teardownYoutubeIframe();
    return;
  }

  menuPanelEl.classList.add("has-youtube");
  youtubePanelEl.classList.remove("is-hidden");

  const embedUrl = buildYoutubeEmbedUrl(state.config.youtubeUrl || "");
  if (!embedUrl) {
    setYoutubePlaceholder("Invalid YouTube URL");
    teardownYoutubeIframe();
    console.warn("Invalid YouTube URL:", state.config.youtubeUrl);
    return;
  }

  setYoutubePlaceholder("Video unavailable");
  const iframe = ensureYoutubeIframe();
  if (state.currentYoutubeEmbedSrc !== embedUrl) {
    state.currentYoutubeEmbedSrc = embedUrl;
    iframe.src = embedUrl;
  }
}

async function fetchJson(url) {
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return await response.json();
}

async function fetchWeatherJson(url) {
  const response = await fetch(url, { cache: "no-store" });
  if (response.status === 204) {
    return null;
  }
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

function formatTemp(value) {
  if (value === null || value === undefined) {
    return "--";
  }
  const rounded = Number(value);
  const label = rounded.toFixed(1).replace(/\.0$/, "");
  return `${label}°C`;
}

function formatUpdatedAt(value, isStale) {
  if (!value) {
    return "Updated --";
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return "Updated --";
  }
  const timeLabel = parsed.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  return isStale ? `Updated ${timeLabel} (stale)` : `Updated ${timeLabel}`;
}

function getWeatherIconSvg(kind, isNight) {
  if (kind === "clear" && isNight) {
    return `
      <svg viewBox="0 0 64 64" aria-hidden="true">
        <path class="moon" d="M42 14a18 18 0 1 0 8 34 20 20 0 1 1-8-34z"></path>
        <circle class="star" cx="18" cy="22" r="2"></circle>
        <circle class="star" cx="26" cy="12" r="1.5"></circle>
        <circle class="star" cx="14" cy="34" r="1.3"></circle>
      </svg>
    `;
  }
  if (kind === "clear") {
    return `
      <svg viewBox="0 0 64 64" aria-hidden="true">
        <g class="sun-ray">
          <line x1="32" y1="4" x2="32" y2="12"></line>
          <line x1="32" y1="52" x2="32" y2="60"></line>
          <line x1="4" y1="32" x2="12" y2="32"></line>
          <line x1="52" y1="32" x2="60" y2="32"></line>
          <line x1="12" y1="12" x2="18" y2="18"></line>
          <line x1="46" y1="46" x2="52" y2="52"></line>
          <line x1="12" y1="52" x2="18" y2="46"></line>
          <line x1="46" y1="18" x2="52" y2="12"></line>
        </g>
        <circle class="sun-core" cx="32" cy="32" r="12"></circle>
      </svg>
    `;
  }
  if (kind === "clouds") {
    return `
      <svg viewBox="0 0 64 64" aria-hidden="true">
        <ellipse class="cloud secondary" cx="26" cy="36" rx="18" ry="10"></ellipse>
        <ellipse class="cloud" cx="38" cy="30" rx="16" ry="9"></ellipse>
      </svg>
    `;
  }
  if (kind === "rain") {
    return `
      <svg viewBox="0 0 64 64" aria-hidden="true">
        <ellipse class="cloud secondary" cx="26" cy="28" rx="18" ry="10"></ellipse>
        <ellipse class="cloud" cx="40" cy="24" rx="16" ry="9"></ellipse>
        <line class="rain-drop" x1="22" y1="40" x2="22" y2="50"></line>
        <line class="rain-drop" x1="34" y1="40" x2="34" y2="52"></line>
        <line class="rain-drop" x1="46" y1="40" x2="46" y2="50"></line>
      </svg>
    `;
  }
  if (kind === "thunder") {
    return `
      <svg viewBox="0 0 64 64" aria-hidden="true">
        <ellipse class="cloud secondary" cx="26" cy="28" rx="18" ry="10"></ellipse>
        <ellipse class="cloud" cx="40" cy="24" rx="16" ry="9"></ellipse>
        <polygon class="bolt" points="34,34 26,50 34,50 28,62 46,42 36,42"></polygon>
      </svg>
    `;
  }
  if (kind === "snow") {
    return `
      <svg viewBox="0 0 64 64" aria-hidden="true">
        <ellipse class="cloud secondary" cx="26" cy="28" rx="18" ry="10"></ellipse>
        <ellipse class="cloud" cx="40" cy="24" rx="16" ry="9"></ellipse>
        <circle class="snow-flake" cx="24" cy="44" r="2"></circle>
        <circle class="snow-flake" cx="36" cy="48" r="2"></circle>
        <circle class="snow-flake" cx="46" cy="44" r="2"></circle>
      </svg>
    `;
  }
  return null;
}

function applyWeatherIcon(iconCode, isNight) {
  const normalized = (iconCode || "").slice(0, 2);
  let kind = "clouds";
  if (normalized === "01") {
    kind = "clear";
  } else if (normalized === "02" || normalized === "03" || normalized === "04") {
    kind = "clouds";
  } else if (normalized === "09" || normalized === "10") {
    kind = "rain";
  } else if (normalized === "11") {
    kind = "thunder";
  } else if (normalized === "13") {
    kind = "snow";
  }

  const svg = getWeatherIconSvg(kind, isNight);
  if (svg) {
    weatherIconEl.innerHTML = svg;
    return;
  }

  weatherIconEl.innerHTML = getWeatherIconSvg("clouds", isNight) || "";
}

function updateWeatherWidget(data) {
  if (!data) {
    weatherBarEl.classList.add("is-hidden");
    return;
  }

  weatherBarEl.classList.remove("is-hidden");
  weatherTempEl.textContent = formatTemp(data.tempC);
  weatherFeelsEl.textContent = `Feels ${formatTemp(data.feelsLikeC)}`;
  weatherDescEl.textContent = data.description || "--";
  weatherHumidityEl.textContent = `Humidity ${data.humidityPct ?? "--"}%`;
  weatherWindEl.textContent =
    data.windMps === null || data.windMps === undefined ? "Wind --" : `Wind ${data.windMps} m/s`;
  weatherUpdatedEl.textContent = formatUpdatedAt(data.updatedAt, data.stale);
  applyWeatherIcon(data.iconCode, data.isNight);
}

async function loadWeather(code) {
  if (!state.config || !state.config.showWeather) {
    weatherBarEl.classList.add("is-hidden");
    return;
  }

  weatherBarEl.classList.add("is-updating");
  try {
    const weather = await fetchWeatherJson(`/api/tenants/${code}/weather`);
    if (!weather) {
      weatherBarEl.classList.add("is-hidden");
      if (state.weatherTimerId) {
        clearInterval(state.weatherTimerId);
        state.weatherTimerId = null;
      }
      return;
    }
    updateWeatherWidget(weather);
  } catch (error) {
    console.warn("Weather update failed.", error);
  } finally {
    weatherBarEl.classList.remove("is-updating");
  }
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
  updateYoutubePanel();
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
  if (!state.config || state.config.showYoutube || state.config.menuMode !== "menuAndImage") {
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
    if (config.showWeather) {
      await loadWeather(code);
    }

    setInterval(() => updateClock(), 1000 * 30);
    setInterval(() => loadArrivals(code), config.refreshSeconds * 1000);
    setInterval(() => loadMenu(code), config.refreshSeconds * 1000);
    setInterval(() => swapMenuView(), config.swapSeconds * 1000);
    setInterval(() => tickEtaCountdown(), 1000 * 10);
    if (config.showWeather) {
      const refreshMs = (config.weatherRefreshSeconds || 600) * 1000;
      state.weatherTimerId = setInterval(() => loadWeather(code), refreshMs);
    }
  } catch (error) {
    menuTextEl.textContent = "Failed to load tenant data.";
  }
}

init();
