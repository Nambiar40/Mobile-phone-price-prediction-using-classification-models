// Admin Interactions

function setupAdminInteractions() {
  // Sidebar Toggle
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.querySelector('.admin-sidebar');
  
  if (sidebarToggle && sidebar && !sidebar.dataset.bound) {
    sidebar.dataset.bound = 'true';
    sidebarToggle.addEventListener('click', () => {
      sidebar.style.display = sidebar.style.display === 'none' ? 'flex' : 'none';
      // In a real app we'd toggle a class to shrink it rather than display: none
    });
  }

  // Theme Toggle
  const themeToggle = document.getElementById('themeToggle');
  if (themeToggle && !themeToggle.dataset.bound) {
    themeToggle.dataset.bound = 'true';
    themeToggle.addEventListener('click', () => {
      document.body.classList.toggle('light-theme');
      if (document.body.classList.contains('light-theme')) {
        themeToggle.classList.remove('fa-sun');
        themeToggle.classList.add('fa-moon');
      } else {
        themeToggle.classList.remove('fa-moon');
        themeToggle.classList.add('fa-sun');
      }
      
      // Update Chart.js defaults if charts exist
      if (window.updateChartTheme) {
        window.updateChartTheme(document.body.classList.contains('light-theme'));
      }
    });
  }
}

document.addEventListener('layoutReady', setupAdminInteractions);

// Fallback in case layout is already injected
if (document.querySelector('.admin-sidebar')) {
  setupAdminInteractions();
}

// Toast Notification System
window.showToast = function(title, message, type = 'success') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  
  let iconClass = 'fa-check-circle';
  if (type === 'error') iconClass = 'fa-circle-exclamation';
  if (type === 'info') iconClass = 'fa-info-circle';

  toast.innerHTML = `
    <i class="fa-solid ${iconClass} toast-icon"></i>
    <div class="toast-content">
      <div class="toast-title">${title}</div>
      <div class="toast-msg">${message}</div>
    </div>
    <button class="toast-close"><i class="fa-solid fa-times"></i></button>
  `;

  container.appendChild(toast);

  const closeBtn = toast.querySelector('.toast-close');
  closeBtn.addEventListener('click', () => {
    toast.style.animation = 'fadeOut 0.3s ease forwards';
    setTimeout(() => toast.remove(), 300);
  });

  setTimeout(() => {
    if(toast.parentElement) {
      toast.style.animation = 'fadeOut 0.3s ease forwards';
      setTimeout(() => toast.remove(), 300);
    }
  }, 5000);
};

// Expose simple functions for HTML buttons to call
window.deleteItem = function(itemName) {
  if(confirm(`Are you sure you want to delete ${itemName}?`)) {
    window.showToast('Deleted', `${itemName} has been deleted successfully.`, 'success');
  }
};
