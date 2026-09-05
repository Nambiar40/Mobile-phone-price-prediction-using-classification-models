// Layout Injection Script

const sidebarHTML = `
<aside class="sidebar admin-sidebar">
  <div class="sidebar-brand">
    <div class="sidebar-logo"><i class="fa-solid fa-robot"></i></div>
    <div class="sidebar-title">Price Predict AI</div>
  </div>
  
  <ul class="sidebar-menu">
    <li class="menu-item"><a href="index.html" class="menu-link" data-path="index.html"><i class="fa-solid fa-gauge-high"></i> Dashboard</a></li>
    <li class="menu-item"><a href="users.html" class="menu-link" data-path="users.html"><i class="fa-solid fa-users"></i> User Management</a></li>
    <li class="menu-item"><a href="predictions.html" class="menu-link" data-path="predictions.html"><i class="fa-solid fa-chart-line"></i> Predictions</a></li>
    <li class="menu-item"><a href="ocr.html" class="menu-link" data-path="ocr.html"><i class="fa-solid fa-camera"></i> OCR Management</a></li>
    <li class="menu-item"><a href="datasets.html" class="menu-link" data-path="datasets.html"><i class="fa-solid fa-database"></i> Datasets</a></li>
    <li class="menu-item"><a href="models.html" class="menu-link" data-path="models.html"><i class="fa-solid fa-brain"></i> AI Models</a></li>
    <li class="menu-item"><a href="analytics.html" class="menu-link" data-path="analytics.html"><i class="fa-solid fa-chart-pie"></i> Analytics</a></li>
    <li class="menu-item"><a href="reports.html" class="menu-link" data-path="reports.html"><i class="fa-solid fa-file-invoice"></i> Reports</a></li>
    <li class="menu-item"><a href="notifications.html" class="menu-link" data-path="notifications.html"><i class="fa-solid fa-bell"></i> Notifications <span style="margin-left: auto; background: var(--primary-color); color: white; border-radius: 99px; padding: 2px 8px; font-size: 0.7rem;">3</span></a></li>
    <li class="menu-item"><a href="logs.html" class="menu-link" data-path="logs.html"><i class="fa-solid fa-clipboard-list"></i> Activity Logs</a></li>
  </ul>
  
  <div class="sidebar-footer">
    <ul class="sidebar-menu">
      <li class="menu-item"><a href="settings.html" class="menu-link" data-path="settings.html"><i class="fa-solid fa-gear"></i> Settings</a></li>
      <li class="menu-item"><a href="profile.html" class="menu-link" data-path="profile.html"><i class="fa-solid fa-user-tie"></i> Profile</a></li>
      <li class="menu-item"><a href="../index.html" class="menu-link text-danger" style="color: #EF4444;"><i class="fa-solid fa-arrow-right-from-bracket"></i> Logout</a></li>
    </ul>
  </div>
</aside>
`;

const navbarHTML = `
<nav class="top-navbar">
  <div class="flex items-center gap-4">
    <i class="fa-solid fa-bars nav-icon" id="sidebarToggle"></i>
    <div class="search-bar" style="width: 350px;">
      <i class="fa-solid fa-search text-secondary"></i>
      <input type="text" placeholder="Global search (Ctrl+K)..." />
    </div>
  </div>
  
  <div class="nav-actions">
    <i class="fa-solid fa-sun nav-icon" id="themeToggle" title="Toggle Theme"></i>
    <div style="position: relative; margin-right: 1rem;">
      <i class="fa-solid fa-bell nav-icon"></i>
      <span style="position: absolute; top: -5px; right: -5px; width: 8px; height: 8px; background: #EF4444; border-radius: 50%;" class="pulse"></span>
    </div>
    <div class="user-profile">
      <img src="https://ui-avatars.com/api/?name=Admin+User&background=7C3AED&color=fff" class="user-avatar" alt="Admin" style="border: 2px solid var(--border-color);" />
      <div class="user-info">
        <span class="user-name">Admin User</span>
        <span class="user-role">Super Admin</span>
      </div>
      <i class="fa-solid fa-chevron-down text-secondary" style="font-size: 0.75rem; margin-left: 0.5rem;"></i>
    </div>
  </div>
</nav>
`;

function initLayout() {
  // Check if we are in admin-layout container
  const appContainer = document.getElementById('admin-app');
  if (!appContainer) return;
  
  // Prevent double injection
  if (appContainer.classList.contains('layout-injected')) return;
  appContainer.classList.add('layout-injected');

  const originalContent = appContainer.innerHTML;

  // Render Layout
  appContainer.innerHTML = sidebarHTML + `
    <main class="admin-main">
      ${navbarHTML}
      <div class="admin-content page-transition" id="admin-page-content">
        ${originalContent}
      </div>
    </main>
  `;

  // Highlight active menu item
  const currentPath = window.location.pathname.split('/').pop() || 'index.html';
  const menuLinks = document.querySelectorAll('.menu-link');
  menuLinks.forEach(link => {
    if (link.getAttribute('data-path') === currentPath) {
      link.classList.add('active');
    }
  });

  // Re-dispatch event so admin.js knows layout is ready
  setTimeout(() => {
    document.dispatchEvent(new Event('layoutReady'));
  }, 50);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initLayout);
} else {
  initLayout();
}
