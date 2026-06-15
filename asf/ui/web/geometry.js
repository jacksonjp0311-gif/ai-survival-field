function svgEl(name, attrs = {}) {
  const node = document.createElementNS("http://www.w3.org/2000/svg", name);
  for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
  return node;
}

function drawGeometry(state) {
  const svg = document.getElementById("triad");
  svg.innerHTML = "";
  svg.appendChild(svgEl("path", { class: "edge", d: "M520 84 L250 520 L790 520 Z" }));
  svg.appendChild(svgEl("path", { class: "inner", d: "M520 235 L370 470 L670 470 Z" }));
  svg.appendChild(svgEl("path", { class: "gate-path", d: gatePath(state.gates) }));
  drawBackgroundRings(svg);
  drawVertex(svg, 520, 86, "∿", "Evidence /", "Rehydration");
  drawVertex(svg, 350, 470, "△", "Governance /", "Coherence");
  drawVertex(svg, 690, 470, "↧", "Action /", "Recovery");
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
  const t1 = svgEl("text", { x, y: y - 54, fill: "#e8fbff", "font-size": 16, "text-anchor": "middle", "font-weight": "700" });
  t1.textContent = a;
  const t2 = svgEl("text", { x, y: y - 34, fill: "#e8fbff", "font-size": 16, "text-anchor": "middle", "font-weight": "700" });
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
  label.textContent = gate.label;
  group.appendChild(label);
  const title = svgEl("title");
  title.textContent = `${gate.gate_id}. ${gate.label}\n${gate.status}\n${gate.pass_condition}`;
  group.appendChild(title);
  group.addEventListener("click", () => showGate(gate));
  svg.appendChild(group);
}

function gatePath(gates) {
  if (!gates.length) return "";
  return gates.map((gate, index) => `${index === 0 ? "M" : "L"}${gate.x} ${gate.y}`).join(" ") + " Z";
}

function drawWoundLink(svg, state) {
  const gate = state.gates.find(item => item.gate_id === state.failed_gate_id);
  if (!gate) return;
  svg.appendChild(svgEl("path", { class: "wound-link", d: `M${gate.x + 18} ${gate.y} C760 ${gate.y}, 840 510, 1030 510` }));
}

function showGate(gate) {
  const drawer = document.getElementById("gate-drawer");
  drawer.hidden = false;
  drawer.innerHTML = `<strong>Gate ${gate.gate_id}: ${gate.label}</strong><br>Status: ${gate.status}<br>Sector: ${gate.sector}<br>${gate.pass_condition}`;
}
