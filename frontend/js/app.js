// ============================================================
// App.js — Router, navigation, and shared state
// ============================================================

const App = (() => {
  let currentPage = 'screener';
  let history = [];
  let syncTimer = null;

  function init() {
    setupNav();
    navigate('screener');
    SearchComponent.init();
    updateMarketStatus();
    setInterval(updateMarketStatus, 60000);
    checkSyncStatus();
    setInterval(checkSyncStatus, 10000);
  }

  function setupNav() {
    document.querySelectorAll('.nav-item').forEach(el => {
      el.addEventListener('click', e => {
        e.preventDefault();
        navigate(el.dataset.page);
      });
    });
  }

  function navigate(page) {
    if (page !== currentPage) {
      history.push(currentPage);
    }
    currentPage = page;

    // Hide all pages
    document.querySelectorAll('.page').forEach(p => p.classList.add('hidden'));
    // Show target
    const target = document.getElementById(`page-${page}`);
    if (target) target.classList.remove('hidden');

    // Update nav active state
    document.querySelectorAll('.nav-item').forEach(el => {
      el.classList.toggle('active', el.dataset.page === page);
    });

    // Trigger page-specific load
    if (page === 'screener') Screener.init();
    if (page === 'industries') Industries.init();
    if (page === 'tracker') Tracker.init();
    if (page === 'home') loadHomeStats();
  }

  function goBack() {
    const prev = history.pop() || 'screener';
    navigate(prev);
  }

  function updateMarketStatus() {
    const now = new Date();
    const ist = new Date(now.toLocaleString('en-US', { timeZone: 'Asia/Kolkata' }));
    const hours = ist.getHours();
    const minutes = ist.getMinutes();
    const day = ist.getDay();
    const totalMins = hours * 60 + minutes;

    const isWeekend = day === 0 || day === 6;
    const isMarketHours = totalMins >= 555 && totalMins <= 930; // 9:15 to 15:30
    const isOpen = !isWeekend && isMarketHours;

    const dot = document.querySelector('.status-dot');
    const text = document.getElementById('market-status-text');
    if (dot && text) {
      dot.style.background = isOpen ? '#10B981' : '#6B7280';
      text.textContent = isOpen ? 'Market Open' : 'Market Closed';
    }
  }

  async function checkSyncStatus() {
    try {
      const res = await api('/api/screener/status');
      const updated = document.getElementById('last-updated');
      if (!updated) return;

      if (res.status === 'syncing') {
        updated.innerHTML = `<span style="color:var(--accent)">🔄 Syncing (${res.progress})</span>`;
        if (!syncTimer) {
          syncTimer = setInterval(checkSyncStatus, 3000);
        }
      } else {
        if (syncTimer) {
          clearInterval(syncTimer);
          syncTimer = null;
          // Sync just completed — refresh view
          if (currentPage === 'screener') Screener.applyFilters();
          if (currentPage === 'industries') Industries.init();
        }
        if (res.last_synced) {
          updated.textContent = `Synced: ${res.last_synced.slice(11, 16)}`;
          updated.title = `Last synced: ${res.last_synced}`;
        }
      }
    } catch (e) {
      // Ignore
    }
  }

  async function loadHomeStats() {
    try {
      const [trackerRes, screenerRes] = await Promise.all([
        fetch('/api/tracker/changes?filter_key=rs80_NSE_ema200').then(r => r.json()).catch(() => ({})),
        fetch('/api/screener?min_rs=80&limit=1').then(r => r.json()).catch(() => ({ total: 0 })),
      ]);

      document.getElementById('stat-entries').textContent = trackerRes.entering_count || 0;
      document.getElementById('stat-exits').textContent = trackerRes.exiting_count || 0;
      if (document.getElementById('stat-rs80')) {
        document.getElementById('stat-rs80').textContent = screenerRes.total || 0;
      }
      if (document.getElementById('stat-nse')) {
        document.getElementById('stat-nse').textContent = '338';
      }

      // Update tracker badge
      const badge = document.getElementById('tracker-badge');
      const total = (trackerRes.entering_count || 0) + (trackerRes.exiting_count || 0);
      if (total > 0 && badge) {
        badge.textContent = total;
        badge.style.display = 'inline';
      }
    } catch (e) {
      console.error('[App] Home stats failed:', e);
    }
  }

  return { init, navigate, goBack, loadHomeStats, checkSyncStatus };
})();


// ============================================================
// Utility functions
// ============================================================

function formatNum(n, decimals = 0) {
  if (n == null || n === '' || isNaN(n)) return '—';
  return Number(n).toLocaleString('en-IN', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
}

function formatCr(n) {
  if (!n || n === 0) return '—';
  if (n >= 100000) return `${(n / 100000).toFixed(1)}L`;
  if (n >= 1000) return `${(n / 1000).toFixed(1)}K`;
  return formatNum(n);
}

function rsClass(rs) {
  if (rs >= 80) return 'high';
  if (rs >= 50) return 'mid';
  return 'low';
}

function pctClass(pct) {
  return pct >= 0 ? 'up' : 'down';
}

async function api(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`API ${path} returned ${res.status}`);
  return res.json();
}


