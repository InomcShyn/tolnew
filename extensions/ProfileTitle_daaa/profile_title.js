(function(){
  const profileName = "daaa";
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
  
  // Function to update address bar (if possible)
  const updateAddressBar = () => {
    try {
      // Try to find address bar and add profile indicator
      const addressBar = document.querySelector('input[type="search"], input[type="text"][name="q"], #searchboxinput, [data-ved]');
      if (addressBar && addressBar.placeholder && !addressBar.value.includes('[')) {
        addressBar.placeholder = profileName + ' | ' + (addressBar.placeholder || 'Tìm kiếm');
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
      indicator.style.cssText = 'position:fixed;top:10px;right:10px;background:rgba(0,0,0,0.8);color:white;padding:5px 10px;border-radius:5px;font-family:Arial;font-size:12px;z-index:9999;border:2px solid #4285f4;';
      indicator.textContent = 'Profile: ' + profileName;
      document.body.appendChild(indicator);
    } catch(e) {}
  };
  
  // Initial setup
  updateTitle();
  updateAddressBar();
  
  // Wait for page load then add indicator
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      setTimeout(addProfileIndicator, 1000);
    });
  } else {
    setTimeout(addProfileIndicator, 1000);
  }
  
  // Monitor title changes
  const titleObserver = new MutationObserver(updateTitle);
  try {
    const titleElement = document.querySelector('title');
    if (titleElement) {
      titleObserver.observe(titleElement, {childList:true, characterData:true, subtree:true});
    } else {
      titleObserver.observe(document.documentElement, {childList:true, characterData:true, subtree:true});
    }
  } catch(e) {}
  
  // Monitor address bar changes
  const addressObserver = new MutationObserver(updateAddressBar);
  try {
    addressObserver.observe(document.body, {childList:true, subtree:true});
  } catch(e) {}
})();
