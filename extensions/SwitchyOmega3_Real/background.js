
// SwitchyOmega 3 Background Script
chrome.runtime.onInstalled.addListener((details) => {
    console.log('SwitchyOmega 3 extension installed:', details.reason);
    
    // Initialize default settings
    chrome.storage.local.set({
        'switchyomega_profiles': {},
        'switchyomega_current_profile': 'direct',
        'switchyomega_options': {
            'auto_switch': false,
            'quick_switch': true
        }
    });
});

// Handle proxy changes
chrome.proxy.onProxyError.addListener((details) => {
    console.log('Proxy error:', details);
});

// Handle extension icon click
chrome.action.onClicked.addListener((tab) => {
    // Open options page
    chrome.tabs.create({ url: chrome.runtime.getURL('options.html') });
});

// Handle context menu
chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === 'switchyomega_quick_switch') {
        // Quick switch functionality
        console.log('Quick switch clicked');
    }
});

// Create context menu
chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: 'switchyomega_quick_switch',
        title: 'SwitchyOmega: Quick Switch',
        contexts: ['page']
    });
});