// ============================================================
// SearchComponent — Quick Stock Search (NSE, BSE, NSE:SME)
// ============================================================
const SearchComponent = (() => {
  let debounceTimers = {};

  function init() {
    setup('screener');
    setup('industries');
    setup('company');
  }

  function setup(prefix) {
    const input = document.getElementById(`${prefix}-search-input`);
    const dropdown = document.getElementById(`${prefix}-search-dropdown`);
    const clearBtn = document.getElementById(`${prefix}-search-clear`);
    if (!input || !dropdown) return;

    input.addEventListener('input', () => {
      const q = input.value.trim();
      if (clearBtn) clearBtn.style.display = q ? 'inline-block' : 'none';

      // Live table filtering on Screener page
      if (prefix === 'screener' && typeof Screener !== 'undefined' && Screener.filterByText) {
        Screener.filterByText(q);
      }

      if (debounceTimers[prefix]) clearTimeout(debounceTimers[prefix]);
      if (!q) {
        dropdown.classList.add('hidden');
        dropdown.innerHTML = '';
        return;
      }

      debounceTimers[prefix] = setTimeout(async () => {
        try {
          const res = await api(`/api/search?q=${encodeURIComponent(q)}`);
          renderDropdown(res.results || [], dropdown, input, prefix);
        } catch (e) {
          console.error('[Search] Failed:', e);
        }
      }, 180);
    });

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        dropdown.classList.add('hidden');
      } else if (e.key === 'Enter') {
        const first = dropdown.querySelector('.search-item');
        if (first) {
          first.click();
        } else if (input.value.trim()) {
          const sym = input.value.trim().toUpperCase();
          dropdown.classList.add('hidden');
          input.value = '';
          openCompanyFromSearch(sym, 'NSE', { symbol: sym });
        }
      }
    });

    document.addEventListener('click', (e) => {
      if (!input.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.classList.add('hidden');
      }
    });
  }

  function renderDropdown(items, dropdown, input, prefix) {
    if (!items.length) {
      dropdown.innerHTML = '<div style="padding:12px;text-align:center;color:var(--text-muted);font-size:12px;">No companies found</div>';
      dropdown.classList.remove('hidden');
      return;
    }

    dropdown.innerHTML = items.map(item => {
      const isSme = item.sector?.includes('SME') || item.name?.includes('SME');
      const isBse = item.exchange === 'BSE' || /^\d+$/.test(item.symbol);
      const badgeClass = isSme ? 'sme' : (isBse ? 'bse' : '');
      const badgeText = isSme ? 'SME' : (item.exchange || 'NSE');

      return `
        <div class="search-item" data-sym="${item.symbol}" data-exch="${item.exchange || 'NSE'}" data-name="${item.name || item.symbol}">
          <div class="search-item-left">
            <div class="search-item-sym-row">
              <span class="search-item-sym">${item.symbol}</span>
              <span class="search-item-badge ${badgeClass}">${badgeText}</span>
            </div>
            <div class="search-item-name" title="${item.name}">${item.name}</div>
          </div>
          <div class="search-item-right">
            ${item.close ? `<span class="search-item-price">₹${formatNum(item.close, 1)}</span>` : ''}
            ${item.rs_rating ? `<span class="search-item-rs" style="color:${item.rs_rating >= 80 ? 'var(--green)' : 'var(--text-secondary)'}">RS ${item.rs_rating}</span>` : ''}
          </div>
        </div>
      `;
    }).join('');

    dropdown.querySelectorAll('.search-item').forEach(el => {
      el.addEventListener('click', () => {
        const sym = el.dataset.sym;
        const exch = el.dataset.exch;
        const name = el.dataset.name;
        dropdown.classList.add('hidden');
        input.value = '';
        openCompanyFromSearch(sym, exch, { symbol: sym, name: name });
      });
    });

    dropdown.classList.remove('hidden');
  }

  function openCompanyFromSearch(sym, exch, stock) {
    document.querySelectorAll('.page').forEach(p => p.classList.add('hidden'));
    document.getElementById('page-company').classList.remove('hidden');
    document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
    CompanyPage.load(sym, exch || 'NSE', stock);
  }

  function clear(prefix) {
    const input = document.getElementById(`${prefix}-search-input`);
    const dropdown = document.getElementById(`${prefix}-search-dropdown`);
    const clearBtn = document.getElementById(`${prefix}-search-clear`);
    if (input) input.value = '';
    if (dropdown) { dropdown.innerHTML = ''; dropdown.classList.add('hidden'); }
    if (clearBtn) clearBtn.style.display = 'none';
    if (prefix === 'screener' && typeof Screener !== 'undefined' && Screener.filterByText) {
      Screener.filterByText('');
    }
  }

  return { init, setup, clear };
})();
