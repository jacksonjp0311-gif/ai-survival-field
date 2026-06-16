function svgEl(name, attrs = {}) {
  const node = document.createElementNS("http://www.w3.org/2000/svg", name);
  for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
  return node;
}

function drawGeometry(state) {
  const svg = document.getElementById("triad");
  svg.innerHTML = "";
  const geom = geometryModel();
  drawBackgroundRings(svg);
  svg.appendChild(svgEl("circle", { class: "gate-orbit", cx: geom.cx, cy: geom.cy, r: geom.gateRadius }));
  svg.appendChild(svgEl("path", { class: "edge", d: trianglePath(geom.triangle) }));
  svg.appendChild(svgEl("path", { class: "inner", d: innerTrianglePath(geom) }));
  drawVertex(svg, geom.triangle.top.x, geom.triangle.top.y, "∿", "Evidence /", "Rehydration");
  drawVertex(svg, geom.triangle.left.x, geom.triangle.left.y, "△", "Governance /", "Coherence");
  drawVertex(svg, geom.triangle.right.x, geom.triangle.right.y, "↧", "Action /", "Recovery");
  drawCore(svg);
  if (state.trace && state.trace.visible && state.trace.display === "full") drawWoundLink(svg, state);
  if (state.trace && state.trace.visible && state.trace.display === "collapsed") drawArchivedWoundMarker(svg, state);
  for (const gate of state.gates) drawGate(svg, gate);
}

function geometryModel() {
  const cx = 490;
  const cy = 345;
  const triangleRadius = 185;
  return {
    cx,
    cy,
    gateRadius: 245,
    triangleRadius,
    triangle: {
      top: polar(cx, cy, -90, triangleRadius),
      left: polar(cx, cy, 150, triangleRadius),
      right: polar(cx, cy, 30, triangleRadius),
    },
  };
}

function polar(cx, cy, angle, radius) {
  const theta = angle * Math.PI / 180;
  return {
    x: Math.round(cx + radius * Math.cos(theta)),
    y: Math.round(cy + radius * Math.sin(theta)),
  };
}

function trianglePath(triangle) {
  return `M${triangle.top.x} ${triangle.top.y} L${triangle.left.x} ${triangle.left.y} L${triangle.right.x} ${triangle.right.y} Z`;
}

function innerTrianglePath(geom) {
  const radius = 118;
  const top = polar(geom.cx, geom.cy, -90, radius);
  const left = polar(geom.cx, geom.cy, 150, radius);
  const right = polar(geom.cx, geom.cy, 30, radius);
  return `M${top.x} ${top.y} L${left.x} ${left.y} L${right.x} ${right.y} Z`;
}

function drawBackgroundRings(svg) {
  for (const r of [118, 185, 245, 287]) {
    svg.appendChild(svgEl("circle", {
      cx: 490, cy: 345, r, fill: "none",
      stroke: "rgba(77,220,255,0.08)", "stroke-width": 1,
    }));
  }
}

function drawVertex(svg, x, y, glyph, a, b) {
  svg.appendChild(svgEl("circle", { class: "vertex-core", cx: x, cy: y, r: 30 }));
  const g = svgEl("text", { x, y: y + 9, fill: "#e8fbff", "font-size": 28, "text-anchor": "middle" });
  g.textContent = glyph;
  svg.appendChild(g);
  const isTop = y < 220;
  const labelY = isTop ? y + 50 : y - 54;
  const labelSize = isTop ? 14 : 16;
  const t1 = svgEl("text", { x, y: labelY, fill: "#e8fbff", "font-size": labelSize, "text-anchor": "middle", "font-weight": "700" });
  t1.textContent = a;
  const t2 = svgEl("text", { x, y: labelY + 18, fill: "#e8fbff", "font-size": labelSize, "text-anchor": "middle", "font-weight": "700" });
  t2.textContent = b;
  svg.appendChild(t1);
  svg.appendChild(t2);
}

