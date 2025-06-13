// Function to set the active class dynamically
function setActiveNav() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('nav ul li a');
    
    navLinks.forEach(link => {
        // Remove 'active' class from all links
        link.classList.remove('active');
        // Check if the link's href matches the current page's path
        if (link.getAttribute('href') === currentPath) {
            // Add 'active' class to the matching link
            link.classList.add('active');
        }
    });
}

// Call the function when the page loads
window.addEventListener('DOMContentLoaded', setActiveNav);
