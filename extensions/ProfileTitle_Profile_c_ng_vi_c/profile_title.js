(function(){
  const profileName = "Profile c\u00f4ng vi\u1ec7c";
  const prefix = '[' + profileName + '] ';
  
  // Function to update title
  const updateTitle = () => {
    try {
      const currentTitle = document.title || '';
      if (!currentTitle.startsWith(prefix)) {
        document.title = prefix + currentTitle;
      }
    } catch(e) {}
  };
  
  // Function to update Google search bar
  const updateGoogleSearch = () => {
    try {
      // Find Google search input
      const searchInput = document.querySelector('input[name="q"], input[aria-label*="Search"], input[placeholder*="Search"]');
      if (searchInput && searchInput.placeholder) {
        const originalPlaceholder = searchInput.placeholder;
        if (!originalPlaceholder.includes(profileName)) {
          searchInput.placeholder = profileName + ' | ' + originalPlaceholder;
        }
      }
    } catch(e) {}
  };
  
  // Function to add profile indicator to page
  const addProfileIndicator = () => {
    try {
      // Remove existing indicator
      const existing = document.getElementById('gpm-profile-indicator');
      if (existing) existing.remove();
      
      // Create new indicator
      const indicator = document.createElement('div');
      indicator.id = 'gpm-profile-indicator';
      indicator.style.cssText = 'position:fixed;top:20px;right:20px;background:linear-gradient(45deg, #4285f4, #34a853);color:white;padding:8px 15px;border-radius:8px;font-family:Arial,sans-serif;font-size:14px;font-weight:bold;z-index:999999;box-shadow:0 4px 12px rgba(0,0,0,0.3);border:2px solid #fff;';
      indicator.textContent = '🔧 ' + profileName;
      document.body.appendChild(indicator);
      
      // Add animation
      indicator.style.animation = 'slideIn 0.5s ease-out';
      const style = document.createElement('style');
      style.textContent = '@keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }';
      document.head.appendChild(style);
    } catch(e) {}
  };
  
  // Function to update page content
  const updatePageContent = () => {
    updateTitle();
    updateGoogleSearch();
    addProfileIndicator();
  };
  
  // Initial setup
  updatePageContent();
  
  // Wait for page load then update
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      setTimeout(updatePageContent, 500);
      setTimeout(updatePageContent, 2000);
    });
  } else {
    setTimeout(updatePageContent, 500);
    setTimeout(updatePageContent, 2000);
  }
  
  // Monitor all changes
  const observer = new MutationObserver(() => {
    setTimeout(updatePageContent, 100);
  });
  
  try {
    observer.observe(document.documentElement, {childList:true, subtree:true, characterData:true});
  } catch(e) {}
  
  // Also monitor window events
  window.addEventListener('load', () => {
    setTimeout(updatePageContent, 1000);
  });
  
  // Periodic update every 5 seconds
  setInterval(updatePageContent, 5000);
})();
