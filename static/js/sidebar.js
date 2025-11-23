document.addEventListener("DOMContentLoaded", () => {
  const body = document.body;
  const sidebar = document.querySelector(".sidebar");
  const toggles = Array.from(document.querySelectorAll('#sidebarToggle, [data-toggle="sidebar"]'));

  // Cambia el ícono según estado
  const updateIcon = (btn) => {
    if (!btn) return;
    const i = btn.querySelector('i');
    if (!i) return;

    const isDesktop = window.innerWidth >= 992;
    const mobileOpen = body.classList.contains('show-sidebar');
    const desktopCollapsed = body.classList.contains('sidebar-collapsed');

    i.classList.remove('fa-bars', 'fa-xmark', 'fa-angles-left', 'fa-angles-right');

    if (!isDesktop) {
      i.classList.add(mobileOpen ? 'fa-xmark' : 'fa-bars');
    } else {
      i.classList.add(desktopCollapsed ? 'fa-angles-right' : 'fa-bars');
    }
  };

  const updateAllIcons = () => toggles.forEach(updateIcon);

  const handleToggle = (e) => {
    e.preventDefault();

    if (window.innerWidth >= 992) {
      body.classList.toggle('sidebar-collapsed');
      body.classList.remove('show-sidebar');
    } else {
      body.classList.toggle('show-sidebar');
      body.classList.remove('sidebar-collapsed');
    }

    updateAllIcons();
  };

  toggles.forEach(btn => btn.addEventListener('click', handleToggle));

  // Click fuera cierra el sidebar (solo móvil)
  document.addEventListener('click', (e) => {
    const isMobileOpen = body.classList.contains('show-sidebar') && window.innerWidth < 992;
    const clickedToggle = e.target.closest('#sidebarToggle, [data-toggle="sidebar"]');
    if (!isMobileOpen) return;
    if (clickedToggle) return;
    if (sidebar && !sidebar.contains(e.target)) {
      body.classList.remove('show-sidebar');
      updateAllIcons();
    }
  });

  // Corrige clases al redimensionar
  window.addEventListener('resize', () => {
    if (window.innerWidth >= 992) {
      body.classList.remove('show-sidebar'); // no overlay en desktop
    } else {
      body.classList.remove('sidebar-collapsed'); // no colapsado en móvil
    }
    updateAllIcons();
  });

  // Estado inicial
  updateAllIcons();
});
