// ============================================================
// Tracker.js — Entry/Exit Tracker page
// ============================================================

const Tracker = (() => {
  let initialized = false;

  function init() {
    if (!initialized) initialized = true;
    load();
    loadMovers();
  }

  async function load() {
    const filterKey = document.getElementById('tracker-filter-key')?.value || 'rs80_NSE_ema200';

    try {
      const data = await api(`/api/tracker/changes?filter_key=${filterKey}`);

      // Entering
      const enterCount = document.getElementById('entering-count');
      const enterList = document.getElementById('entering-list');
      enterCount.textContent = data.entering?.length || 0;

      const badge = document.getElementById('tracker-badge');
      const total = (data.entering?.length || 0) + (data.exiting?.length || 0);
      if (total > 0) {
        badge.textContent = total;
        badge.style.display = 'inline';
      } else {
        badge.style.display = 'none';
      }

      if (enterList) {
        enterList.innerHTML = '';
        if (!data.entering?.length) {
          enterList.innerHTML = '<span style="color:var(--text-muted);font-size:12px">No new entries today</span>';
        } else {
          data.entering.forEach(sym => {
            const tag = document.createElement('span');
            tag.className = 'tracker-tag entering';
            tag.textContent = sym;
            tag.title = `Click to view ${sym}`;
            tag.addEventListener('click', () => openCompanyFromTracker(sym));
            enterList.appendChild(tag);
          });
        }
      }

      // Exiting
      const exitCount = document.getElementById('exiting-count');
      const exitList = document.getElementById('exiting-list');
      exitCount.textContent = data.exiting?.length || 0;

      if (exitList) {
        exitList.innerHTML = '';
        if (!data.exiting?.length) {
          exitList.innerHTML = '<span style="color:var(--text-muted);font-size:12px">No exits today</span>';
        } else {
          data.exiting.forEach(sym => {
            const tag = document.createElement('span');
            tag.className = 'tracker-tag exiting';
            tag.textContent = sym;
            tag.title = `Click to view ${sym}`;
            tag.addEventListener('click', () => openCompanyFromTracker(sym));
            exitList.appendChild(tag);
          });
        }
      }

      // Snapshot chart
      loadSnapshotChart();

    } catch (e) {
      console.error('[Tracker] Load failed:', e);
    }
  }

  async function loadMovers() {
    const days = parseInt(document.getElementById('tracker-days')?.value || '7');
    const filterKey = document.getElementById('tracker-filter-key')?.value || 'rs80_NSE_ema200';

    try {
      const data = await api(`/api/tracker/movers?filter_key=${filterKey}&days=${days}`);

      const enterEl = document.getElementById('movers-entering');
      const exitEl = document.getElementById('movers-exiting');

      if (enterEl) {
        enterEl.innerHTML = '';
        if (!data.entering?.length) {
          enterEl.innerHTML = '<div style="color:var(--text-muted);font-size:12px;padding:8px">No entries in period</div>';
        } else {
          data.entering.forEach(sym => {
            const div = document.createElement('div');
            div.className = 'mover-item';
            div.innerHTML = `<span style="color:var(--green);margin-right:6px">▲</span>${sym}`;
            div.addEventListener('click', () => openCompanyFromTracker(sym));
            enterEl.appendChild(div);
          });
        }
      }

      if (exitEl) {
        exitEl.innerHTML = '';
        if (!data.exiting?.length) {
          exitEl.innerHTML = '<div style="color:var(--text-muted);font-size:12px;padding:8px">No exits in period</div>';
        } else {
          data.exiting.forEach(sym => {
            const div = document.createElement('div');
            div.className = 'mover-item';
            div.innerHTML = `<span style="color:var(--red);margin-right:6px">▼</span>${sym}`;
            div.addEventListener('click', () => openCompanyFromTracker(sym));
            exitEl.appendChild(div);
          });
        }
      }
    } catch (e) {
      console.error('[Tracker] Movers failed:', e);
    }
  }

  async function loadSnapshotChart() {
    const filterKey = document.getElementById('tracker-filter-key')?.value || 'rs80_NSE_ema200';
    try {
      const data = await api(`/api/tracker/snapshots?filter_key=${filterKey}`);
      const snapshots = (data.snapshots || []).reverse();
      const chartEl = document.getElementById('snapshot-chart');
      if (!chartEl || !snapshots.length) return;

      chartEl.innerHTML = '';
      const maxCount = Math.max(...snapshots.map(s => s.count), 1);

      snapshots.forEach(snap => {
        const bar = document.createElement('div');
        bar.className = 'snapshot-bar';
        const heightPct = Math.max((snap.count / maxCount) * 100, 5);
        bar.style.height = `${heightPct}%`;
        bar.title = `${snap.date}: ${snap.count} stocks`;
        chartEl.appendChild(bar);
      });
    } catch (e) { /* Ignore */ }
  }

  function openCompanyFromTracker(symbol) {
    document.querySelectorAll('.page').forEach(p => p.classList.add('hidden'));
    document.getElementById('page-company').classList.remove('hidden');
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    CompanyPage.load(symbol, 'NSE', { symbol });
  }

  return { init, load, loadMovers };
})();
