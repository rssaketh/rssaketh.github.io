// Page interactions: scroll reveals, autoplaying videos in view, paper filters.
document.documentElement.classList.add('js');

const io = new IntersectionObserver(entries => {
  for (const e of entries) {
    if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
  }
}, { rootMargin: '0px 0px -8% 0px' });
document.querySelectorAll('.reveal').forEach(el => io.observe(el));

const vio = new IntersectionObserver(entries => {
  for (const e of entries) {
    const v = e.target;
    if (e.isIntersecting) v.play().catch(() => {}); else v.pause();
  }
}, { threshold: 0.35 });
if (!matchMedia('(prefers-reduced-motion: reduce)').matches) {
  document.querySelectorAll('video[data-autoplay]').forEach(v => vio.observe(v));
}

const filters = document.querySelector('.filters');
if (filters) {
  filters.addEventListener('click', ev => {
    const btn = ev.target.closest('button');
    if (!btn) return;
    const topic = btn.dataset.topic;
    filters.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b === btn)));
    document.querySelectorAll('.paper[data-topics]').forEach(el => {
      el.hidden = topic !== 'all' && !el.dataset.topics.split(' ').includes(topic);
    });
    // Highlights: the default picks for "All", otherwise that topic's own top three.
    document.querySelectorAll('.feat[data-hl]').forEach(el => {
      el.hidden = topic === 'all' ? !('default' in el.dataset) : !el.dataset.hl.split(' ').includes(topic);
    });
    document.querySelector('.featured')?.classList.toggle('filtered', topic !== 'all');
    document.querySelectorAll('.year-group').forEach(g => {
      g.hidden = !g.querySelector('.paper:not([hidden])');
    });
    document.querySelectorAll('.reveal').forEach(el => el.classList.add('in'));
  });
}
