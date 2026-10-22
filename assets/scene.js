// Time-of-day landscape. The sky, sun/moon, stars and land colours follow the
// clock in TIMEZONE; each page picks a terrain via <body data-scene="...">.
// Preview another hour with ?t=HH or ?t=HH:MM.

const TIMEZONE = 'America/New_York';

const W = 1600, H = 1000, HORIZON = 600;
const SVG_NS = 'http://www.w3.org/2000/svg';

// [hour, sky top, sky bottom]
const SKY = [
  [0,    '#0b0f2c', '#23285a'],
  [4.5,  '#121738', '#3a3566'],
  [5.75, '#2b3264', '#8a6c8a'],
  [6.75, '#5a74ad', '#f1b68f'],
  [8,    '#5a87c6', '#d9e3ee'],
  [12,   '#4d86d2', '#c9dcef'],
  [16,   '#5888c6', '#e4e1d6'],
  [18.25,'#6670a8', '#f3a96c'],
  [19.25,'#353a70', '#b9707a'],
  [20.5, '#131838', '#2e3263'],
  [24,   '#0b0f2c', '#23285a'],
];

const LAND = {
  day:   { far: '#cfd3c8', near: '#3b5348' },
  night: { far: '#555983', near: '#1a1c34' },
};

const SUNRISE = 6.25, SUNSET = 19;

// ---------- helpers ----------

