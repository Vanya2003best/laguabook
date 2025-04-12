// app/static/js/main.js

/**
 * LinguaReader - Main JavaScript file
 * Handles global functionality across the app
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });

    // Handle dark mode toggle
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
            const isDarkMode = document.body.classList.contains('dark-mode');
            localStorage.setItem('darkMode', isDarkMode ? 'enabled' : 'disabled');

            // Update icon
            const icon = darkModeToggle.querySelector('i');
            if (isDarkMode) {
                icon.classList.remove('fa-moon');
                icon.classList.add('fa-sun');
            } else {
                icon.classList.remove('fa-sun');
                icon.classList.add('fa-moon');
            }
        });

        // Check for saved dark mode preference
        const savedDarkMode = localStorage.getItem('darkMode');
        if (savedDarkMode === 'enabled') {
            document.body.classList.add('dark-mode');
            const icon = darkModeToggle.querySelector('i');
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
        }
    }

    // Global search functionality
    const globalSearch = document.getElementById('globalSearch');
    if (globalSearch) {
        globalSearch.addEventListener('input', debounce(function() {
            const query = this.value.trim();

            if (query.length < 2) {
                document.getElementById('searchResults').innerHTML = '';
                document.getElementById('searchDropdown').classList.remove('show');
                return;
            }

            fetch(`/api/search?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    const resultsContainer = document.getElementById('searchResults');
                    resultsContainer.innerHTML = '';

                    // Check if we have any results
                    const hasBooks = data.books && data.books.length > 0;
                    const hasVocabulary = data.vocabulary && data.vocabulary.length > 0;

                    if (!hasBooks && !hasVocabulary) {
                        resultsContainer.innerHTML = `
                            <div class="dropdown-item disabled">No results found</div>
                        `;
                        return;
                    }

                    // Display book results
                    if (hasBooks) {
                        resultsContainer.innerHTML += `
                            <h6 class="dropdown-header">Books</h6>
                        `;

                        data.books.forEach(book => {
                            resultsContainer.innerHTML += `
                                <a class="dropdown-item" href="/book/${book.id}">
                                    <i class="fas fa-book me-2"></i> ${book.title}
                                    <small class="text-muted d-block">${book.author || 'Unknown author'}</small>
                                </a>
                            `;
                        });
                    }

                    // Display vocabulary results
                    if (hasVocabulary) {
                        resultsContainer.innerHTML += `
                            <h6 class="dropdown-header">Vocabulary</h6>
                        `;

                        data.vocabulary.forEach(item => {
                            resultsContainer.innerHTML += `
                                <a class="dropdown-item" href="/vocabulary#word-${item.id}">
                                    <i class="fas fa-language me-2"></i> ${item.word}
                                    <small class="text-muted d-block">${item.context || ''}</small>
                                </a>
                            `;
                        });
                    }

                    // Show the dropdown
                    document.getElementById('searchDropdown').classList.add('show');
                })
                .catch(error => {
                    console.error('Error fetching search results:', error);
                });
        }, 300));
    }

    // Close search dropdown when clicking outside
    document.addEventListener('click', function(e) {
        const searchDropdown = document.getElementById('searchDropdown');
        const globalSearch = document.getElementById('globalSearch');

        if (searchDropdown && globalSearch) {
            if (!globalSearch.contains(e.target) && !searchDropdown.contains(e.target)) {
                searchDropdown.classList.remove('show');
            }
        }
    });

    // Toast notification system
    window.showToast = function(message, type = 'success', duration = 5000) {
        // Create toast container if it doesn't exist
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container';
            document.body.appendChild(toastContainer);
        }

        // Create toast element
        const toastId = 'toast-' + Date.now();
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type}`;
        toast.id = toastId;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        toastContainer.appendChild(toast);

        // Initialize and show the toast
        const toastInstance = new bootstrap.Toast(toast, {
            delay: duration
        });
        toastInstance.show();

        // Remove from DOM after hidden
        toast.addEventListener('hidden.bs.toast', function() {
            this.remove();
        });
    };
});

// Debounce function to limit how often a function is called
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

// Function to confirm dangerous actions
function confirmAction(message) {
    return confirm(message);
}

// Stats page chart initialization
function initCharts() {
    if (typeof Chart === 'undefined') return;

    // Reading Time Chart
    const readingTimeCtx = document.getElementById('readingTimeChart');
    if (readingTimeCtx) {
        fetch('/api/stats/reading-time')
            .then(response => response.json())
            .then(data => {
                new Chart(readingTimeCtx, {
                    type: 'line',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: 'Reading Time (minutes)',
                            data: data.values,
                            backgroundColor: 'rgba(67, 97, 238, 0.2)',
                            borderColor: 'rgba(67, 97, 238, 1)',
                            borderWidth: 2,
                            tension: 0.3
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            });
    }

    // Words Looked Up Chart
    const wordsLookedUpCtx = document.getElementById('wordsLookedUpChart');
    if (wordsLookedUpCtx) {
        fetch('/api/stats/words-looked-up')
            .then(response => response.json())
            .then(data => {
                new Chart(wordsLookedUpCtx, {
                    type: 'bar',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: 'Words Looked Up',
                            data: data.values,
                            backgroundColor: 'rgba(72, 149, 239, 0.7)'
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            });
    }

    // Proficiency Distribution Chart
    const proficiencyCtx = document.getElementById('proficiencyChart');
    if (proficiencyCtx) {
        fetch('/api/stats/proficiency')
            .then(response => response.json())
            .then(data => {
                new Chart(proficiencyCtx, {
                    type: 'doughnut',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            data: data.values,
                            backgroundColor: [
                                '#ff6384', '#36a2eb', '#cc65fe', '#ffce56', '#4bc0c0', '#9966ff'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'right'
                            }
                        }
                    }
                });
            });
    }
}