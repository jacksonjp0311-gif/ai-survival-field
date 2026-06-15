function gatePosition(id) {
  const positions = [
    [110, 170], [150, 230], [190, 290], [230, 350], [270, 410],
    [315, 470], [320, 120], [380, 90], [450, 76], [520, 90],
    [580, 120], [635, 170], [685, 225], [745, 285], [770, 350],
    [750, 415], [700, 475], [630, 520], [555, 548], [480, 555],
    [405, 548], [330, 520], [260, 475], [200, 415], [155, 350],
  ];
  return positions[id - 1] || [450, 310];
}

function drawGeometry(state) {
  const svg = document.getElementById("triad");
  svg.innerHTML = "";
  const ns = "http://www.w3.org/2000/svg";
  function el(name, attrs = {}) {
    const node = document.createElementNS(ns, name);
    for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
    return node;
  }
  svg.appendChild(el("path", { class: "edge", d: "M450 55 L95 555 L805 555 Z" }));
  svg.appendChild(el("path", { class: "inner", d: "M450 220 L330 410 L570 410 Z" }));
  [["∿ Evidence / Rehydration", 150, 585], ["Governance / Coherence", 450, 38], ["Action / Recovery", 745, 585]].forEach(([label, x, y]) => {
    const text = el("text", { x, y, fill: "#4ddcff", "font-size": 18, "text-anchor": "middle" });
    text.textContent = label;
    svg.appendChild(text);
  });
  for (const gate of state.gates) {
    const [x, y] = gatePosition(gate.gate_id);
    const group = el("g", { class: `gate ${gate.status}` });
    group.appendChild(el("circle", { cx: x, cy: y, r: 21 }));
    const idText = el("text", { x, y: y - 3 });
    idText.textContent = gate.gate_id;
    const labelText = el("text", { x, y: y + 12 });
    labelText.textContent = gate.label.split(" ")[0];
    group.appendChild(idText);
    group.appendChild(labelText);
    const title = el("title");
    title.textContent = `${gate.gate_id}. ${gate.label}\n${gate.status}\n${gate.pass_condition}`;
    group.appendChild(title);
    svg.appendChild(group);
  }
}
