// ============================================================
// Screener.js — Screener page logic
// ============================================================

const Screener = (() => {
  let data = [];
  let filtered = [];
  let sortCol = 'rs_rating';
  let sortDir = 'desc';
  let initialized = false;
  let activeFilters = new Set(['rs80', 'price10']);
  let activeExchange = 'NSE';
  let openDropdown = null;

  function init() {
    if (!initialized) {
      initialized = true;
      setupExchangeToggle();
      setupClickOutside();
      loadSectors();
      load();
    }
  }

  function setupExchangeToggle() {
    document.querySelectorAll('#page-screener .exch-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('#page-screener .exch-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        activeExchange = btn.dataset.exch;
        loadSectors();
        load();
      });
    });
  }

  function setupClickOutside() {
    document.addEventListener('click', e => {
      if (openDropdown && !e.target.closest('.filter-dropdown')) {
        document.getElementById(`dropdown-${openDropdown}`)?.classList.remove('open');
        openDropdown = null;
      }
    });
  }

  function toggleDropdown(name) {
    const menu = document.getElementById(`dropdown-${name}`);
    if (!menu) return;
    if (openDropdown && openDropdown !== name) {
      document.getElementById(`dropdown-${openDropdown}`)?.classList.remove('open');
    }
    menu.classList.toggle('open');
    openDropdown = menu.classList.contains('open') ? name : null;
    event.stopPropagation();
  }

  function toggleFilter(filterName) {
    if (activeFilters.has(filterName)) {
      activeFilters.delete(filterName);
    } else {
      activeFilters.add(filterName);
    }
    document.getElementById(`chip-${filterName}`)?.classList.toggle('active', activeFilters.has(filterName));

    // Update RS range if rs80 toggled
    if (filterName === 'rs80') {
      const minRs = document.getElementById('min-rs');
      if (minRs) minRs.value = activeFilters.has('rs80') ? '80' : '0';
    }

    applyFilters();
  }

  async function loadSectors() {
    try {
      const res = await api(`/api/screener/sectors?exchange=${activeExchange}`);
      const sel = document.getElementById('sector-filter');
      if (sel) {
        sel.innerHTML = '<option value="">All Sectors</option>';
        (res.sectors || []).forEach(s => {
          const opt = document.createElement('option');
          opt.value = s;
          opt.textContent = s;
          sel.appendChild(opt);
        });
      }
    } catch (e) { /* Ignore */ }
  }

  async function load() {
    const loading = document.getElementById('screener-loading');
    const tableContainer = document.getElementById('screener-table-container');

    loading.style.display = 'flex';
    tableContainer.style.display = 'none';

    const params = buildParams();
    try {
      const res = await api(`/api/screener?${params}`);
      data = res.data || [];
      applyClientFilters();
      renderTable();
    } catch (e) {
      loading.innerHTML = `<div class="loading-spinner"></div><p style="color:var(--red)">Error loading data: ${e.message}</p><button class="btn-primary" onclick="Screener.load()" style="margin-top:12px">Retry</button>`;
      return;
    }

    loading.style.display = 'none';
    tableContainer.style.display = 'block';
    document.getElementById('result-count').textContent = `${filtered.length} results`;
  }

  function buildParams() {
    const params = new URLSearchParams();
    params.set('exchange', activeExchange);
    params.set('min_rs', activeFilters.has('rs80') ? (document.getElementById('min-rs')?.value || '80') : '0');
    params.set('max_rs', document.getElementById('max-rs')?.value || '99');
    params.set('above_ema200', activeFilters.has('ema200') ? 'true' : 'false');
    params.set('above_ema50', activeFilters.has('ema50') ? 'true' : 'false');
    params.set('min_price', activeFilters.has('price10') ? '10' : '0');
    params.set('min_market_cap_cr', document.getElementById('min-mktcap')?.value || '0');
    params.set('min_turnover_cr', document.getElementById('min-turnover')?.value || '0');
    params.set('volume_surge', activeFilters.has('volume') ? 'true' : 'false');
    const sector = document.getElementById('sector-filter')?.value;
    if (sector) params.set('sector', sector);
    return params.toString();
  }

  function applyFilters() {
    load();
  }

  let filterSearchText = '';

  function filterByText(text) {
    filterSearchText = (text || '').toLowerCase().trim();
    applyClientFilters();
    renderTable();
  }

  function applyClientFilters() {
    filtered = [...data];
    if (filterSearchText) {
      filtered = filtered.filter(s =>
        s.symbol.toLowerCase().includes(filterSearchText) ||
        (s.name && s.name.toLowerCase().includes(filterSearchText)) ||
        (s.sub_industry && s.sub_industry.toLowerCase().includes(filterSearchText))
      );
    }

    // Close all dropdowns
    if (openDropdown) {
      document.getElementById(`dropdown-${openDropdown}`)?.classList.remove('open');
      openDropdown = null;
    }

    sortData();
  }

  function sort(col) {
    if (sortCol === col) {
      sortDir = sortDir === 'asc' ? 'desc' : 'asc';
    } else {
      sortCol = col;
      sortDir = 'desc';
    }
    // Update header classes
    document.querySelectorAll('#screener-table th').forEach(th => {
      th.classList.remove('sorted-asc', 'sorted-desc');
      if (th.dataset.col === col) {
        th.classList.add(sortDir === 'asc' ? 'sorted-asc' : 'sorted-desc');
      }
    });
    sortData();
    renderRows();
  }

  function sortData() {
    filtered.sort((a, b) => {
      let av = a[sortCol], bv = b[sortCol];
      if (av == null) av = sortDir === 'asc' ? Infinity : -Infinity;
      if (bv == null) bv = sortDir === 'asc' ? Infinity : -Infinity;
      if (typeof av === 'string') av = av.toLowerCase();
      if (typeof bv === 'string') bv = bv.toLowerCase();
      if (av < bv) return sortDir === 'asc' ? -1 : 1;
      if (av > bv) return sortDir === 'asc' ? 1 : -1;
      return 0;
    });
  }

  function renderTable() {
    sortData();
    renderRows();
    document.getElementById('result-count').textContent = `${filtered.length} results`;
  }

  function renderRows() {
    const tbody = document.getElementById('screener-tbody');
    if (!tbody) return;

    tbody.innerHTML = '';
    const fragment = document.createDocumentFragment();

    filtered.forEach(stock => {
      const tr = document.createElement('tr');
      tr.dataset.symbol = stock.symbol;
      tr.dataset.exchange = stock.exchange || activeExchange;
      tr.addEventListener('click', () => openCompany(stock));

      const from52 = stock.from_52w_high || 0;
      const from52Class = from52 >= -5 ? 'high' : from52 >= -20 ? 'near' : 'negative';
      const rsC = rsClass(stock.rs_rating || 0);
      const exchLc = (stock.exchange || activeExchange).toLowerCase();

      tr.innerHTML = `
        <td>
          <div class="sym-cell">
            <span class="sym-tag">${stock.symbol}</span>
            <span class="sym-badge ${exchLc}">${stock.exchange || activeExchange}</span>
          </div>
        </td>
        <td style="max-width:180px;overflow:hidden;text-overflow:ellipsis">${stock.name || '—'}</td>
        <td style="color:var(--text-muted)">${stock.exchange || activeExchange}</td>
        <td style="color:var(--text-secondary);max-width:160px;overflow:hidden;text-overflow:ellipsis">${stock.sub_industry || stock.industry || '—'}</td>
        <td class="num">${formatCr(stock.market_cap)}</td>
        <td class="num">₹${formatNum(stock.close, 2)}</td>
        <td class="num">${stock.pe ? formatNum(stock.pe, 1) : '—'}</td>
        <td class="num"><span class="rs-badge ${rsC}">${stock.rs_rating || '—'}</span></td>
        <td class="num"><span class="rs-badge ${rsClass(stock.rs_3m || 0)}">${stock.rs_3m || '—'}</span></td>
        <td class="num from-52w ${from52Class}">${from52 ? from52.toFixed(1) + '%' : '—'}</td>
        <td>
          <div class="ema-dots">
            <div class="ema-dot ${stock.above_ema200 ? 'active' : ''}" title="EMA 200"></div>
            <div class="ema-dot ${stock.above_ema50 ? 'active' : ''}" title="EMA 50"></div>
          </div>
        </td>
      `;
      fragment.appendChild(tr);
    });

    tbody.appendChild(fragment);
  }

  function openCompany(stock) {
    const sym = stock.symbol;
    const exch = stock.exchange || activeExchange;
    // Navigate to company page
    document.querySelectorAll('.page').forEach(p => p.classList.add('hidden'));
    document.getElementById('page-company').classList.remove('hidden');

    // Update nav
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));

    CompanyPage.load(sym, exch, stock);
  }

  function exportCSV() {
    if (!filtered.length) return;
    const headers = ['Symbol', 'Name', 'Exchange', 'Sector', 'Sub-Industry', 'Close', 'Market Cap (Cr)', 'PE', 'RS Rating', 'RS 3M', 'From 52W High %', 'Above EMA200', 'Above EMA50'];
    const rows = filtered.map(s => [
      s.symbol, s.name, s.exchange, s.sector, s.sub_industry || s.industry,
      s.close, s.market_cap, s.pe || '', s.rs_rating, s.rs_3m,
      s.from_52w_high, s.above_ema200, s.above_ema50
    ]);

    const csv = [headers, ...rows].map(r => r.map(v => `"${v ?? ''}"`).join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `screener_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
  }

  return { init, load, sort, toggleFilter, toggleDropdown, applyFilters, exportCSV, filterByText };
})();


// ============================================================
// CompanyPage — Company detail view, Financials & Shareholding
// ============================================================
const CompanyPage = (() => {
  let currentSymbol = null;
  let currentExchange = 'NSE';
  let activeTab = 'overview';

  function setTab(tabName) {
    activeTab = tabName;
    document.querySelectorAll('.comp-tab').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.tab === tabName);
    });
    document.querySelectorAll('.company-tab-pane').forEach(pane => {
      pane.classList.toggle('active', pane.id === `comp-pane-${tabName}`);
    });
    if (tabName === 'overview' && ChartManager.resizeCompanyChart) {
      setTimeout(() => ChartManager.resizeCompanyChart(), 60);
    }
  }

  function load(symbol, exchange, stockData) {
    currentSymbol = symbol;
    currentExchange = exchange || 'NSE';
    setTab('overview');

    // Set basic info immediately from what we have
    document.getElementById('company-name').textContent = stockData?.name || symbol;
    document.getElementById('company-meta').textContent = `${currentExchange}:${symbol} · ${stockData?.sector || ''} · ${stockData?.sub_industry || stockData?.industry || ''}`;
    document.getElementById('company-price').textContent = stockData?.close ? `₹${formatNum(stockData.close, 2)}` : '—';

    // Show initial skeleton or placeholder for stats grid
    const statsGrid = document.getElementById('company-stats-grid');
    if (statsGrid) {
      statsGrid.innerHTML = `
        <div class="stat-item"><div class="stat-item-label">Market Cap</div><div class="stat-item-val">${stockData?.market_cap ? formatCr(stockData.market_cap) + ' Cr' : 'Loading...'}</div></div>
        <div class="stat-item"><div class="stat-item-label">P/E Ratio</div><div class="stat-item-val">${stockData?.pe ? formatNum(stockData.pe, 1) : 'Loading...'}</div></div>
        <div class="stat-item"><div class="stat-item-label">52W High</div><div class="stat-item-val">Loading...</div></div>
        <div class="stat-item"><div class="stat-item-label">52W Low</div><div class="stat-item-val">Loading...</div></div>
        <div class="stat-item"><div class="stat-item-label">From 52W High</div><div class="stat-item-val">${stockData?.from_52w_high ? stockData.from_52w_high.toFixed(1) + '%' : 'Loading...'}</div></div>
        <div class="stat-item"><div class="stat-item-label">RS Rating</div><div class="stat-item-val">${stockData?.rs_rating || stockData?.rs_score || 'Loading...'}</div></div>
      `;
    }

    // Load full detail
    loadDetail(symbol, currentExchange);

    // Load chart
    ChartManager.loadCompanyChart(symbol, currentExchange);

    // Pre-fetch Financials and Shareholding in background
    loadFinancials(symbol);
    loadShareholding(symbol);
  }

  async function loadDetail(symbol, exchange) {
    try {
      const data = await api(`/api/company/${symbol}?exchange=${exchange}`);

      document.getElementById('company-name').textContent = data.name || symbol;
      document.getElementById('company-meta').textContent =
        `${exchange}:${symbol} · ${data.sector || ''} · ${data.industry || ''}`;
      document.getElementById('company-price').textContent = `₹${formatNum(data.close, 2)}`;

      const change1d = data.return_1d || 0;
      const chEl = document.getElementById('company-change');
      chEl.textContent = `${change1d >= 0 ? '+' : ''}${change1d.toFixed(2)}%`;
      chEl.style.color = change1d >= 0 ? 'var(--green)' : 'var(--red)';

      // Stats grid
      const statsGrid = document.getElementById('company-stats-grid');
      const stats = [
        ['Market Cap', data.market_cap ? `${formatCr(data.market_cap)} Cr` : '—'],
        ['P/E Ratio', data.pe ? formatNum(data.pe, 1) : '—'],
        ['52W High', data['52w_high'] ? `₹${formatNum(data['52w_high'], 1)}` : '—'],
        ['52W Low', data['52w_low'] ? `₹${formatNum(data['52w_low'], 1)}` : '—'],
        ['From 52W High', `${(data.from_52w_high || 0).toFixed(1)}%`],
        ['RS Rating', data.rs_rating ? data.rs_rating : (data.rs_score_raw ? Math.round(data.rs_score_raw * 100) : '—')],
        ['Above EMA 50', data.above_ema50 ? '✅ Yes' : '❌ No'],
        ['Above EMA 200', data.above_ema200 ? '✅ Yes' : '❌ No'],
        ['ROCE', data.roce != null ? `${data.roce}%` : '—'],
        ['ROE', data.roe != null ? `${data.roe}%` : '—'],
        ['Book Value', data.book_value ? `₹${formatNum(data.book_value, 1)}` : '—'],
        ['Div Yield', data.dividend_yield != null ? `${data.dividend_yield}%` : '—'],
      ];

      statsGrid.innerHTML = stats.map(([label, val]) => `
        <div class="stat-item">
          <div class="stat-item-label">${label}</div>
          <div class="stat-item-val">${val}</div>
        </div>
      `).join('');

      // Returns table
      const returnsTable = document.getElementById('returns-table');
      const returns = [
        ['1 Day', data.return_1d],
        ['1 Week', data.return_1w],
        ['1 Month', data.return_1m],
        ['3 Months', data.return_3m],
        ['6 Months', data.return_6m],
        ['1 Year', data.return_1y],
      ];

      returnsTable.innerHTML = returns.map(([label, val]) => {
        const v = val || 0;
        const cls = v >= 0 ? 'up' : 'down';
        return `
          <div class="return-row">
            <span class="return-label">${label}</span>
            <span class="return-val ${cls}">${v >= 0 ? '+' : ''}${v.toFixed(2)}%</span>
          </div>
        `;
      }).join('');

    } catch (e) {
      console.error('[Company] Load failed:', e);
    }
  }

  async function loadFinancials(symbol, forceRefresh = false) {
    const container = document.getElementById('financials-container');
    if (!container) return;
    if (forceRefresh) {
      container.innerHTML = '<div class="panel-loading"><div class="loading-spinner small"></div> <span>Fetching quarterly financials...</span></div>';
    }

    try {
      const data = await api(`/api/company/${symbol}/financials?force_refresh=${forceRefresh}`);
      if (!data.quarters || !data.rows || !data.rows.length) {
        container.innerHTML = `
          <div class="empty-state" style="padding:40px;text-align:center;">
            <p>No quarterly financial statement found for ${symbol}.</p>
            <button class="filter-chip" style="margin-top:12px;" onclick="CompanyPage.refreshFinancials()">Retry Fetch</button>
          </div>
        `;
        return;
      }

      const quarters = data.quarters;
      const rows = data.rows;
      const latestQ = quarters && quarters.length ? quarters[quarters.length - 1] : '—';
      const subEl = document.querySelector('#comp-pane-financials .section-subtitle');
      if (subEl) {
        subEl.innerHTML = `Values in ₹ Crores · Latest reported filing: <span style="color:var(--accent);font-weight:700;">${latestQ}</span> (Sep results reflect latest Q2 filings; click Refresh to re-check)`;
      }

      let html = '<table class="fin-table">';
      // Header row
      html += '<thead><tr><th>Financial Metric</th>';
      quarters.forEach(q => {
        html += `<th>${q}</th>`;
      });
      html += '</tr></thead><tbody>';

      // Rows
      rows.forEach(r => {
        const nameLower = r.name.toLowerCase();
        const isHighlight = nameLower.includes('sales') || nameLower.includes('revenue') ||
                            nameLower.includes('operating profit') || nameLower.includes('net profit');
        const isMargin = nameLower.includes('%') || nameLower.includes('opm');

        html += `<tr class="${isHighlight ? 'fin-row-highlight' : ''}">`;
        html += `<td>${r.name}${r.unit && !r.name.includes('%') ? ` (${r.unit})` : ''}</td>`;

        (r.values || []).forEach(v => {
          let cellContent = v ?? '—';
          let cellStyle = '';
          if (v && v !== '—') {
            const cleanNum = parseFloat(String(v).replace(/,/g, '').replace(/%/g, ''));
            if (!isNaN(cleanNum)) {
              if (cleanNum < 0) cellStyle = 'color:var(--red);font-weight:600;';
              else if (isHighlight && cleanNum > 0) cellStyle = 'font-weight:600;';
            }
            if (isMargin) {
              cellContent = `<span class="fin-badge">${v}</span>`;
            }
          }
          html += `<td style="${cellStyle}">${cellContent}</td>`;
        });
        html += '</tr>';
      });

      html += '</tbody></table>';
      container.innerHTML = html;

    } catch (e) {
      console.error('[Financials] Load failed:', e);
      container.innerHTML = `
        <div class="empty-state" style="padding:40px;text-align:center;">
          <p>Failed to load financials for ${symbol}.</p>
          <button class="filter-chip" style="margin-top:12px;" onclick="CompanyPage.refreshFinancials()">Retry</button>
        </div>
      `;
    }
  }

  async function loadShareholding(symbol, forceRefresh = false) {
    const container = document.getElementById('shareholding-container');
    const bar = document.getElementById('sh-progress-bar');
    const grid = document.getElementById('sh-cards-grid');
    const asOfEl = document.getElementById('sh-as-of');

    if (forceRefresh && container) {
      container.innerHTML = '<div class="panel-loading"><div class="loading-spinner small"></div> <span>Fetching shareholding patterns...</span></div>';
    }

    try {
      const data = await api(`/api/company/${symbol}/shareholding?force_refresh=${forceRefresh}`);
      if (!data.quarters || !data.rows || !data.rows.length) {
        if (container) {
          container.innerHTML = `
            <div class="empty-state" style="padding:40px;text-align:center;">
              <p>No shareholding data available for ${symbol}.</p>
              <button class="filter-chip" style="margin-top:12px;" onclick="CompanyPage.refreshShareholding()">Retry Fetch</button>
            </div>
          `;
        }
        return;
      }

      const latest = data.latest || {};
      const quarters = data.quarters;
      const rows = data.rows;

      const latestQ = latest.quarter || (quarters && quarters.length ? quarters[quarters.length - 1] : '—');
      if (asOfEl) {
        asOfEl.innerHTML = `Ownership breakdown as of <span style="color:var(--accent);font-weight:700;">${latestQ}</span>`;
      }

      // Render Visual Distribution Bar
      if (bar) {
        const pPromoter = latest.promoters || 0;
        const pFii = latest.fiis || 0;
        const pDii = latest.diis || 0;
        const pGovt = latest.government || 0;
        const pPublic = latest.public || 0;

        bar.innerHTML = `
          <div class="sh-bar-seg promoter" style="width:${pPromoter}%" title="Promoters: ${pPromoter}%"></div>
          <div class="sh-bar-seg fii" style="width:${pFii}%" title="FIIs: ${pFii}%"></div>
          <div class="sh-bar-seg dii" style="width:${pDii}%" title="DIIs: ${pDii}%"></div>
          ${pGovt > 0 ? `<div class="sh-bar-seg govt" style="width:${pGovt}%" title="Government: ${pGovt}%"></div>` : ''}
          <div class="sh-bar-seg public" style="width:${pPublic}%" title="Public & Retail: ${pPublic}%"></div>
        `;
      }

      // Render Summary Stat Cards
      if (grid) {
        grid.innerHTML = `
          <div class="sh-stat-card promoter">
            <span class="sh-card-label"><span class="sh-card-dot promoter"></span> Promoters</span>
            <span class="sh-card-val">${latest.promoters != null ? `${latest.promoters}%` : '—'}</span>
          </div>
          <div class="sh-stat-card fii">
            <span class="sh-card-label"><span class="sh-card-dot fii"></span> FIIs / FPIs</span>
            <span class="sh-card-val">${latest.fiis != null ? `${latest.fiis}%` : '—'}</span>
          </div>
          <div class="sh-stat-card dii">
            <span class="sh-card-label"><span class="sh-card-dot dii"></span> DIIs (MFs/Ins)</span>
            <span class="sh-card-val">${latest.diis != null ? `${latest.diis}%` : '—'}</span>
          </div>
          ${latest.government > 0 ? `
            <div class="sh-stat-card govt">
              <span class="sh-card-label"><span class="sh-card-dot govt"></span> Government</span>
              <span class="sh-card-val">${latest.government}%</span>
            </div>
          ` : ''}
          <div class="sh-stat-card public">
            <span class="sh-card-label"><span class="sh-card-dot public"></span> Public / Retail</span>
            <span class="sh-card-val">${latest.public != null ? `${latest.public}%` : '—'}</span>
          </div>
          ${latest.shareholders_count ? `
            <div class="sh-stat-card total">
              <span class="sh-card-label">👥 Total Shareholders</span>
              <span class="sh-card-val" style="font-size:15px;">${latest.shareholders_count}</span>
            </div>
          ` : ''}
        `;
      }

      // Render Historical Shareholding Table
      if (container) {
        let html = '<table class="fin-table">';
        html += '<thead><tr><th>Holder Category</th>';
        quarters.forEach(q => {
          html += `<th>${q}</th>`;
        });
        html += '</tr></thead><tbody>';

        rows.forEach(r => {
          const nameLower = r.name.toLowerCase();
          const isCount = nameLower.includes('shareholder');

          html += '<tr>';
          html += `<td><strong>${r.name}</strong></td>`;
          (r.values || []).forEach(v => {
            html += `<td>${v ?? '—'}</td>`;
          });
          html += '</tr>';
        });

        html += '</tbody></table>';
        container.innerHTML = html;
      }

    } catch (e) {
      console.error('[Shareholding] Load failed:', e);
      if (container) {
        container.innerHTML = `
          <div class="empty-state" style="padding:40px;text-align:center;">
            <p>Failed to load shareholding patterns for ${symbol}.</p>
            <button class="filter-chip" style="margin-top:12px;" onclick="CompanyPage.refreshShareholding()">Retry</button>
          </div>
        `;
      }
    }
  }

  function refreshFinancials() {
    if (currentSymbol) loadFinancials(currentSymbol, true);
  }

  function refreshShareholding() {
    if (currentSymbol) loadShareholding(currentSymbol, true);
  }

  return { load, setTab, refreshFinancials, refreshShareholding };
})();
