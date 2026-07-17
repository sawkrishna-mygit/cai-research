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
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  ctx.strokeStyle = "#0b0b0b";
  ctx.fillStyle = "rgba(0,0,0,.04)";

  function roughLine(x1, y1, x2, y2, reps = 3, jitter = 2) {
    for (let r = 0; r < reps; r++) {
      ctx.beginPath();
      ctx.lineWidth = 1.1 + Math.random() * 1.2;
      const dx1 = (Math.random() - 0.5) * jitter;
      const dy1 = (Math.random() - 0.5) * jitter;
      const dx2 = (Math.random() - 0.5) * jitter;
      const dy2 = (Math.random() - 0.5) * jitter;
      ctx.moveTo(x1 + dx1, y1 + dy1);
      const cx = (x1 + x2) / 2 + (Math.random() - 0.5) * jitter * 4;
      const cy = (y1 + y2) / 2 + (Math.random() - 0.5) * jitter * 4;
      ctx.quadraticCurveTo(cx, cy, x2 + dx2, y2 + dy2);
      ctx.stroke();
    }
  }
  function roughRect(x, y, ww, hh) {
    roughLine(x, y, x + ww, y, 3, 3);
    roughLine(x + ww, y, x + ww, y + hh, 3, 3);
    roughLine(x + ww, y + hh, x, y + hh, 3, 3);
    roughLine(x, y + hh, x, y, 3, 3);
  }
  function roughText(txt, x, y, size = 18, rot = 0) {
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(rot);
    ctx.font = "900 " + size + "px Caveat, Patrick Hand, sans-serif";
    ctx.fillStyle = "#0b0b0b";
    ctx.fillText(txt, 0, 0);
    ctx.restore();
  }

  const bx = w * 0.25;
  const by = h * 0.16;
  const bw = w * 0.42;
  const bh = h * 0.68;
  roughRect(bx, by, bw, bh);
  roughLine(bx, by, bx + bw * 0.16, by - h * 0.08, 3, 4);
  roughLine(bx + bw, by, bx + bw * 0.84, by - h * 0.08, 3, 4);
  roughLine(bx + bw * 0.16, by - h * 0.08, bx + bw * 0.84, by - h * 0.08, 3, 4);
  for (let i = 0; i < 5; i++) {
    for (let j = 0; j < 4; j++) {
      const x = bx + 25 + (j * (bw - 50)) / 3;
      const y = by + 34 + (i * (bh - 85)) / 4;
      roughRect(x, y, 28, 22);
      if ((i + j) % 3 === 0) {
        roughLine(x + 6, y + 12, x + 22, y + 12, 2, 2);
        roughLine(x + 14, y + 5, x + 14, y + 18, 2, 2);
      }
    }
  }
  roughRect(bx + bw * 0.42, by + bh - 70, bw * 0.16, 70);
  roughText("LEED?", bx + bw * 0.2, by + bh + 34, 26, -0.08);
  roughText("WELL?", bx + bw * 0.57, by + bh + 34, 24, 0.08);

  for (let k = 0; k < 9; k++) {
    const startX = bx + bw + 18 + k * 4;
    const amp = 16 + k * 5;
    ctx.beginPath();
    ctx.lineWidth = 1.1 + k * 0.08;
    for (let t = 0; t < 90; t++) {
      const x = startX + t * 2.7;
      const y = by + bh * 0.35 + Math.sin(t / 7 + k) * amp;
      if (t === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
  }
  roughText("NOISE", bx + bw + 44, by + bh * 0.22, 42, -0.08);
  roughText("sound privacy", bx + bw + 58, by + bh * 0.52, 20, 0.04);

  roughLine(w * 0.08, h * 0.82, w * 0.92, h * 0.82, 3, 4);
  roughText("badge points", w * 0.07, h * 0.09, 20, -0.1);
  roughText("occupant pain", w * 0.64, h * 0.91, 22, 0.06);
  roughLine(w * 0.13, h * 0.13, w * 0.2, h * 0.16, 2, 4);
  roughLine(w * 0.75, h * 0.86, w * 0.68, h * 0.78, 2, 4);

  ctx.globalAlpha = 0.18;
  for (let i = 0; i < 220; i++) {
    ctx.beginPath();
    ctx.arc(Math.random() * w, Math.random() * h, Math.random() * 1.2, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.globalAlpha = 1;
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
