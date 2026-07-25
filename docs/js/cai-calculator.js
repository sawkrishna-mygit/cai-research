const topicNames = ["Acoustics", "Thermal", "Lighting", "Air"];
const topicKeys = ["ac", "th", "li", "air"];

let systems = [];
let projectData = null;

function el(id) {
  return document.getElementById(id);
}

function sign(x) {
  return x > 0 ? 1 : x < 0 ? -1 : 0;
}

function tauB(x, y) {
  let nc = 0;
  let nd = 0;
  let tiesX = 0;
  let tiesY = 0;
  const n = x.length;
  const pairs = (n * (n - 1)) / 2;
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      const sx = sign(x[i] - x[j]);
      const sy = sign(y[i] - y[j]);
      if (sx === 0) tiesX++;
      if (sy === 0) tiesY++;
      if (sx !== 0 && sy !== 0) {
        if (sx === sy) nc++;
        else nd++;
      }
    }
  }
  const den = Math.sqrt((pairs - tiesX) * (pairs - tiesY));
  return den ? (nc - nd) / den : 0;
}

function verdict(t) {
  if (t >= 0.5) return "aligned with occupant pain";
  if (t >= 0.1) return "weakly aligned";
  if (t > -0.1) return "nearly unrelated";
  if (t > -0.5) return "misaligned";
  return "strongly inverted";
}

function fmt(x, d = 1) {
  return Number(x).toFixed(d);
}

function sortSystems(list) {
  const order = { LEED: 0, WELL: 1, BREEAM: 2, Fitwel: 3 };
  return [...list].sort((a, b) => {
    const sys = order[a.system] - order[b.system];
    return sys !== 0 ? sys : a.year - b.year;
  });
}

function loadPreset(index) {
  const s = systems[index];
  el("acPts").value = s.ac;
  el("thPts").value = s.th;
  el("liPts").value = s.li;
  el("airPts").value = s.air;
  el("totalPts").value = s.total;
  calc();
}

function calc() {
  const pts = [
    Number(el("acPts").value),
    Number(el("thPts").value),
    Number(el("liPts").value),
    Number(el("airPts").value),
  ];
  const total = Math.max(1, Number(el("totalPts").value));
  const occ = [
    Number(el("acOcc").value),
    Number(el("thOcc").value),
    Number(el("liOcc").value),
    Number(el("airOcc").value),
  ];
  const pct = pts.map((p) => (100 * p) / total);
  const t = tauB(pct, occ);
  el("tauOut").textContent = (t >= 0 ? "+" : "") + t.toFixed(3);
  el("verdictOut").textContent = verdict(t);
  const pointOrder = topicNames
    .map((name, i) => [name, pct[i]])
    .sort((a, b) => b[1] - a[1])
    .map((x) => x[0]);
  const occOrder = topicNames
    .map((name, i) => [name, occ[i]])
    .sort((a, b) => b[1] - a[1])
    .map((x) => x[0]);
  el("orderOut").innerHTML =
    "<b>Certification rewards:</b> " +
    pointOrder.join(" > ") +
    "<br><b>Occupants complain:</b> " +
    occOrder.join(" > ");
  const gapList = el("gapList");
  gapList.innerHTML = "";
  let worstIndex = 0;
  topicNames.forEach((name, i) => {
    const gap = pct[i] - occ[i];
    if (gap < pct[worstIndex] - occ[worstIndex]) worstIndex = i;
    const row = document.createElement("div");
    row.className = "gap-item";
    row.innerHTML =
      "<b>" +
      name +
      "</b><div class='gap-sketch'><span style='--w:" +
      Math.min(96, Math.abs(gap) * 1.65) +
      "%'></span></div><b>" +
      (gap >= 0 ? "+" : "") +
      fmt(gap, 1) +
      "</b>";
    gapList.appendChild(row);
  });
  el("toolNote").textContent =
    "Most under-served topic: " +
    topicNames[worstIndex] +
    ". Certification gives it " +
    fmt(pct[worstIndex], 1) +
    "% of total points while occupant dissatisfaction benchmark is " +
    fmt(occ[worstIndex], 0) +
    "%.";
}

function fillTables() {
  const select = el("preset");
  select.innerHTML = "";
  systems.forEach((s, i) => {
    const opt = document.createElement("option");
    opt.value = String(i);
    opt.textContent = s.name + " (" + s.year + ")";
    select.appendChild(opt);
  });
  select.value = "0";
  select.addEventListener("change", () => loadPreset(Number(select.value)));
  ["acPts", "thPts", "liPts", "airPts", "totalPts", "acOcc", "thOcc", "liOcc", "airOcc"].forEach(
    (id) => {
      el(id).addEventListener("input", calc);
    }
  );

  const occ = projectData.occupant;
  el("acOcc").value = occ.Acoustics;
  el("thOcc").value = occ.Thermal;
  el("liOcc").value = occ.Lighting;
  el("airOcc").value = occ.Air;
  loadPreset(0);

  const rows = el("summaryRows");
  rows.innerHTML = "";
  systems.forEach((s) => {
    const tr = document.createElement("tr");
    tr.innerHTML =
      "<td>" +
      s.system +
      "</td><td>" +
      s.version +
      "</td><td>" +
      s.year +
      "</td><td class='num bad'>" +
      s.tau.toFixed(3) +
      "</td><td class='num'>" +
      (s.ci_lower !== null ? s.ci_lower.toFixed(3) : "—") +
      "</td><td class='num'>" +
      (s.ci_upper !== null ? s.ci_upper.toFixed(3) : "—") +
      "</td><td class='num'>" +
      s.acGap.toFixed(1) +
      "</td><td class='num'>" +
      s.thGap.toFixed(1) +
      "</td>";
    rows.appendChild(tr);
  });
}