function mulberry32(seed) {
  return function () {
    seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function hexToRgb(h) {
  const n = parseInt(h.slice(1), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}
function rgbToHex([r, g, b]) {
  return '#' + [r, g, b].map(v => Math.round(v).toString(16).padStart(2, '0')).join('');
}
function mix(a, b, t) {
  const A = hexToRgb(a), B = hexToRgb(b);
  return rgbToHex(A.map((v, i) => v + (B[i] - v) * t));
}
const smooth = t => t * t * (3 - 2 * t);
const clamp01 = t => Math.min(1, Math.max(0, t));

function el(tag, attrs = {}, parent) {
  const e = document.createElementNS(SVG_NS, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  if (parent) parent.appendChild(e);
  return e;
}

// ---------- time ----------

function currentHour() {
  const q = new URLSearchParams(location.search).get('t');
  if (q) {
    const [h, m = 0] = q.split(':').map(Number);
    if (!isNaN(h)) return { hour: h + m / 60, label: `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}` };
  }
  const parts = new Intl.DateTimeFormat('en-GB', {
    timeZone: TIMEZONE, hour: '2-digit', minute: '2-digit', hour12: false,
  }).formatToParts(new Date());
  const h = +parts.find(p => p.type === 'hour').value % 24;
  const m = +parts.find(p => p.type === 'minute').value;
  return { hour: h + m / 60, label: `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}` };
}

function skyAt(hour) {
  for (let i = 0; i < SKY.length - 1; i++) {
    const [h0, t0, b0] = SKY[i], [h1, t1, b1] = SKY[i + 1];
    if (hour >= h0 && hour <= h1) {
      const t = smooth((hour - h0) / (h1 - h0));
      return { top: mix(t0, t1, t), bottom: mix(b0, b1, t) };
    }
  }
  return { top: SKY[0][1], bottom: SKY[0][2] };
}

// 0 at night, 1 in full day, eased across sunrise/sunset.
function daylight(hour) {
  const up = clamp01((hour - (SUNRISE - 0.75)) / 1.75);
  const down = clamp01(((SUNSET + 0.75) - hour) / 1.75);
  return smooth(Math.min(up, down));
}

// ---------- terrain ----------

function ridgeHills(rng, base, amp, octaves = 3) {
  const waves = Array.from({ length: octaves }, (_, k) => ({
    f: (0.0016 + rng() * 0.002) * (k + 1) * 1.6,
    a: amp / (k + 1.2),
    p: rng() * Math.PI * 2,
  }));
  const pts = [];
  for (let x = -20; x <= W + 20; x += 20) {
    let y = base;
    for (const w of waves) y += Math.sin(x * w.f + w.p) * w.a;
    pts.push([x, y]);
  }
  return pts;
}

function ridgeMountains(rng, base, amp, roughness = 0.52) {
  const n = 128;
  const ys = new Array(n + 1).fill(0);
  ys[0] = rng() * amp; ys[n] = rng() * amp;
  let step = n, scale = amp;
  while (step > 1) {
    const half = step / 2;
    for (let i = half; i < n; i += step) {
      ys[i] = (ys[i - half] + ys[i + half]) / 2 + (rng() - 0.5) * 2 * scale;
    }
    step = half; scale *= roughness;
  }
  // Normalise so the tallest peak reaches the full amplitude.
  const lo = Math.min(...ys), hi = Math.max(...ys);
  return ys.map((v, i) => [-20 + (i / n) * (W + 40), base - ((v - lo) / (hi - lo || 1)) * amp]);
}

function pathFrom(pts, smoothCurve) {
  let d = `M${pts[0][0]},${H + 10} L${pts[0][0]},${pts[0][1]}`;
  if (smoothCurve) {
    for (let i = 1; i < pts.length; i++) {
      const [x0, y0] = pts[i - 1], [x1, y1] = pts[i];
      const mx = (x0 + x1) / 2;
      d += ` Q${x0},${y0} ${mx},${(y0 + y1) / 2}`;
    }
    const last = pts[pts.length - 1];
    d += ` L${last[0]},${last[1]}`;
  } else {
    for (let i = 1; i < pts.length; i++) d += ` L${pts[i][0].toFixed(1)},${pts[i][1].toFixed(1)}`;
  }
  return d + ` L${pts[pts.length - 1][0]},${H + 10} Z`;
}

function pines(rng, pts, every, height) {
  let d = '';
  for (let i = 0; i < pts.length; i += 1) {
    if (rng() > every) continue;
    const [x, y] = pts[i];
    const h = height * (0.6 + rng() * 0.7), w = h * 0.32;
    d += `M${x - w},${y + 4} L${x},${y - h} L${x + w},${y + 4} Z `;
  }
  return d;
}

// Each layer: { pts, smooth, extra? }. Index 0 is farthest.
const SCENES = {
  hills(rng) {
    return [
      { pts: ridgeHills(rng, HORIZON + 20, 26), smooth: true },
      { pts: ridgeHills(rng, HORIZON + 70, 34), smooth: true },
      { pts: ridgeHills(rng, HORIZON + 140, 30), smooth: true },
      { pts: ridgeHills(rng, HORIZON + 230, 26), smooth: true },
      { pts: ridgeHills(rng, HORIZON + 330, 18), smooth: true },
    ];
  },
  mountains(rng) {
    return [
      { pts: ridgeMountains(rng, HORIZON + 60, 300), smooth: false },
      { pts: ridgeMountains(rng, HORIZON + 110, 170), smooth: false },
      { pts: ridgeHills(rng, HORIZON + 170, 30), smooth: true },
      { pts: ridgeHills(rng, HORIZON + 260, 24), smooth: true },
      { pts: ridgeHills(rng, HORIZON + 350, 16), smooth: true },
    ];
  },
  lake(rng) {
    const flat = y => [[-20, y], [W + 20, y]];
    return [
      { pts: ridgeMountains(rng, HORIZON + 90, 220, 0.5), smooth: false },
      { pts: ridgeHills(rng, HORIZON + 80, 22), smooth: true },
      { pts: flat(HORIZON + 120), smooth: false, water: true },
      { pts: ridgeHills(rng, HORIZON + 330, 22), smooth: true },
    ];
  },
  forest(rng) {
    const back = ridgeHills(rng, HORIZON + 40, 40);
    const mid = ridgeHills(rng, HORIZON + 130, 34);
    const front = ridgeHills(rng, HORIZON + 260, 26);
    return [
      { pts: back, smooth: true },
      { pts: mid, smooth: true, trees: pines(rng, mid, 0.55, 46) },
      { pts: front, smooth: true, trees: pines(rng, front, 0.4, 80) },
      { pts: ridgeHills(rng, HORIZON + 360, 14), smooth: true },
    ];
  },
};

// ---------- build ----------

function build(root, sceneName) {
  const rng = mulberry32([...sceneName].reduce((a, c) => a * 31 + c.charCodeAt(0), 7));
  const svg = el('svg', { viewBox: `0 0 ${W} ${H}`, preserveAspectRatio: 'xMidYMax slice', 'aria-hidden': 'true', focusable: 'false' });
  root.appendChild(svg);

  const defs = el('defs', {}, svg);
  const glow = el('radialGradient', { id: 'sunglow' }, defs);
  el('stop', { offset: '0%', 'stop-color': '#ffd59a', 'stop-opacity': '.7' }, glow);
  el('stop', { offset: '100%', 'stop-color': '#ffd59a', 'stop-opacity': '0' }, glow);
  const mglow = el('radialGradient', { id: 'moonglow' }, defs);
  el('stop', { offset: '0%', 'stop-color': '#e9ecff', 'stop-opacity': '.45' }, mglow);
  el('stop', { offset: '100%', 'stop-color': '#e9ecff', 'stop-opacity': '0' }, mglow);
  const sunFill = el('radialGradient', { id: 'sunfill', cx: '40%', cy: '35%' }, defs);
  el('stop', { offset: '0%', 'stop-color': '#ffe3ae' }, sunFill);
  el('stop', { offset: '100%', 'stop-color': '#f7a24c' }, sunFill);

  const stars = el('g', { class: 'stars' }, svg);
  for (let i = 0; i < 140; i++) {
    el('circle', {
      cx: (rng() * W).toFixed(1), cy: (rng() * (HORIZON - 40)).toFixed(1),
      r: (0.6 + rng() * 1.3).toFixed(2), fill: '#fff',
      style: `animation-delay:${(rng() * 6).toFixed(2)}s`,
    }, stars);
  }

  const sun = el('g', { class: 'sun' }, svg);
  el('circle', { r: 110, fill: 'url(#sunglow)' }, sun);
  el('circle', { r: 38, fill: 'url(#sunfill)' }, sun);

  const moon = el('g', { class: 'moon' }, svg);
  el('circle', { r: 90, fill: 'url(#moonglow)' }, moon);
  el('circle', { r: 30, fill: '#eef0f6' }, moon);
  el('circle', { r: 6, cx: -9, cy: -6, fill: '#d6d9e6' }, moon);
  el('circle', { r: 4, cx: 10, cy: 8, fill: '#d6d9e6' }, moon);
  el('circle', { r: 3, cx: 4, cy: -14, fill: '#dfe2ec' }, moon);

  const clouds = el('g', { class: 'clouds' }, svg);
  for (let i = 0; i < 5; i++) {
    const g = el('g', { class: 'cloud', style: `animation-duration:${160 + rng() * 160}s;animation-delay:-${rng() * 300}s` }, clouds);
    const y = 60 + rng() * (HORIZON - 260), s = 0.6 + rng() * 0.9;
    const inner = el('g', { transform: `translate(0 ${y.toFixed(0)}) scale(${s.toFixed(2)})` }, g);
    if (rng() < 0.45) {
      // thin streak
      el('rect', { x: 0, y: 0, width: 260, height: 5, rx: 2.5 }, inner);
      el('rect', { x: 70, y: 12, width: 220, height: 4, rx: 2 }, inner);
    } else {
      el('ellipse', { cx: 70, cy: 18, rx: 70, ry: 12 }, inner);
      el('ellipse', { cx: 60, cy: 6, rx: 30, ry: 20 }, inner);
      el('ellipse', { cx: 95, cy: 2, rx: 34, ry: 26 }, inner);
      el('ellipse', { cx: 130, cy: 12, rx: 26, ry: 16 }, inner);
      el('rect', { x: 0, y: 18, width: 170, height: 12, rx: 6 }, inner);
    }
  }

  const land = el('g', { class: 'land' }, svg);
  const layers = SCENES[sceneName] ? SCENES[sceneName](rng) : SCENES.hills(rng);
  const layerEls = layers.map((L, i) => {
    const g = el('g', {}, land);
    const p = el('path', { d: pathFrom(L.pts, L.smooth) }, g);
    const parts = { g, p, i, n: layers.length, water: L.water };
    if (L.trees) parts.t = el('path', { d: L.trees }, g);
    // a faint highlight along each ridge
    el('path', { d: pathFrom(L.pts, L.smooth), fill: 'none', stroke: 'rgba(255,255,255,.12)', 'stroke-width': 1.2 }, g);
    if (L.water) {
      parts.sheen = el('g', {}, g);
      for (let k = 0; k < 14; k++) {
        const y = L.pts[0][1] + 18 + k * 14 + rng() * 6;
        const x = rng() * W, w = 80 + rng() * 260;
        el('rect', { x, y, width: w, height: 1.5, rx: 1, fill: '#fff', opacity: 0.08 + rng() * 0.12 }, parts.sheen);
      }
    }
    return parts;
  });

  return { svg, sun, moon, stars, clouds, layerEls };
}

function paint(root, scene, timeEl) {
  const { hour, label } = currentHour();
  const sky = skyAt(hour);
  const d = daylight(hour);

  root.style.setProperty('--sky-top', sky.top);
  root.style.setProperty('--sky-bottom', sky.bottom);
  const doc = document.documentElement.style;
  doc.setProperty('--sky-top', sky.top);
  doc.setProperty('--sky-bottom', sky.bottom);
  document.documentElement.dataset.daypart = d > 0.5 ? 'day' : 'night';
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.content = sky.top;

  // sun / moon arcs
  // The SVG is cropped ("slice") to fill the viewport, so place the arc within
  // the visible part. Wide screens keep it right of the text column; narrow
  // ones run it low across the full width, below the heading.
  const vw = innerWidth, vh = innerHeight;
  const scale = Math.max(vw / W, vh / H);
  const visW = vw / scale, x0 = (W - visW) / 2;
  const narrow = vw < 760;
  const [from, span, k] = narrow ? [0.12, 0.76, 0.3] : [0.42, 0.5, 1];
  const arc = (t, lift) => [x0 + visW * (from + span * t), HORIZON + 40 - Math.sin(Math.PI * t) * lift * k];
  const st = (hour - SUNRISE) / (SUNSET - SUNRISE);
  if (st > -0.08 && st < 1.08) {
    const [x, y] = arc(st, narrow ? 840 : 420);
    scene.sun.setAttribute('transform', `translate(${x} ${y})`);
    scene.sun.style.opacity = 1;
  } else scene.sun.style.opacity = 0;

  const nightLen = 24 - (SUNSET - SUNRISE);
  const mt = (((hour - SUNSET) % 24) + 24) % 24 / nightLen;
  if (mt > -0.05 && mt < 1.05) {
    const [x, y] = arc(mt, narrow ? 800 : 380);
    scene.moon.setAttribute('transform', `translate(${x} ${y})`);
    scene.moon.style.opacity = 1 - d;
  } else scene.moon.style.opacity = 0;

  scene.stars.style.opacity = Math.pow(1 - d, 2);
  scene.clouds.style.fill = mix(mix('#f4f6fa', sky.top, 0.15), mix(sky.top, '#ffffff', 0.18), 1 - d);
  scene.clouds.style.opacity = 0.55 + 0.4 * d;

  const far = mix(mix(LAND.night.far, LAND.day.far, d), sky.bottom, 0.4);
  const near = mix(LAND.night.near, LAND.day.near, d);
  for (const L of scene.layerEls) {
    const t = L.n === 1 ? 1 : L.i / (L.n - 1);
    let c = mix(far, near, Math.pow(t, 0.9));
    if (L.water) c = mix(mix(sky.bottom, sky.top, 0.35), c, 0.35);
    L.p.setAttribute('fill', c);
    if (L.t) L.t.setAttribute('fill', mix(c, near, 0.35));
  }

  if (timeEl) timeEl.textContent = `It's ${label} where I am`;
}

function init() {
  const root = document.querySelector('.scene');
  if (!root) return;
  const scene = build(root, document.body.dataset.scene || 'hills');
  const timeEl = document.querySelector('[data-clock]');
  paint(root, scene, timeEl);
  setInterval(() => paint(root, scene, timeEl), 60_000);
  addEventListener('resize', () => paint(root, scene, timeEl));
}

init();
