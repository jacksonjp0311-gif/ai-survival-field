async function refresh() {
  const response = await fetch("/state.json", { cache: "no-store" });
  const state = await response.json();
  drawGeometry(state);
  document.getElementById("legend").textContent = Object.values(state.legend).join(" | ");
  document.getElementById("cli").textContent = JSON.stringify(state.cli_panel, null, 2);
  const wound = document.getElementById("wound");
  wound.textContent = JSON.stringify(state.wound_panel, null, 2);
  wound.parentElement.classList.toggle("blocked", state.wound_panel.status === "blocked");
  document.getElementById("law").innerHTML = state.read_only_law.map(item => `<li>${item}</li>`).join("");
  const strip = state.status_strip;
  document.getElementById("status").textContent =
    `VERSION ${strip.latest_version} | COMMIT ${strip.latest_commit} | SEAL ${strip.release_seal} | STATE ${strip.current_state} | ACTION ${strip.current_action} | DECISION ${strip.decision} | WOUND ${strip.wound_id} | CLOSURE ${strip.closure_status} | CI ${strip.ci_evidence_status}`;
}

refresh();
setInterval(refresh, 2500);