function drawCore(svg) {
  svg.appendChild(svgEl("circle", { class: "core-circle", cx: 490, cy: 345, r: 64 }));
  [["ASF-R", 325, 22], ["Runtime", 350, 20], ["Geometry", 375, 20], ["READ-ONLY", 403, 11]].forEach(([text, y, size]) => {
    const node = svgEl("text", { x: 490, y, fill: text === "READ-ONLY" ? "#4ddcff" : "#f2fbff", "font-size": size, "text-anchor": "middle", "font-weight": "700" });
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
  const label = svgEl("text", {
    class: "gate-label",
    x: gate.label_x,
    y: gate.label_y,
    "text-anchor": gate.label_anchor || "middle",
  });
  const lines = gate.label_lines || splitLabel(gate.label);
  const startDy = lines.length > 1 ? -5 : 0;
  for (const [index, line] of lines.entries()) {
    const tspan = svgEl("tspan", {
      x: gate.label_x,
      dy: index === 0 ? startDy : 12,
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
  const trace = state.trace || {};
  let startX;
  let startY;
  if (trace.source === "failed_gate" && state.failed_gate_id) {
    const gate = state.gates.find(item => item.gate_id === state.failed_gate_id && item.failed);
    if (!gate) return;
    startX = gate.x + 18;
    startY = gate.y;
  } else {
    const source = state.wound_source_node;
    if (!source || !source.visible) return;
    drawWoundSourceNode(svg, source, trace.mode);
    startX = source.x + 10;
    startY = source.y;
  }
  const midX = 812;
  const endX = 1032;
  const woundY = 486;
  svg.appendChild(svgEl("path", {
    class: `circuit-trace ${trace.mode || "active"}`,
    d: `M${startX} ${startY} H${midX} Q${midX + 8} ${startY} ${midX + 8} ${startY + 8} V${woundY - 8} Q${midX + 8} ${woundY} ${midX + 16} ${woundY} H${endX}`,
  }));
  for (const [x, y] of [[startX, startY], [midX + 8, Math.round((startY + woundY) / 2)], [endX, woundY]]) {
    svg.appendChild(svgEl("circle", { class: "circuit-pad", cx: x, cy: y, r: 3.5 }));
  }
}

function drawWoundSourceNode(svg, source, mode = "active") {
  const group = svgEl("g", { class: `wound-source-node ${mode}` });
  group.appendChild(svgEl("circle", { cx: source.x, cy: source.y, r: 9 }));
  if (mode !== "archived") {
    const label = svgEl("text", { x: source.x + 14, y: source.y - 8, "text-anchor": "start" });
    label.textContent = source.label || "Wound Source";
    group.appendChild(label);
  }
  const title = svgEl("title");
  title.textContent = `${mode === "archived" ? "Archived wound" : "Wound source"}: ${source.label || "Wound Source"}`;
  group.appendChild(title);
  svg.appendChild(group);
}

function drawArchivedWoundMarker(svg, state) {
  const source = state.wound_source_node || { x: 760, y: 474, label: "Wound Source" };
  const markerX = 815;
  const markerY = 486;
  const group = svgEl("g", { class: "archived-wound-marker" });
  group.appendChild(svgEl("path", {
    d: `M${source.x} ${source.y} C${source.x + 22} ${source.y} ${markerX - 28} ${markerY} ${markerX} ${markerY}`,
  }));
  group.appendChild(svgEl("circle", { cx: markerX, cy: markerY, r: 7 }));
  const title = svgEl("title");
  title.textContent = `Archived wound: ${state.wound_panel?.failed_gate || source.label || "Wound Source"}`;
  group.appendChild(title);
  svg.appendChild(group);
}

function showGate(gate) {
  const drawer = document.getElementById("gate-drawer");
  drawer.hidden = false;
  drawer.innerHTML = `<strong>Gate ${gate.gate_id}: ${gate.label}</strong><br>Status: ${gate.status}<br>Sector: ${gate.sector}<br>${gate.pass_condition}`;
}
