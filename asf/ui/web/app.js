let latestState = null;

async function refresh() {
  const response = await fetch("/state.json", { cache: "no-store" });
  latestState = await response.json();
  renderState(latestState);
}

function renderState(state) {
  drawGeometry(state);
  document.getElementById("gate-count").textContent = `${state.gates.length} / 25`;
  renderCli(state.cli_panel);
  renderWound(state.wound_panel);
  renderCards(state.status_strip);
}

function renderCli(panel) {
  document.getElementById("command-line").textContent = `$ ${panel.command}`;
  document.getElementById("metric-phase").textContent = panel.phase;
  document.getElementById("metric-exit").textContent = `${panel.exit_code} (observe)`;
  document.getElementById("metric-follow").textContent = panel.follow ? "on" : "off";
  const stream = document.getElementById("cli-stream");
  stream.innerHTML = "";
  for (const line of panel.stream) {
    const row = document.createElement("div");
    row.className = `stream-line ${statusFromLine(line)}`;
    row.textContent = line;
    stream.appendChild(row);
  }
}

function statusFromLine(line) {
  const lower = line.toLowerCase();
  if (lower.includes("blocked")) return "blocked";
  if (lower.includes("pending")) return "pending";
  if (lower.includes("pass")) return "pass";
  return "";
}

function renderWound(panel) {
  const box = document.getElementById("wound-panel");
  const gate = document.getElementById("wound-gate");
  const fields = document.getElementById("wound-fields");
  box.classList.toggle("blocked", panel.status === "blocked");
  gate.textContent = panel.status === "blocked" ? `BLOCKED AT GATE ${panel.failed_gate_id || 12}` : "NO ACTIVE WOUND";
  if (panel.message) {
    fields.innerHTML = `<b>Status</b><span>${panel.message}</span>`;
    return;
  }
  const rows = [
    ["Wound ID", panel.wound_id],
    ["Failed Gate", `${panel.failed_gate_id || 12} ${panel.failed_gate || "Permission Checked"}`],
    ["Failure Class", panel.failure_class],
    ["Decision", panel.decision],
    ["Permission Ceiling", panel.permission_ceiling],
    ["Blocked Actions", (panel.blocked_actions || []).join(", ")],
    ["Permitted Actions", (panel.permitted_actions || []).join(", ")],
    ["Repair Path", "16 -> 17 -> 18 -> 19 -> 20 -> 21 -> 22"],
    ["Closure Status", panel.closure_status || "pending"],
  ];
  fields.innerHTML = rows.map(([key, value]) => `<b>${key}</b><span class="${key === "Decision" ? "hot" : ""}">${value || "unknown"}</span>`).join("");
}

function renderCards(strip) {
  const cards = [
    ["Version", strip.latest_version, "ok"],
    ["Commit", short(strip.latest_commit), ""],
    ["Release Seal", strip.release_seal, ""],
    ["Current State", strip.current_state, ""],
    ["Current Action", strip.current_action, ""],
    ["Decision", strip.decision, strip.decision === "pass" ? "ok" : "alert"],
    ["Permission Ceiling", strip.permission_ceiling, ""],
    ["Wound ID", strip.wound_id, strip.wound_id === "none" ? "" : "alert"],
    ["Authorization Receipt", strip.authorization_receipt_id, ""],
    ["Closure Status", strip.closure_status, strip.closure_status === "closed" ? "ok" : ""],
    ["CI Evidence Status", strip.ci_evidence_status, "ok"],
    ["Non-Claim Lock", "preserved", "ok"],
  ];
  document.getElementById("status-cards").innerHTML = cards.map(([label, value, status]) => {
    const long = String(value || "").length > 18 ? "long" : "";
    return `<div class="status-card ${status} ${long}"><label>${label}</label><strong>${value}</strong></div>`;
  }).join("");
}

function short(value) {
  return String(value || "unknown").slice(0, 8);
}

function connectEvents() {
  if (!window.EventSource) return;
  const source = new EventSource("/events");
  source.addEventListener("cli_line", event => {
    const payload = JSON.parse(event.data);
    const stream = document.getElementById("cli-stream");
    const row = document.createElement("div");
    row.className = `stream-line ${statusFromLine(payload.message)}`;
    row.textContent = payload.message;
    stream.appendChild(row);
    stream.scrollTop = stream.scrollHeight;
  });
  source.addEventListener("summary", () => refresh());
}

refresh();
connectEvents();
setInterval(refresh, 5000);
