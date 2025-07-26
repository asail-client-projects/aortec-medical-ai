// MOBILE MENU TOGGLE FUNCTIONALITY
console.log('🚀 Header.js loaded successfully!');

document.addEventListener('DOMContentLoaded', function() {
    console.log('📱 DOM loaded, initializing mobile menu...');
    
    const menuToggle = document.querySelector('.menu-toggle');
    const mobileNav = document.querySelector('.mobile-nav');
    
    // Debug: Check if elements exist
    console.log('Menu toggle button:', menuToggle);
    console.log('Mobile nav:', mobileNav);
    
    if (!menuToggle) {
        console.error('❌ .menu-toggle not found! Check your header.html structure');
        return;
    }
    
    if (!mobileNav) {
        console.error('❌ .mobile-nav not found! Check your header.html structure');
        return;
    }
    
    console.log('✅ Both elements found successfully');
    
    let isMenuOpen = false;
    
    // Toggle function
    function toggleMenu() {
        isMenuOpen = !isMenuOpen;
        console.log('📱 Menu toggled. Open:', isMenuOpen);
        
        if (isMenuOpen) {
            menuToggle.classList.add('active');
            mobileNav.classList.add('active');
            mobileNav.style.display = 'block';
            document.body.style.overflow = 'hidden';
            console.log('🔓 Menu opened');
        } else {
            menuToggle.classList.remove('active');
            mobileNav.classList.remove('active');
            mobileNav.style.display = 'none';
            document.body.style.overflow = '';
            console.log('🔒 Menu closed');
        }
        
        menuToggle.setAttribute('aria-expanded', isMenuOpen);
    }
    
    // Main click event for hamburger button
    menuToggle.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log('🖱️ Hamburger button clicked!');
        toggleMenu();
    });
    
    // Close menu when clicking on mobile navigation links
    const mobileLinks = document.querySelectorAll('.mobile-nav a');
    console.log(`🔗 Found ${mobileLinks.length} mobile links`);
    
    mobileLinks.forEach((link, index) => {
        link.addEventListener('click', function() {
            console.log(`🔗 Mobile link ${index + 1} clicked, closing menu`);
            if (isMenuOpen) {
                toggleMenu();
            }
        });
    });
    
    // Close menu when clicking outside of menu area
    document.addEventListener('click', function(e) {
        if (isMenuOpen && !menuToggle.contains(e.target) && !mobileNav.contains(e.target)) {
            console.log('🌐 Clicked outside menu area, closing menu');
            toggleMenu();
        }
    });
    
    // Close menu when pressing Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && isMenuOpen) {
            console.log('⌨️ Escape key pressed, closing menu');
            toggleMenu();
        }
    });
    
    // Handle window resize - close menu if switching to desktop view
    window.addEventListener('resize', function() {
        const windowWidth = window.innerWidth;
        console.log(`📐 Window resized to: ${windowWidth}px`);
        
        if (windowWidth > 768 && isMenuOpen) {
            console.log('📱➡️💻 Switched to desktop view, closing mobile menu');
            toggleMenu();
        }
    });
    
    // Additional debugging: Log current window size
    console.log(`📐 Current window size: ${window.innerWidth}px`);
    console.log(`📱 Mobile menu should be ${window.innerWidth <= 768 ? 'visible' : 'hidden'}`);
    
    console.log('✅ Mobile menu initialization complete!');
});

// ACTIVE PAGE HIGHLIGHTING (Enhanced version)
function setActiveNav() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('nav ul li a, .mobile-nav ul li a');
    
    console.log(`🎯 Setting active navigation for path: ${currentPath}`);
    console.log(`🔗 Found ${navLinks.length} navigation links to process`);
    
    navLinks.forEach((link, index) => {
        link.classList.remove('active');
        const linkHref = link.getAttribute('href');
        
        if (linkHref === currentPath) {
            link.classList.add('active');
            console.log(`✅ Set link ${index + 1} as active: ${linkHref}`);
        }
    });
}

// Call the function when the page loads
window.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 Setting up active navigation highlighting...');
    setActiveNav();
});

// Additional debugging function you can call from console
window.debugMobileMenu = function() {
    console.log('🔍 MOBILE MENU DEBUG INFO:');
    console.log('Menu toggle:', document.querySelector('.menu-toggle'));
    console.log('Mobile nav:', document.querySelector('.mobile-nav'));
    console.log('Window width:', window.innerWidth);
    console.log('Mobile nav classes:', document.querySelector('.mobile-nav')?.className);
    console.log('Menu toggle classes:', document.querySelector('.menu-toggle')?.className);
};