function updateSummaryStats() {
  const summary = projectData.summary;
  const gaps = projectData.gaps_by_topic;
  const avgTau = el("avgTauStat");
  const acCert = el("acCertStat");
  if (avgTau) avgTau.textContent = summary.avg_tau.toFixed(3);
  if (acCert) acCert.textContent = gaps.Acoustics.cert_pct.toFixed(1) + "%";
  const acBar = el("acCertBar");
  if (acBar) acBar.style.setProperty("--w", gaps.Acoustics.cert_pct + "%");
  const acGapBar = el("acGapBar");
  if (acGapBar) acGapBar.style.setProperty("--w", Math.abs(gaps.Acoustics.avg_gap) + "%");
  const acLabel = el("acCertLabel");
  if (acLabel) acLabel.textContent = gaps.Acoustics.cert_pct.toFixed(1) + "%";
  const acGapLabel = el("acGapLabel");
  if (acGapLabel) acGapLabel.textContent = gaps.Acoustics.avg_gap.toFixed(1) + "%";
}

function drawSketch() {
  const canvas = el("sketchCanvas");
  if (!canvas) return;
  const rect = canvas.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  canvas.width = Math.max(320, rect.width * dpr);
  canvas.height = Math.max(320, rect.height * dpr);
  const ctx = canvas.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  const w = rect.width;
  const h = rect.height;
  ctx.clearRect(0, 0, w, h);
  ctx.lineCap = "square";
  ctx.lineJoin = "miter";
  ctx.strokeStyle = "#141414";
  ctx.fillStyle = "rgba(20,20,20,.04)";

  function line(x1, y1, x2, y2, width = 1) {
    ctx.beginPath();
    ctx.lineWidth = width;
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();
  }

  function rect(x, y, ww, hh, width = 1) {
    line(x, y, x + ww, y, width);
    line(x + ww, y, x + ww, y + hh, width);
    line(x + ww, y + hh, x, y + hh, width);
    line(x, y + hh, x, y, width);
  }

  function label(txt, x, y, size = 11, weight = "500") {
    ctx.font = weight + " " + size + "px IBM Plex Mono, ui-monospace, monospace";
    ctx.fillStyle = "#141414";
    ctx.fillText(txt, x, y);
  }

  const bx = w * 0.22;
  const by = h * 0.18;
  const bw = w * 0.44;
  const bh = h * 0.62;
  rect(bx, by, bw, bh, 1.2);
  line(bx, by, bx + bw * 0.16, by - h * 0.07, 1);
  line(bx + bw, by, bx + bw * 0.84, by - h * 0.07, 1);
  line(bx + bw * 0.16, by - h * 0.07, bx + bw * 0.84, by - h * 0.07, 1);

  for (let i = 0; i < 5; i++) {
    for (let j = 0; j < 4; j++) {
      const x = bx + 24 + (j * (bw - 48)) / 3;
      const y = by + 32 + (i * (bh - 78)) / 4;
      rect(x, y, 28, 22, 0.8);
    }
  }
  rect(bx + bw * 0.42, by + bh - 68, bw * 0.16, 68, 1);

  label("PLAN — CERTIFIED BUILDING", bx, by - 18, 10);
  label("LEED / WELL", bx + bw * 0.18, by + bh + 28, 12, "600");
  label("ACOUSTIC FIELD", bx + bw + 28, by + 24, 10);

  for (let k = 0; k < 7; k++) {
    const startX = bx + bw + 24 + k * 5;
    const amp = 12 + k * 4;
    ctx.beginPath();
    ctx.lineWidth = 0.8 + k * 0.05;
    for (let t = 0; t < 90; t++) {
      const x = startX + t * 2.5;
      const y = by + bh * 0.38 + Math.sin(t / 6 + k) * amp;
      if (t === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
  }

  label("NOISE", bx + bw + 42, by + bh * 0.24, 22, "600");
  label("sound privacy", bx + bw + 42, by + bh * 0.52, 10);

  line(w * 0.08, h * 0.84, w * 0.92, h * 0.84, 0.6);
  label("badge points", w * 0.08, h * 0.1, 10);
  label("occupant pain", w * 0.62, h * 0.9, 10);
  line(w * 0.12, h * 0.12, w * 0.18, h * 0.16, 0.6);
  line(w * 0.72, h * 0.86, w * 0.66, h * 0.78, 0.6);
}

async function initCAI() {
  const response = await fetch("assets/data/systems.json");
  projectData = await response.json();
  systems = sortSystems(projectData.systems);
  fillTables();
  updateSummaryStats();
  drawSketch();
}

window.addEventListener("resize", () => {
  window.clearTimeout(window.__sketchTimer);
  window.__sketchTimer = window.setTimeout(drawSketch, 120);
});

document.addEventListener("DOMContentLoaded", initCAI);
