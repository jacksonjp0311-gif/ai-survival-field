function svgEl(name, attrs = {}) {
  const node = document.createElementNS("http://www.w3.org/2000/svg", name);
  for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
  return node;
}

function drawGeometry(state) {
  const svg = document.getElementById("triad");
  svg.innerHTML = "";
  svg.appendChild(svgEl("path", { class: "edge", d: "M520 74 L252 512 L788 512 Z" }));
  svg.appendChild(svgEl("path", { class: "inner", d: "M520 220 L370 462 L670 462 Z" }));
  svg.appendChild(svgEl("path", { class: "gate-path", d: gatePath(state.gates) }));
  drawBackgroundRings(svg);
  drawVertex(svg, 520, 82, "∿", "Evidence /", "Rehydration");
  drawVertex(svg, 350, 468, "△", "Governance /", "Coherence");
  drawVertex(svg, 690, 468, "↧", "Action /", "Recovery");
  drawCore(svg);
  if (state.failed_gate_id) drawWoundLink(svg, state);
  for (const gate of state.gates) drawGate(svg, gate);
}

function drawBackgroundRings(svg) {
  for (const r of [142, 205, 268]) {
    svg.appendChild(svgEl("circle", {
      cx: 520, cy: 360, r, fill: "none",
      stroke: "rgba(77,220,255,0.08)", "stroke-width": 1,
    }));
  }
}

function drawVertex(svg, x, y, glyph, a, b) {
  svg.appendChild(svgEl("circle", { class: "vertex-core", cx: x, cy: y, r: 30 }));
  const g = svgEl("text", { x, y: y + 9, fill: "#e8fbff", "font-size": 28, "text-anchor": "middle" });
  g.textContent = glyph;
  svg.appendChild(g);
  const labelOffset = y < 120 ? 64 : 54;
  const t1 = svgEl("text", { x, y: y - labelOffset, fill: "#e8fbff", "font-size": 16, "text-anchor": "middle", "font-weight": "700" });
  t1.textContent = a;
  const t2 = svgEl("text", { x, y: y - labelOffset + 20, fill: "#e8fbff", "font-size": 16, "text-anchor": "middle", "font-weight": "700" });
  t2.textContent = b;
  svg.appendChild(t1);
  svg.appendChild(t2);
}

function drawCore(svg) {
  svg.appendChild(svgEl("circle", { class: "core-circle", cx: 520, cy: 360, r: 62 }));
  [["ASF-R", 340, 22], ["Runtime", 365, 20], ["Geometry", 390, 20], ["READ-ONLY", 418, 11]].forEach(([text, y, size]) => {
    const node = svgEl("text", { x: 520, y, fill: text === "READ-ONLY" ? "#4ddcff" : "#f2fbff", "font-size": size, "text-anchor": "middle", "font-weight": "700" });
    node.textContent = text;
    svg.appendChild(node);
  });
}

function drawGate(svg, gate) {
  const group = svgEl("g", { class: `gate ${gate.status}`, tabindex: "0" });
  group.appendChild(svgEl("circle", { cx: gate.x, cy: gate.y, r: 18 }));
  const number = svgEl("text", { class: "gate-number", x: gate.x, y: gate.y + 4 });
  number.textContent = gate.gate_id;
  group.appendChild(number);
  const label = svgEl("text", { class: "gate-label", x: gate.label_x, y: gate.label_y });
  for (const [index, line] of splitLabel(gate.label).entries()) {
    const tspan = svgEl("tspan", {
      x: gate.label_x,
      dy: index === 0 ? 0 : 12,
    });
    tspan.textContent = line;
    label.appendChild(tspan);
  }
  group.appendChild(label);
  const title = svgEl("title");
  title.textContent = `${gate.gate_id}. ${gate.label}\n${gate.status}\n${gate.pass_condition}`;
  group.appendChild(title);
  group.addEventListener("click", () => showGate(gate));
  svg.appendChild(group);
}

function splitLabel(label) {
  const hard = {
    "Latest Pointer Loaded": ["Latest Pointer", "Loaded"],
    "Rehydration Passed": ["Rehydration", "Passed"],
    "Release Seal Loaded": ["Release Seal", "Loaded"],
    "Repository Truth Aligned": ["Repository Truth", "Aligned"],
    "CI Evidence Loaded": ["CI Evidence", "Loaded"],
    "Claim Ceiling Assigned": ["Claim Ceiling", "Assigned"],
    "Artifact Validated": ["Artifact", "Validated"],
    "Decision Computed": ["Decision", "Computed"],
    "Permission Checked": ["Permission", "Checked"],
    "Non-Claim Lock Preserved": ["Non-Claim Lock", "Preserved"],
    "Block Enforcement Checked": ["Block Enforcement", "Checked"],
    "Wound Emitted": ["Wound", "Emitted"],
    "Repair Plan Created": ["Repair Plan", "Created"],
    "Repair Dry-Run Passed": ["Repair Dry-Run", "Passed"],
    "Repair Validation Passed": ["Repair Validation", "Passed"],
    "Repair Replay Passed": ["Repair Replay", "Passed"],
    "Authorization Bound": ["Authorization", "Bound"],
    "Bounded Repair Executed": ["Bounded Repair", "Executed"],
    "Post-Repair Evidence Captured": ["Post-Repair Evidence", "Captured"],
    "Closure Request Created": ["Closure Request", "Created"],
    "Closure Validation Passed": ["Closure Validation", "Passed"],
    "Closure Record Written": ["Closure Record", "Written"],
  };
  return hard[label] || [label];
}

function gatePath(gates) {
  if (!gates.length) return "";
  return gates.map((gate, index) => `${index === 0 ? "M" : "L"}${gate.x} ${gate.y}`).join(" ") + " Z";
}

function drawWoundLink(svg, state) {
  const gate = state.gates.find(item => item.gate_id === state.failed_gate_id);
  if (!gate) return;
  const startX = gate.x + 18;
  const startY = gate.y;
  const midX = Math.max(startX + 78, 710);
  const endX = 1032;
  const endY = 500;
  svg.appendChild(svgEl("path", {
    class: "wound-link",
    d: `M${startX} ${startY} C${midX} ${startY}, ${midX + 76} ${endY}, ${endX} ${endY}`,
  }));
}

function showGate(gate) {
  const drawer = document.getElementById("gate-drawer");
  drawer.hidden = false;
  drawer.innerHTML = `<strong>Gate ${gate.gate_id}: ${gate.label}</strong><br>Status: ${gate.status}<br>Sector: ${gate.sector}<br>${gate.pass_condition}`;
}
