// Chart.js Configuration for Admin Panel

// Setup global defaults
Chart.defaults.color = '#9CA3AF'; // text-secondary
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.scale.grid.color = 'rgba(255, 255, 255, 0.05)';
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(17, 24, 39, 0.9)';
Chart.defaults.plugins.tooltip.titleColor = '#fff';
Chart.defaults.plugins.tooltip.padding = 12;
Chart.defaults.plugins.tooltip.cornerRadius = 8;
Chart.defaults.plugins.tooltip.borderColor = 'rgba(255,255,255,0.1)';
Chart.defaults.plugins.tooltip.borderWidth = 1;

window.updateChartTheme = function(isLight) {
  Chart.defaults.color = isLight ? '#475569' : '#9CA3AF';
  Chart.defaults.scale.grid.color = isLight ? 'rgba(0, 0, 0, 0.05)' : 'rgba(255, 255, 255, 0.05)';
  Chart.defaults.plugins.tooltip.backgroundColor = isLight ? 'rgba(255, 255, 255, 0.9)' : 'rgba(17, 24, 39, 0.9)';
  Chart.defaults.plugins.tooltip.titleColor = isLight ? '#0F172A' : '#fff';
  Chart.defaults.plugins.tooltip.bodyColor = isLight ? '#475569' : '#fff';
  
  // Re-render all charts
  for (let id in Chart.instances) {
    Chart.instances[id].update();
  }
};

window.renderDashboardCharts = function() {
  const ctxActivity = document.getElementById('activityChart');
  if (ctxActivity) {
    new Chart(ctxActivity, {
      type: 'line',
      data: {
        labels: ['1', '5', '10', '15', '20', '25', '30'],
        datasets: [{
          label: 'Total Predictions',
          data: [150, 230, 224, 318, 450, 520, 610],
          borderColor: '#7C3AED',
          backgroundColor: 'rgba(124, 58, 237, 0.1)',
          borderWidth: 3,
          fill: true,
          tension: 0.4,
          pointBackgroundColor: '#7C3AED',
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true },
          x: { grid: { display: false } }
        }
      }
    });
  }

  const ctxDist = document.getElementById('distChart');
  if (ctxDist) {
    new Chart(ctxDist, {
      type: 'doughnut',
      data: {
        labels: ['Current', 'Future', 'Resale', 'OCR'],
        datasets: [{
          data: [45, 25, 20, 10],
          backgroundColor: [
            '#7C3AED', // Primary
            '#3B82F6', // Secondary
            '#10B981', // Success
            '#F97316'  // Orange
          ],
          borderWidth: 0,
          hoverOffset: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '75%',
        plugins: {
          legend: { position: 'bottom', labels: { padding: 20, usePointStyle: true } }
        }
      }
    });
  }

  const ctxBrands = document.getElementById('brandsChart');
  if (ctxBrands) {
    new Chart(ctxBrands, {
      type: 'bar',
      data: {
        labels: ['Apple', 'Samsung', 'OnePlus', 'Xiaomi', 'Google', 'Vivo'],
        datasets: [{
          label: 'Searches',
          data: [1200, 1050, 800, 650, 500, 450],
          backgroundColor: '#3B82F6',
          borderRadius: 6,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true },
          x: { grid: { display: false } }
        }
      }
    });
  }
};

window.renderAnalyticsCharts = function() {
  // Similar logic for deeper analytics page charts
  const ctxTrend = document.getElementById('analyticsTrendChart');
  if (ctxTrend) {
    new Chart(ctxTrend, {
      type: 'line',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        datasets: [
          {
            label: 'New Users',
            data: [65, 78, 90, 115, 140, 180, 220, 250, 210, 280, 310, 350],
            borderColor: '#10B981',
            tension: 0.4
          },
          {
            label: 'Predictions Made',
            data: [200, 350, 420, 600, 800, 1200, 1450, 1600, 1400, 1800, 2100, 2500],
            borderColor: '#7C3AED',
            tension: 0.4
          }
        ]
      },
      options: { responsive: true, maintainAspectRatio: false }
    });
  }
  
  const ctxRam = document.getElementById('ramChart');
  if(ctxRam) {
    new Chart(ctxRam, {
      type: 'polarArea',
      data: {
        labels: ['4GB', '6GB', '8GB', '12GB', '16GB'],
        datasets: [{
          data: [10, 25, 45, 15, 5],
          backgroundColor: [
            'rgba(249, 115, 22, 0.7)',
            'rgba(16, 185, 129, 0.7)',
            'rgba(124, 58, 237, 0.7)',
            'rgba(59, 130, 246, 0.7)',
            'rgba(239, 68, 68, 0.7)'
          ]
        }]
      },
      options: { responsive: true, maintainAspectRatio: false }
    });
  }
};
