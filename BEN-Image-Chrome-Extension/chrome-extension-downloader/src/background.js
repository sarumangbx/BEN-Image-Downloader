chrome.action.onClicked.addListener((tab) => {
    // Inject content.js into the current tab
    chrome.scripting.executeScript({
        target: {tabId: tab.id},
        files: ["src/content.js"]
    }, () => {
        // Send message to content.js to extract images
        chrome.tabs.sendMessage(tab.id, {action: "extractImages"}, (response) => {
            if (chrome.runtime.lastError || !response) {
                chrome.notifications.create({
                    type: "basic",
                    iconUrl: "icons/icon48.png",
                    title: "BEN Image Downloader",
                    message: "Failed to extract images."
                });
                return;
            }
            const imageUrls = response.imageUrls;
            if (imageUrls.length === 0) {
                chrome.notifications.create({
                    type: "basic",
                    iconUrl: "icons/icon48.png",
                    title: "BEN Image Downloader",
                    message: "No image URLs found."
                });
                return;
            }
            // Download each image
            imageUrls.forEach(url => {
                chrome.downloads.download({
                    url: url,
                    filename: url.split('/').pop(),
                    conflictAction: 'uniquify'
                });
            });
            chrome.notifications.create({
                type: "basic",
                iconUrl: "icons/icon48.png",
                title: "BEN Image Downloader",
                message: `Started downloading ${imageUrls.length} images.`
            });
        });
    });
});