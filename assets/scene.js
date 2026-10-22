// Desert landscape that follows the time of day in TIMEZONE. Each page picks a
// terrain via <body data-scene="...">. Layers drift at different speeds as the
// page scrolls, and the sun or moon sinks toward the horizon.
// Preview another hour with ?t=HH or ?t=HH:MM.

const TIMEZONE = 'America/Los_Angeles';

const W = 1600, H = 1000, HORIZON = 600;
const SVG_NS = 'http://www.w3.org/2000/svg';
const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;

// [hour, sky top, sky bottom]
const SKY = [
  [0,     '#120c24', '#2c1838'],
  [4.5,   '#1a1030', '#3e2442'],
  [5.75,  '#2e1e4a', '#a05a6a'],
  [6.75,  '#6e7fb8', '#f6b38a'],
  [8,     '#79a8d4', '#f2dcc4'],
  [12,    '#6aa5d8', '#ecdfcc'],
  [16,    '#709dcc', '#f1d0ad'],
  [18.25, '#8a6fa8', '#f78f5c'],
  [19.25, '#4a2b5e', '#d0607a'],
  [20.5,  '#1c1030', '#3a1e40'],
  [24,    '#120c24', '#2c1838'],
];

const LAND = {
  day:   { far: '#e7c3a3', near: '#6e3426' },
  night: { far: '#5b3c5f', near: '#1b1020' },
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

// Fraction through the synodic month: 0 new, .5 full.
function moonPhase(date = new Date()) {
  const ref = Date.UTC(2000, 0, 6, 18, 14);
  const days = (date - ref) / 864e5;
  return ((days / 29.530589) % 1 + 1) % 1;
}

// Lit part of a moon of radius r at phase f, as an SVG path.
function moonLitPath(r, f) {
  const k = Math.cos(2 * Math.PI * f), rx = Math.abs(k) * r;
  const waxing = f < 0.5;
  const outer = waxing ? 1 : 0;
  const term = waxing ? (k > 0 ? 0 : 1) : (k > 0 ? 1 : 0);
  return `M0,${-r} A${r},${r} 0 0 ${outer} 0,${r} A${rx},${r} 0 0 ${term} 0,${-r} Z`;
}

// ---------- terrain ----------

function rolling(rng, base, amp, octaves = 3) {
  const waves = Array.from({ length: octaves }, (_, k) => ({
    f: (0.0016 + rng() * 0.002) * (k + 1) * 1.6,
    a: amp / (k + 1.2),
    p: rng() * Math.PI * 2,
  }));
  const pts = [];
  for (let x = -40; x <= W + 40; x += 16) {
    let y = base;
    for (const w of waves) y += Math.sin(x * w.f + w.p) * w.a;
    pts.push([x, y]);
  }
  return pts;
}

// Dunes: a long gentle windward slope, then a sharper slip face.
function dunes(rng, base, amp, count = 4) {
  const pts = [];
  let x = -40;
  while (x < W + 40) {
    const w = (W / count) * (0.7 + rng() * 0.6), h = amp * (0.5 + rng() * 0.6);
    const crest = 0.68 + rng() * 0.12;
    for (let i = 0; i <= 24; i++) {
      const u = i / 24;
      const y = u < crest
        ? Math.sin((u / crest) * Math.PI / 2) ** 1.6
        : Math.cos(((u - crest) / (1 - crest)) * Math.PI / 2) ** 0.7;
      pts.push([x + u * w, base - y * h]);
    }
    x += w;
  }
  return pts;
}

// Mesas and buttes: flat tops, steep stepped sides, low ground between.
function mesas(rng, base, amp, density = 0.55) {
  const pts = [[-40, base]];
  let x = -40;
  while (x < W + 40) {
    if (rng() < density) {
      const top = base - amp * (0.45 + rng() * 0.55);
      const w = 90 + rng() * 320, side = 18 + rng() * 34, step = rng() < 0.6;
      const ledge = base - (base - top) * (0.45 + rng() * 0.2);
      if (step) pts.push([x + side * 0.5, ledge], [x + side * 0.9, ledge - 4]);
      pts.push([x + side, top + 6], [x + side + 8, top]);
      const capEnd = x + side + w;
      for (let cx = x + side + 30; cx < capEnd - 20; cx += 40) pts.push([cx, top + (rng() - 0.5) * 3]);
      pts.push([capEnd - 8, top], [capEnd, top + 6]);
      if (step) pts.push([capEnd + side * 0.1, ledge - 4], [capEnd + side * 0.5, ledge]);
      pts.push([capEnd + side, base - rng() * 10]);
      x = capEnd + side;
    } else {
      const gap = 60 + rng() * 180;
      pts.push([x + gap / 2, base - rng() * 14], [x + gap, base - rng() * 8]);
      x += gap;
    }
  }
  return pts;
}

function pathFrom(pts, curve) {
  const bottom = H + 700; // deep enough that scrolling never reveals the edge
  let d = `M${pts[0][0]},${bottom} L${pts[0][0]},${pts[0][1]}`;
  if (curve) {
    for (let i = 1; i < pts.length; i++) {
      const [x0, y0] = pts[i - 1], [x1, y1] = pts[i];
      d += ` Q${x0},${y0} ${(x0 + x1) / 2},${(y0 + y1) / 2}`;
    }
    const last = pts[pts.length - 1];
    d += ` L${last[0]},${last[1]}`;
  } else {
    for (let i = 1; i < pts.length; i++) d += ` L${pts[i][0].toFixed(1)},${pts[i][1].toFixed(1)}`;
  }
  return d + ` L${pts[pts.length - 1][0]},${bottom} Z`;
}

function heightAt(pts, x) {
  for (let i = 1; i < pts.length; i++) {
    if (pts[i][0] >= x) {
      const [x0, y0] = pts[i - 1], [x1, y1] = pts[i];
      return y0 + (y1 - y0) * ((x - x0) / (x1 - x0 || 1));
    }
  }
  return pts[pts.length - 1][1];
}

// Saguaro silhouettes drawn as thick round-capped strokes.
function saguaros(rng, pts, n, size) {
  let d = '';
  for (let i = 0; i < n; i++) {
    // spread evenly across the width, with some jitter
    const x = (W / n) * (i + 0.2 + rng() * 0.6), y = heightAt(pts, x) + 6;
    const h = size * (0.6 + rng() * 0.6);
    d += `M${x},${y} V${y - h} `;
    if (rng() < 0.85) d += `M${x},${y - h * 0.42} H${x - h * 0.22} V${y - h * 0.72} `;
    if (rng() < 0.7) d += `M${x},${y - h * 0.55} H${x + h * 0.2} V${y - h * 0.82} `;
  }
  return d;
}

// A natural rock arch: an outer mass with an elliptical window.
function arch(cx, ground, w, h) {
  const ox = w / 2, ix = w * 0.3, iy = h * 0.62;
  return `M${cx - ox},${ground} C${cx - ox},${ground - h * 0.9} ${cx - ox * 0.6},${ground - h} ${cx},${ground - h} ` +
         `C${cx + ox * 0.6},${ground - h} ${cx + ox},${ground - h * 0.85} ${cx + ox},${ground} Z ` +
         `M${cx - ix},${ground + 2} C${cx - ix},${ground - iy} ${cx + ix},${ground - iy} ${cx + ix},${ground + 2} Z`;
}

// Each layer: { pts, curve, strata?, cacti?, arch? }. Index 0 is farthest.
const SCENES = {
  mesas(rng) {
    const near = dunes(rng, HORIZON + 300, 46, 3);
    return [
      { pts: mesas(rng, HORIZON + 70, 150, 0.5), strata: true },
      { pts: mesas(rng, HORIZON + 130, 110, 0.45), strata: true },
      { pts: dunes(rng, HORIZON + 220, 50, 4), curve: true },
      { pts: near, curve: true, cacti: saguaros(rng, near, 4, 110) },
    ];
  },
  badlands(rng) {
    return [
      { pts: mesas(rng, HORIZON + 50, 220, 0.65), strata: true },
      { pts: mesas(rng, HORIZON + 120, 160, 0.6), strata: true },
      { pts: mesas(rng, HORIZON + 200, 110, 0.5), strata: true },
      { pts: dunes(rng, HORIZON + 300, 40, 3), curve: true },
    ];
  },
  dunes(rng) {
    const mid = dunes(rng, HORIZON + 170, 90, 3);
    return [
      { pts: mesas(rng, HORIZON + 40, 120, 0.35), strata: true },
      { pts: dunes(rng, HORIZON + 90, 70, 4), curve: true },
      { pts: mid, curve: true, cacti: saguaros(rng, mid, 2, 70) },
      { pts: dunes(rng, HORIZON + 310, 70, 2), curve: true },
    ];
  },
  arch(rng) {
    const mid = rolling(rng, HORIZON + 160, 20);
    const near = dunes(rng, HORIZON + 310, 40, 3);
    return [
      { pts: mesas(rng, HORIZON + 40, 200, 0.45), strata: true },
      { pts: mid, curve: true, arch: arch(1120, heightAt(mid, 1120) + 10, 420, 300) },
      { pts: near, curve: true, cacti: saguaros(rng, near, 3, 110) },
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
  el('stop', { offset: '0%', 'stop-color': '#ffcf8a', 'stop-opacity': '.75' }, glow);
  el('stop', { offset: '100%', 'stop-color': '#ffcf8a', 'stop-opacity': '0' }, glow);
  const mglow = el('radialGradient', { id: 'moonglow' }, defs);
  el('stop', { offset: '0%', 'stop-color': '#f6e7ff', 'stop-opacity': '.4' }, mglow);
  el('stop', { offset: '100%', 'stop-color': '#f6e7ff', 'stop-opacity': '0' }, mglow);
  const sunFill = el('radialGradient', { id: 'sunfill', cx: '40%', cy: '35%' }, defs);
  const sunStop0 = el('stop', { offset: '0%', 'stop-color': '#fff1c9' }, sunFill);
  const sunStop1 = el('stop', { offset: '100%', 'stop-color': '#ff9a4d' }, sunFill);
  const strata = el('pattern', { id: 'strata', width: 8, height: 26, patternUnits: 'userSpaceOnUse' }, defs);
  el('rect', { width: 8, height: 2, y: 4, fill: 'rgba(255,255,255,.06)' }, strata);
  el('rect', { width: 8, height: 5, y: 15, fill: 'rgba(0,0,0,.045)' }, strata);

  const sky = el('g', {}, svg);
  const stars = el('g', { class: 'stars' }, sky);
  for (let i = 0; i < 160; i++) {
    el('circle', {
      cx: (rng() * W).toFixed(1), cy: (rng() * (HORIZON - 20)).toFixed(1),
      r: (0.5 + rng() * 1.3).toFixed(2), fill: '#fff6ea',
      style: `animation-delay:${(rng() * 6).toFixed(2)}s`,
    }, stars);
  }
  const meteors = el('g', { class: 'meteors' }, sky);

  const sun = el('g', { class: 'sun' }, sky);
  el('circle', { r: 130, fill: 'url(#sunglow)' }, sun);
  el('circle', { r: 40, fill: 'url(#sunfill)' }, sun);

  const moon = el('g', { class: 'moon' }, sky);
  el('circle', { r: 100, fill: 'url(#moonglow)' }, moon);
  el('circle', { r: 30, fill: 'rgba(255,255,255,.07)' }, moon);
  el('path', { d: moonLitPath(30, moonPhase()), fill: '#fbf1e4' }, moon);

  const clouds = el('g', { class: 'clouds' }, sky);
  for (let i = 0; i < 4; i++) {
    const g = el('g', { class: 'cloud', style: `animation-duration:${200 + rng() * 160}s;animation-delay:-${rng() * 300}s` }, clouds);
    const y = 50 + rng() * (HORIZON - 300), s = 0.7 + rng() * 0.8;
    const inner = el('g', { transform: `translate(0 ${y.toFixed(0)}) scale(${s.toFixed(2)})` }, g);
    // long desert streaks, a few segments each
    let x = 0;
    for (let k = 0; k < 3; k++) {
      const w = 120 + rng() * 200;
      el('rect', { x, y: k * 9, width: w, height: 4 + rng() * 3, rx: 3 }, inner);
      x += 40 + rng() * 80;
    }
  }

  const birds = el('g', { class: 'birds' }, sky);
  for (let i = 0; i < 3; i++) {
    const g = el('g', { class: 'bird', style: `animation-duration:${60 + rng() * 40}s;animation-delay:-${rng() * 80}s` }, birds);
    const y = 60 + rng() * 120;
    for (let k = 0; k < 3; k++) {
      const bx = k * 22 + rng() * 8, by = y + k * 10 + rng() * 6;
      el('path', { d: `M${bx - 7},${by - 3} Q${bx - 3},${by - 5} ${bx},${by} Q${bx + 3},${by - 5} ${bx + 7},${by - 3}` }, g);
    }
  }

  const land = el('g', { class: 'land' }, svg);
  const layers = (SCENES[sceneName] || SCENES.mesas)(rng);
  const layerEls = layers.map((L, i) => {
    const g = el('g', {}, land);
    const d = pathFrom(L.pts, L.curve);
    const parts = { g, i, n: layers.length };
    parts.p = el('path', { d }, g);
    if (L.strata) el('path', { d, fill: 'url(#strata)' }, g);
    el('path', { d, fill: 'none', stroke: 'rgba(255,240,225,.14)', 'stroke-width': 1.2 }, g);
    if (L.arch) {
      parts.arch = el('path', { d: L.arch, 'fill-rule': 'evenodd' }, g);
      el('path', { d: L.arch, 'fill-rule': 'evenodd', fill: 'url(#strata)' }, g);
    }
    if (L.cacti) parts.cacti = el('path', { d: L.cacti, fill: 'none', 'stroke-width': 9, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, g);
    return parts;
  });

  return { svg, sky, sun, moon, stars, meteors, clouds, birds, layerEls, sunStop0, sunStop1, pos: {} };
}

function paint(scene, timeEl) {
  const { hour, label } = currentHour();
  const sky = skyAt(hour);
  const d = daylight(hour);
  scene.daylight = d;

  const doc = document.documentElement;
  doc.style.setProperty('--sky-top', sky.top);
  doc.style.setProperty('--sky-bottom', sky.bottom);
  doc.dataset.daypart = d > 0.5 ? 'day' : 'night';
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.content = sky.top;

  // The SVG is cropped ("slice") to fill the viewport, so place the arc within
  // the visible part. Wide screens keep it right of the text column; narrow
  // ones run it low across the full width, below the heading.
  const vw = innerWidth, vh = innerHeight;
  const scale = Math.max(vw / W, vh / H);
  const visW = vw / scale, x0 = (W - visW) / 2;
  scene.scale = scale;
  const narrow = vw < 760;
  const [from, span, k] = narrow ? [0.12, 0.76, 0.3] : [0.5, 0.44, 1];
  const arc = (t, lift) => [x0 + visW * (from + span * t), HORIZON + 40 - Math.sin(Math.PI * t) * lift * k];

  const st = (hour - SUNRISE) / (SUNSET - SUNRISE);
  if (st > -0.08 && st < 1.08) {
    scene.pos.sun = arc(st, narrow ? 840 : 430);
    scene.sun.style.opacity = 1;
    // redder near the horizon
    const low = 1 - clamp01(Math.sin(Math.PI * clamp01(st)) * 2.2);
    scene.sunStop0.setAttribute('stop-color', mix('#fff1c9', '#ffc58a', low));
    scene.sunStop1.setAttribute('stop-color', mix('#ff9a4d', '#e8463a', low));
  } else scene.sun.style.opacity = 0;

  const nightLen = 24 - (SUNSET - SUNRISE);
  const mt = ((((hour - SUNSET) % 24) + 24) % 24) / nightLen;
  if (mt < 1.05) {
    scene.pos.moon = arc(mt, narrow ? 800 : 380);
    scene.moon.style.opacity = 1 - d;
  } else scene.moon.style.opacity = 0;

  scene.stars.style.opacity = Math.pow(1 - d, 2);
  scene.birds.style.opacity = d * 0.8;
  scene.birds.style.stroke = mix('#3a2a2a', sky.top, 0.3);
  scene.clouds.style.fill = mix(mix('#fff4ea', sky.bottom, 0.2), mix(sky.top, '#e8b7c8', 0.2), 1 - d);
  scene.clouds.style.opacity = 0.45 + 0.4 * d;

  const far = mix(mix(LAND.night.far, LAND.day.far, d), sky.bottom, 0.38);
  const near = mix(LAND.night.near, LAND.day.near, d);
  for (const L of scene.layerEls) {
    const t = L.n === 1 ? 1 : L.i / (L.n - 1);
    const c = mix(far, near, Math.pow(t, 0.85));
    L.p.setAttribute('fill', c);
    if (L.arch) L.arch.setAttribute('fill', mix(c, near, 0.15));
    if (L.cacti) L.cacti.setAttribute('stroke', mix(c, '#000000', 0.25));
  }

  if (timeEl) {
    const [hh, mm] = label.split(':').map(Number);
    const icon = d > 0.5 ? '☀︎' : '☾';
    timeEl.textContent = `${icon} ${((hh + 11) % 12) + 1}:${String(mm).padStart(2, '0')} ${hh < 12 ? 'am' : 'pm'} in San Mateo`;
  }
  scroll(scene);
}

// Parallax: nearer layers rise faster; the sun and moon sink.
function scroll(scene) {
  const y = Math.min(scrollY, 1400) / (scene.scale || 1);
  const f = REDUCED ? 0.25 : 1;
  scene.layerEls.forEach(L => {
    const t = L.n === 1 ? 1 : L.i / (L.n - 1);
    L.g.setAttribute('transform', `translate(0 ${(-y * (0.04 + 0.22 * t) * f).toFixed(1)})`);
  });
  for (const k of ['sun', 'moon']) {
    const p = scene.pos[k];
    if (p) scene[k].setAttribute('transform', `translate(${p[0].toFixed(1)} ${(p[1] + y * 0.32 * f).toFixed(1)})`);
  }
  scene.stars.setAttribute('transform', `translate(0 ${(y * 0.06 * f).toFixed(1)})`);
  scene.clouds.setAttribute('transform', `translate(0 ${(y * 0.12 * f).toFixed(1)})`);
}

function meteor(scene) {
  if (scene.daylight < 0.3 && !document.hidden) {
    const x = 300 + Math.random() * 1100, y = 40 + Math.random() * 220;
    const len = 120 + Math.random() * 120;
    const m = el('line', { x1: x, y1: y, x2: x - len, y2: y + len * 0.45, class: 'meteor' }, scene.meteors);
    setTimeout(() => m.remove(), 1600);
  }
  setTimeout(() => meteor(scene), 5000 + Math.random() * 9000);
}

function init() {
  const root = document.querySelector('.scene');
  if (!root) return;
  const scene = build(root, document.body.dataset.scene || 'mesas');
  const timeEl = document.querySelector('[data-clock]');
  paint(scene, timeEl);
  setInterval(() => paint(scene, timeEl), 60_000);
  addEventListener('resize', () => paint(scene, timeEl));
  let ticking = false;
  addEventListener('scroll', () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => { scroll(scene); ticking = false; });
  }, { passive: true });
  if (!REDUCED) setTimeout(() => meteor(scene), 2500);
}

init();
