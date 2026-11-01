// ============================================================
// Chart.js — TradingView chart integration
// ============================================================

const ChartManager = (() => {
  let industriesChart = null;
  let companyChart = null;

  const CHART_OPTIONS = {
    layout: {
      background: { color: '#0A0E1A' },
      textColor: '#8895B3',
    },
    grid: {
      vertLines: { color: '#1e2d4a', style: 1 },
      horzLines: { color: '#1e2d4a', style: 1 },
    },
    crosshair: {
      mode: LightweightCharts.CrosshairMode.Normal,
    },
    rightPriceScale: {
      borderColor: '#1e2d4a',
    },
    timeScale: {
      borderColor: '#1e2d4a',
      timeVisible: true,
    },
    handleScroll: true,
    handleScale: true,
  };

  const chartObservers = new Map();

  function createChart(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return null;

    // Disconnect any existing observer on this container
    if (chartObservers.has(containerId)) {
      chartObservers.get(containerId).disconnect();
      chartObservers.delete(containerId);
    }

    container.innerHTML = '';

    const width = container.clientWidth || 600;
    const height = container.clientHeight || 400;

    const chart = LightweightCharts.createChart(container, {
      ...CHART_OPTIONS,
      width: width,
      height: height,
    });

    let resizeTimer = null;
    const ro = new ResizeObserver(entries => {
      if (resizeTimer) return;
      resizeTimer = requestAnimationFrame(() => {
        resizeTimer = null;
        for (const entry of entries) {
          const w = Math.floor(entry.contentRect.width);
          const h = Math.floor(entry.contentRect.height);
          if (w > 50 && h > 50) {
            chart.applyOptions({ width: w, height: h });
          }
        }
      });
    });
    ro.observe(container);
    chartObservers.set(containerId, ro);

    return chart;
  }

  async function loadIndustriesChart(symbol, exchange) {
    if (industriesChart) {
      industriesChart.remove();
      industriesChart = null;
    }

    industriesChart = createChart('tv-chart');
    if (!industriesChart) return;

    await loadCandleData(industriesChart, symbol, exchange);
  }

  async function loadCompanyChart(symbol, exchange) {
    if (companyChart) {
      companyChart.remove();
      companyChart = null;
    }

    companyChart = createChart('company-tv-chart');
    if (!companyChart) return;

    await loadCandleData(companyChart, symbol, exchange);
  }

  async function loadCandleData(chart, symbol, exchange) {
    try {
      const suffix = exchange === 'NSE' ? '.NS' : '.BO';
      const yahooSym = encodeURIComponent(`${symbol}${suffix}`);
      
      // Fetch OHLCV from our backend proxy (avoid CORS)
      const res = await fetch(`/api/company/${symbol}/ohlcv?exchange=${exchange}`);
      let candles = [];

      if (res.ok) {
        const data = await res.json();
        candles = data.candles || [];
      } else {
        // Fallback: generate mock data for demo
        candles = generateMockCandles(symbol);
      }

      if (!candles.length) {
        candles = generateMockCandles(symbol);
      }

      const candleSeries = chart.addCandlestickSeries({
        upColor: '#10B981',
        downColor: '#EF4444',
        borderUpColor: '#10B981',
        borderDownColor: '#EF4444',
        wickUpColor: '#10B981',
        wickDownColor: '#EF4444',
      });

      // Price candles occupy top 74% of chart height
      candleSeries.priceScale().applyOptions({
        scaleMargins: {
          top: 0.08,
          bottom: 0.26,
        },
      });

      candleSeries.setData(candles);

      // Add EMA 50
      const ema50 = chart.addLineSeries({
        color: '#F59E0B',
        lineWidth: 1,
        title: 'EMA 50',
      });
      ema50.setData(calcEMA(candles, 50));

      // Add EMA 200
      const ema200 = chart.addLineSeries({
        color: '#3B82F6',
        lineWidth: 1,
        title: 'EMA 200',
      });
      ema200.setData(calcEMA(candles, 200));

      // Compute 20-period moving average of volume and detect spikes
      const volumeData = [];
      const VOL_MA_PERIOD = 20;

      for (let i = 0; i < candles.length; i++) {
        const c = candles[i];
        const v = c.volume || 0;
        const isUp = c.close >= c.open;

        let avgVol = 0;
        if (i >= VOL_MA_PERIOD) {
          let sum = 0;
          for (let j = i - VOL_MA_PERIOD; j < i; j++) {
            sum += (candles[j].volume || 0);
          }
          avgVol = sum / VOL_MA_PERIOD;
        } else if (i > 0) {
          let sum = 0;
          for (let j = 0; j < i; j++) sum += (candles[j].volume || 0);
          avgVol = sum / i;
        }

        const isSpike = avgVol > 0 && v >= (2.0 * avgVol);

        // Highlight volume spikes with vivid solid colors, regular volume with translucent tint
        let barColor = isUp ? 'rgba(16, 185, 129, 0.35)' : 'rgba(239, 68, 68, 0.35)';
        if (isSpike) {
          barColor = isUp ? '#10B981' : '#EF4444';
        }

        volumeData.push({
          time: c.time,
          value: v,
          color: barColor,
        });
      }

      // Add Volume Series positioned in bottom 22% of chart
      const volumeSeries = chart.addHistogramSeries({
        priceFormat: {
          type: 'volume',
        },
        priceScaleId: '', // Overlay scale
      });

      chart.priceScale('').applyOptions({
        scaleMargins: {
          top: 0.78,
          bottom: 0,
        },
      });

      volumeSeries.setData(volumeData);

      chart.timeScale().fitContent();

    } catch (e) {
      console.error('[Chart] Failed to load data:', e);
      // Show mock data
      const candles = generateMockCandles(symbol);
      const candleSeries = chart.addCandlestickSeries({
        upColor: '#10B981',
        downColor: '#EF4444',
      });
      candleSeries.priceScale().applyOptions({
        scaleMargins: { top: 0.08, bottom: 0.26 },
      });
      candleSeries.setData(candles);

      const volumeSeries = chart.addHistogramSeries({
        priceFormat: { type: 'volume' },
        priceScaleId: '',
      });
      chart.priceScale('').applyOptions({
        scaleMargins: { top: 0.78, bottom: 0 },
      });
      volumeSeries.setData(candles.map(c => ({
        time: c.time,
        value: c.volume || 100000,
        color: c.close >= c.open ? 'rgba(16, 185, 129, 0.4)' : 'rgba(239, 68, 68, 0.4)',
      })));

      chart.timeScale().fitContent();
    }
  }

  function calcEMA(candles, period) {
    if (!candles.length) return [];
    const k = 2 / (period + 1);
    const result = [];
    let ema = null;

    candles.forEach((c, i) => {
      const close = c.close;
      if (i < period - 1) return;
      if (ema === null) {
        // Seed with SMA
        const seed = candles.slice(i - period + 1, i + 1);
        ema = seed.reduce((acc, s) => acc + s.close, 0) / period;
      } else {
        ema = close * k + ema * (1 - k);
      }
      result.push({ time: c.time, value: parseFloat(ema.toFixed(2)) });
    });

    return result;
  }

  function generateMockCandles(symbol) {
    // Generate realistic-looking OHLCV data for demonstration
    const candles = [];
    const now = Math.floor(Date.now() / 1000);
    const daySeconds = 86400;
    let price = 100 + Math.random() * 900;
    const vol = 0.015 + Math.random() * 0.02;

    for (let i = 365; i >= 0; i--) {
      const t = now - i * daySeconds;
      // Skip weekends
      const d = new Date(t * 1000);
      if (d.getDay() === 0 || d.getDay() === 6) continue;

      const change = (Math.random() - 0.47) * vol * price;
      const open = price;
      const close = Math.max(price + change, 1);
      const high = Math.max(open, close) * (1 + Math.random() * 0.01);
      const low = Math.min(open, close) * (1 - Math.random() * 0.01);
      price = close;

      candles.push({
        time: Math.floor(t),
        open: parseFloat(open.toFixed(2)),
        high: parseFloat(high.toFixed(2)),
        low: parseFloat(low.toFixed(2)),
        close: parseFloat(close.toFixed(2)),
        volume: Math.floor(150000 + Math.random() * 600000),
      });
    }
    return candles;
  }

  function resizeCompanyChart() {
    if (companyChart) {
      const container = document.getElementById('company-tv-chart');
      if (container && container.clientWidth > 50 && container.clientHeight > 50) {
        companyChart.applyOptions({
          width: container.clientWidth,
          height: container.clientHeight,
        });
        companyChart.timeScale().fitContent();
      }
    }
  }

  return { loadIndustriesChart, loadCompanyChart, resizeCompanyChart };
})();
