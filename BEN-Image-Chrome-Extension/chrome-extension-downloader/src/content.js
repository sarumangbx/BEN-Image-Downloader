chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "extractImages") {
        // Get the full HTML of the page
        const html = document.documentElement.outerHTML;

        // Regex to find all URLs
        const urlPattern = /https?:\/\/[^\s"'>]+/g;
        const allUrls = html.match(urlPattern) || [];

        // Filter URLs that contain 'project_modules' and end with image extensions
        const imageExtensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"];
        const urlsFiltered = allUrls
            .filter(url => url.includes("project_modules") && imageExtensions.some(ext => url.toLowerCase().endsWith(ext)))
            .map(url => url.replace(/(project_modules\/)[^/]+/, "$1source"));

        // Remove duplicates
        const uniqueUrls = [...new Set(urlsFiltered)];

        sendResponse({ imageUrls: uniqueUrls });
        return true; // Async response
    }
});