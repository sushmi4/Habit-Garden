/**
 * Habit Garden - Main JavaScript
 * 
 * This file contains global JavaScript functionality
 * that applies across the entire application.
 */

/**
 * Initialize the application when the DOM is fully loaded.
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('🌱 Habit Garden loaded!');
    
    // Initialize any global features
    initNavigation();
    initMessages();
});

/**
 * Initialize navigation highlighting.
 * 
 * Adds an 'active' class to the current page's navigation link.
 */
function initNavigation() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-menu a');
    
    navLinks.forEach(link => {
        // Get the link's href path
        const linkPath = new URL(link.href).pathname;
        
        // Highlight if it matches the current path
        if (currentPath === linkPath || 
            (linkPath !== '/' && currentPath.startsWith(linkPath))) {
            link.classList.add('active');
        }
    });
}

/**
 * Initialize message auto-dismiss.
 * 
 * Messages from Django's messages framework will auto-dismiss after 5 seconds.
 */
function initMessages() {
    const messages = document.querySelectorAll('.messages li');
    
    messages.forEach(message => {
        // Add click to dismiss
        message.addEventListener('click', function() {
            this.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => this.remove(), 300);
        });
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (message.parentNode) {
                message.style.animation = 'fadeOut 0.3s ease';
                setTimeout(() => message.remove(), 300);
            }
        }, 5000);
    });
}

/**
 * Show a loading state on a button.
 * 
 * @param {HTMLElement} button - The button element
 * @param {string} text - Loading text to display
 */
function showLoading(button, text = 'Loading...') {
    button.disabled = true;
    button.dataset.originalText = button.textContent;
    button.textContent = text;
}

/**
 * Hide loading state on a button.
 * 
 * @param {HTMLElement} button - The button element
 */
function hideLoading(button) {
    button.disabled = false;
    button.textContent = button.dataset.originalText || 'Submit';
}

/**
 * Format a date as a readable string.
 * 
 * @param {Date|string} date - The date to format
 * @returns {string} Formatted date string
 */
function formatDate(date) {
    const d = new Date(date);
    return d.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

/**
 * Debounce function - limits how often a function can be called.
 * 
 * @param {Function} func - The function to debounce
 * @param {number} wait - Milliseconds to wait
 * @returns {Function} Debounced function
 */
function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Add CSS for message animations
const mainStyle = document.createElement('style');
mainStyle.textContent = `
    @keyframes fadeOut {
        from { opacity: 1; }
        to { opacity: 0; }
    }
    
    .messages li {
        cursor: pointer;
    }
`;
document.head.appendChild(mainStyle);
