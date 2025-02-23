function updateTextContrast() {
    const bgColor = getComputedStyle(document.body).getPropertyValue('--background-color');
    const rgb = bgColor.match(/\d+/g);
    const brightness = Math.round(((parseInt(rgb[0]) * 299) +
                     (parseInt(rgb[1]) * 587) +
                     (parseInt(rgb[2]) * 114)) / 1000);
    
    document.documentElement.style.setProperty('--text-color', 
        brightness > 125 ? '#1a1a1a' : '#ffffff');
}

function updateAdminContrast() {
    const bgColor = getComputedStyle(document.documentElement)
        .getPropertyValue('--background-color');
    const textColor = getComputedStyle(document.documentElement)
        .getPropertyValue('--text-color');
    
    // Add contrast class if needed
    document.querySelector('.admin-panel').classList.toggle(
        'low-contrast', 
        getContrastRatio(bgColor, textColor) < 4.5
    );
}

function changeTheme(theme) {
    // Remove existing theme classes
    document.body.className = '';
    document.body.classList.add(theme);
    
    // Update CSS variables
    const root = document.documentElement;
    const styles = getComputedStyle(document.body);
    
    root.style.setProperty('--primary-color', styles.getPropertyValue('--primary-color'));
    root.style.setProperty('--background-color', styles.getPropertyValue('--background-color'));
    root.style.setProperty('--text-color', styles.getPropertyValue('--text-color'));
    root.style.setProperty('--nav-bg', styles.getPropertyValue('--nav-bg'));
    root.style.setProperty('--card-bg', styles.getPropertyValue('--card-bg'));
    root.style.setProperty('--border-color', styles.getPropertyValue('--border-color'));
    
    // Save to localStorage
    localStorage.setItem('selectedTheme', theme);
    
    // Update active state
    document.querySelectorAll('.theme-option').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.theme === theme);
    });
    
    updateTextContrast();
    updateAdminContrast();
}

// Load saved theme
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('selectedTheme') || 'minimal';
    document.body.className = savedTheme;
    
    // Add click handlers
    document.querySelectorAll('.theme-option').forEach(btn => {
        btn.addEventListener('click', () => changeTheme(btn.dataset.theme));
        if(btn.dataset.theme === savedTheme) {
            btn.classList.add('active');
        }
    });
    
    // Force update CSS variables
    changeTheme(savedTheme);
}); 