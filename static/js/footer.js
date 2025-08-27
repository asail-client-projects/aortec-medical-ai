// JAVASCRIPT FOR DISCLAIMER BAR FUNCTIONALITY

function closeDiclaimerBar() {
  const disclaimerBar = document.querySelector('.medical-disclaimer-bar');
  if (disclaimerBar) {
    disclaimerBar.classList.add('hidden');          // slide it down (CSS handles transform)
    document.body.classList.add('disclaimer-closed'); // remove bottom padding
    sessionStorage.setItem('disclaimerClosed', 'true');
  }
}
// expose for inline onclick
window.closeDiclaimerBar = closeDiclaimerBar;

// Delegate click: works even if the button is re-rendered
document.addEventListener('click', (e) => {
  if (e.target.closest('.disclaimer-close')) {
    closeDiclaimerBar();
  }
});

// Show disclaimer bar on page load (unless user closed it in this tab)
document.addEventListener('DOMContentLoaded', function () {
  const disclaimerBar = document.querySelector('.medical-disclaimer-bar');
  const wasClosed = sessionStorage.getItem('disclaimerClosed');
  if (wasClosed === 'true' && disclaimerBar) {
    disclaimerBar.classList.add('hidden');
    document.body.classList.add('disclaimer-closed');
  }
});

// Optional: after 30s, just reduce opacity (do not auto-hide)
setTimeout(function () {
  if (sessionStorage.getItem('disclaimerClosed') !== 'true') {
    const disclaimerBar = document.querySelector('.medical-disclaimer-bar');
    if (disclaimerBar) disclaimerBar.style.opacity = '0.9';
  }
}, 30000);
