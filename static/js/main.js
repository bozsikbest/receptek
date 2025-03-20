// Theme switching functionality
function setTheme(theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);
    const themeLink = document.getElementById('theme-link');
    const themeIcon = document.getElementById('theme-icon');
    
    if (typeof updateTinyMCETheme === 'function') {
        updateTinyMCETheme();
    }

    if (theme === 'light') {
        themeLink.href = 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css';
        themeIcon.className = 'fa fa-moon-o';
    } else {
        themeLink.href = 'https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css';
        themeIcon.className = 'fa fa-sun-o';
    }
    localStorage.setItem('theme', theme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-bs-theme');
    setTheme(currentTheme === 'dark' ? 'light' : 'dark');
}

// Load saved theme preference
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);
});
