/**
 * Habits App - JavaScript
 * 
 * This file handles dynamic interactions on the dashboard,
 * specifically the habit completion toggle feature.
 */

/**
 * Toggle habit completion for today.
 * 
 * This function is called when the user clicks the "Mark Complete" button.
 * It sends an AJAX request to the server and updates the UI without reloading.
 * 
 * @param {number} habitId - The ID of the habit to toggle
 */
function toggleComplete(habitId) {
    // Get the habit card element
    const habitCard = document.querySelector(`[data-habit-id="${habitId}"]`);
    if (!habitCard) {
        console.error('Habit card not found for ID:', habitId);
        return;
    }
    const completeBtn = habitCard.querySelector('.complete-btn');
    const streakCount = habitCard.querySelector('.streak-count');

    if (!completeBtn) {
        console.error('Complete button not found in habit card:', habitId);
        return;
    }

    // Disable the button while processing
    completeBtn.disabled = true;

    // Get the CSRF token from cookies (required for Django POST requests)
    const csrfToken = getCookie('csrftoken');
    if (!csrfToken) {
        console.error('CSRF token not found in cookies');
        showMessage('Session error. Please refresh the page.', 'error');
        completeBtn.disabled = false;
        return;
    }

    // Send AJAX request to toggle completion
    fetch(`/habits/${habitId}/complete/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin',
    })
    .then(response => {
        return response.json().then(data => {
            if (!response.ok) {
                throw new Error(data.error || `Server error (${response.status})`);
            }
            return data;
        });
    })
    .then(data => {
        if (data.success) {
            // Update the UI based on the response
            if (data.completed) {
                // Habit was just completed
                habitCard.classList.add('completed');
                completeBtn.classList.add('completed');
                completeBtn.textContent = '✓ Completed';
            } else {
                // Habit was just uncompleted
                habitCard.classList.remove('completed');
                completeBtn.classList.remove('completed');
                completeBtn.textContent = 'Mark Complete';
            }
            
            // Update the streak count
            if (streakCount) {
                streakCount.textContent = data.streak;
            }
            
            // Update dashboard stats
            const completedCountEl = document.getElementById('completed-count');
            const progressPercentageEl = document.getElementById('progress-percentage');
            const progressRingCircle = document.getElementById('progress-ring-circle');
            
            if (completedCountEl) {
                completedCountEl.textContent = data.completed_today;
            }
            if (progressPercentageEl) {
                progressPercentageEl.textContent = data.completion_rate + '%';
            }
            if (progressRingCircle) {
                progressRingCircle.style.strokeDashoffset = data.ring_offset;
            }
            
            // Show a success message
            showMessage(data.message, 'success');
        } else {
            // Error occurred
            showMessage('Something went wrong. Please try again.', 'error');
        }
    })
    .catch(error => {
        console.error('Toggle complete error:', error);
        showMessage('Network error. Please try again.', 'error');
    })
    .finally(() => {
        // Re-enable the button
        completeBtn.disabled = false;
    });
}

/**
 * Get a cookie value by name.
 * 
 * This is needed to get the CSRF token for Django's CSRF protection.
 * 
 * @param {string} name - The name of the cookie
 * @returns {string|null} The cookie value or null if not found
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Show a temporary message to the user.
 * 
 * Creates a message element and displays it at the top of the page.
 * The message disappears after 3 seconds.
 * 
 * @param {string} message - The message to display
 * @param {string} type - The message type ('success', 'error', 'info')
 */
function showMessage(message, type = 'info') {
    // Remove any existing messages
    const existingMessages = document.querySelectorAll('.toast-message');
    existingMessages.forEach(msg => msg.remove());
    
    // Create new message element
    const messageEl = document.createElement('div');
    messageEl.className = `toast-message toast-${type}`;
    messageEl.textContent = message;
    
    // Add styles
    messageEl.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 16px 24px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        animation: slideIn 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    `;
    
    // Set background color based on type
    switch (type) {
        case 'success':
            messageEl.style.background = '#4CAF50';
            break;
        case 'error':
            messageEl.style.background = '#E57373';
            break;
        default:
            messageEl.style.background = '#87CEEB';
    }
    
    // Add to page
    document.body.appendChild(messageEl);
    
    // Remove after 3 seconds
    setTimeout(() => {
        messageEl.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => messageEl.remove(), 300);
    }, 3000);
}

// Add CSS animations for messages
const toastStyle = document.createElement('style');
toastStyle.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(toastStyle);
