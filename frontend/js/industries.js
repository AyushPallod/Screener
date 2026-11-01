// ============================================================
// Industries.js — Sector/Industry/Sub-Industry with Screener Leader Tracking
// ============================================================

const Industries = (() => {
  let initialized = false;
  let selectedSector = null;
  let selectedStock = null;
  let currentPeriod = '1w';
  let currentGroup = 'sector';       // 'sector', 'industry', or 'sub_industry'
  let currentExchange = 'NSE';      // 'NSE', 'BSE', or 'BOTH'
  let screenerOnly = false;         // true = only stocks passing screener (RS ≥ 80, Close > 200 EMA)
  let sortAsc = false;
  let sectorData = [];

  function init() {
    if (!initialized) {
      initialized = true;
      setupExchangeToggle();
      setupPeriodTabs();
      setupGroupTabs();
    }
    loadSectors();
  }

  function setupExchangeToggle() {
    document.querySelectorAll('.ind-exch-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.ind-exch-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentExchange = btn.dataset.exch;
        loadSectors();
      });
    });
  }

  function setupPeriodTabs() {
    document.querySelectorAll('.period-tab').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.period-tab').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentPeriod = btn.dataset.period;
        loadSectors();
      });
    });
  }

  function setupGroupTabs() {
    document.querySelectorAll('.group-tab').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.group-tab').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentGroup = btn.dataset.group;
        selectedSector = null; // Reset selection on tier change
        selectedStock = null;
        loadSectors();
      });
    });
  }

  function toggleScreenerLeaders() {
    screenerOnly = !screenerOnly;
    const btn = document.getElementById('ind-screener-toggle');
    if (btn) btn.classList.toggle('active', screenerOnly);
    selectedStock = null;
    loadSectors();
  }

  async function loadSectors() {
    const listEl = document.getElementById('sector-list');
    const loadingEl = document.getElementById('sector-list-loading');
    const colTitleEl = document.getElementById('sector-col-title');
    const periodTitleEl = document.getElementById('period-col-title');

    // Update column title based on active group tier
    if (colTitleEl) {
      if (currentGroup === 'industry') colTitleEl.textContent = 'Industry';
      else if (currentGroup === 'sub_industry') colTitleEl.textContent = 'Sub-Industry';
      else colTitleEl.textContent = 'Sector';
    }

    if (periodTitleEl) {
      periodTitleEl.textContent = `${currentPeriod.toUpperCase()} Return`;
    }

    listEl.innerHTML = '';
    loadingEl.classList.remove('hidden');

    try {
      const params = new URLSearchParams({
        exchange: currentExchange,
        period: currentPeriod,
        group_by: currentGroup,
        screener_only: screenerOnly ? 'true' : 'false',
      });

      const res = await api(`/api/industries?${params.toString()}`);
      sectorData = res.data || [];

      loadingEl.classList.add('hidden');

      if (!sectorData.length) {
        listEl.innerHTML = `<div class="empty-state">No ${currentGroup.replace('_', ' ')}s matching current filters</div>`;
        const stocksList = document.getElementById('sector-stocks-list');
        if (stocksList) stocksList.innerHTML = '<div class="empty-state">No matching stocks</div>';
        return;
      }

      renderSectorList(sectorData);

      // Reload selected sector if still present in data, else pick the first
      const exists = sectorData.some(s => s.sector === selectedSector);
      if (!exists && sectorData.length > 0) {
        selectedSector = sectorData[0].sector;
      }

      if (selectedSector) {
        loadSectorStocks(selectedSector);
      }
    } catch (e) {
      loadingEl.classList.add('hidden');
      listEl.innerHTML = `<div class="empty-state" style="color:var(--red)">Failed to load: ${e.message}</div>`;
    }
  }

  function toggleSort() {
    sortAsc = !sortAsc;
    const sorted = [...sectorData].sort((a, b) =>
      sortAsc ? a.avg_return_pct - b.avg_return_pct : b.avg_return_pct - a.avg_return_pct
    );
    renderSectorList(sorted);
  }

  function renderSectorList(data) {
    const listEl = document.getElementById('sector-list');
    listEl.innerHTML = '';

    const maxAbs = Math.max(...data.map(s => Math.abs(s.avg_return_pct)), 0.01);

    data.forEach(sector => {
      const isUp = sector.avg_return_pct >= 0;
      const barWidth = Math.round((Math.abs(sector.avg_return_pct) / maxAbs) * 100);
      const row = document.createElement('div');
      row.className = `sector-row${sector.sector === selectedSector ? ' active' : ''}`;
      row.dataset.sector = sector.sector;
      row.innerHTML = `
        <div class="sector-row-name" title="${sector.sector}">
          ${sector.sector}
          <span class="sector-row-count" title="${sector.total_stocks} stocks">${sector.total_stocks}</span>
        </div>
        <div class="sector-return-bar">
          <div class="mini-bar">
            <div class="mini-bar-fill ${isUp ? 'up' : 'down'}" style="width:${barWidth}%"></div>
          </div>
          <span class="sector-return-val ${isUp ? 'up' : 'down'}">
            ${isUp ? '+' : ''}${sector.avg_return_pct.toFixed(2)}%
          </span>
        </div>
      `;
      row.addEventListener('click', () => {
        document.querySelectorAll('.sector-row').forEach(r => r.classList.remove('active'));
        row.classList.add('active');
        selectedSector = sector.sector;
        loadSectorStocks(sector.sector);
      });
      listEl.appendChild(row);
    });
  }

  async function loadSectorStocks(sectorName) {
    const stocksList = document.getElementById('sector-stocks-list');
    const loadingEl = document.getElementById('sector-stocks-loading');
    const headerEl = document.getElementById('selected-sector-name');
    const countEl = document.getElementById('sector-stock-count');

    stocksList.innerHTML = '';
    loadingEl.classList.remove('hidden');
    headerEl.textContent = sectorName;

    try {
      const params = new URLSearchParams({
        exchange: currentExchange,
        period: currentPeriod,
        group_by: currentGroup,
        screener_only: screenerOnly ? 'true' : 'false',
      });

      const res = await api(`/api/industries/${encodeURIComponent(sectorName)}/stocks?${params.toString()}`);
      const stocks = res.stocks || [];

      loadingEl.classList.add('hidden');
      countEl.textContent = `${stocks.length} stock${stocks.length === 1 ? '' : 's'}`;

      if (!stocks.length) {
        stocksList.innerHTML = '<div class="empty-state">No matching stocks in this tier</div>';
        return;
      }

      stocks.forEach((stock, idx) => {
        const isUp = stock.period_return >= 0;
        const row = document.createElement('div');
        row.className = `stock-row${stock.symbol === selectedStock ? ' active' : ''}`;
        row.dataset.symbol = stock.symbol;
        row.innerHTML = `
          <div class="stock-row-sym" title="${stock.name || stock.symbol}">
            ${stock.symbol}
            <span class="badge" style="font-size:9px;padding:1px 4px;margin-left:4px;background:var(--bg-card);color:var(--text-muted);border:1px solid var(--border)">${stock.exchange || 'NSE'}</span>
          </div>
          <div class="stock-row-rs" style="color:${stock.rs_score >= 80 ? 'var(--green)' : stock.rs_score >= 50 ? 'var(--accent)' : 'var(--text-muted)'}" title="Screener RS Rating: ${stock.rs_score}">${Math.round(stock.rs_score) || '—'}</div>
          <div class="stock-row-return ${isUp ? 'up' : 'down'}">
            ${isUp ? '+' : ''}${stock.period_return.toFixed(2)}%
          </div>
        `;
        row.addEventListener('click', () => {
          document.querySelectorAll('.stock-row').forEach(r => r.classList.remove('active'));
          row.classList.add('active');
          selectedStock = stock.symbol;
          loadChart(stock);
        });
        row.addEventListener('dblclick', () => {
          document.querySelectorAll('.page').forEach(p => p.classList.add('hidden'));
          document.getElementById('page-company').classList.remove('hidden');
          document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
          CompanyPage.load(stock.symbol, stock.exchange || currentExchange || 'NSE', stock);
        });
        stocksList.appendChild(row);

        // Auto-load first stock chart if nothing selected
        if (idx === 0 && (!selectedStock || !stocks.some(s => s.symbol === selectedStock))) {
          row.classList.add('active');
          selectedStock = stock.symbol;
          loadChart(stock);
        }
      });
    } catch (e) {
      loadingEl.classList.add('hidden');
      stocksList.innerHTML = `<div class="empty-state" style="color:var(--red)">Error: ${e.message}</div>`;
    }
  }

  function loadChart(stock) {
    const symEl = document.getElementById('chart-symbol');
    symEl.innerHTML = `<span style="cursor:pointer;text-decoration:underline;text-underline-offset:3px;" title="Click to view full financial results & shareholding">${stock.symbol} · ${stock.name || ''} ↗</span>`;
    symEl.onclick = () => {
      document.querySelectorAll('.page').forEach(p => p.classList.add('hidden'));
      document.getElementById('page-company').classList.remove('hidden');
      document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
      CompanyPage.load(stock.symbol, stock.exchange || currentExchange || 'NSE', stock);
    };
    document.getElementById('chart-price').textContent = stock.close ? `₹${formatNum(stock.close, 2)}` : '';
    document.getElementById('chart-empty').style.display = 'none';
    ChartManager.loadIndustriesChart(stock.symbol, stock.exchange || currentExchange || 'NSE');
  }

  function copyList() {
    const stocks = [...document.querySelectorAll('#sector-stocks-list .stock-row-sym')]
      .map(el => el.textContent.trim().split(/\s+/)[0]);
    navigator.clipboard.writeText(stocks.join('\n'))
      .then(() => alert(`Copied ${stocks.length} symbols`))
      .catch(() => {});
  }

  return { init, toggleSort, toggleScreenerLeaders, copyList };
})();
