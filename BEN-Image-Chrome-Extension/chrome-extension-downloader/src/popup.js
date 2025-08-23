const extractBtn = document.getElementById('extract-btn');
const statusDiv = document.getElementById('status');
const imageList = document.getElementById('image-list');

extractBtn.onclick = () => {
    statusDiv.textContent = "Extracting images...";
    imageList.innerHTML = "";

    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
        const tab = tabs[0];
        // Inject content.js first
        chrome.scripting.executeScript({
            target: {tabId: tab.id},
            files: ["src/content.js"]
        }, () => {
            // Now send the message
            chrome.tabs.sendMessage(tab.id, {action: "extractImages"}, (response) => {
                if (chrome.runtime.lastError || !response) {
                    statusDiv.textContent = "Failed to extract images.";
                    return;
                }
                const imageUrls = response.imageUrls;
                if (imageUrls.length === 0) {
                    statusDiv.textContent = "No image URLs found.";
                    return;
                }
                statusDiv.textContent = `Found ${imageUrls.length} images. Downloading...`;
                imageList.innerHTML = imageUrls.map(url => `<li><a href="${url}" target="_blank">${url}</a></li>`).join('');
                // Download each image
                imageUrls.forEach(url => {
                    chrome.downloads.download({
                        url: url,
                        filename: url.split('/').pop(),
                        conflictAction: 'uniquify'
                    });
                });
                statusDiv.textContent = "Download started for all images.";
            });
        });
    });
};