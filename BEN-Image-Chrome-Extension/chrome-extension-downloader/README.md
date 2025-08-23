# Chrome Extension Downloader

This project is a Chrome extension designed to fetch the source code of a website and facilitate the downloading of files from that source. Below are the details on how to install and use the extension.

## Features

- Fetches the source code of the currently active tab.
- Allows users to download files directly from the fetched source code.
- User-friendly popup interface for easy interaction.

## Installation

1. Clone the repository to your local machine:
   ```
   git clone <repository-url>
   ```

2. Navigate to the project directory:
   ```
   cd chrome-extension-downloader
   ```

3. Open Google Chrome and go to `chrome://extensions/`.

4. Enable "Developer mode" by toggling the switch in the top right corner.

5. Click on "Load unpacked" and select the `chrome-extension-downloader` directory.

## Usage

1. Click on the extension icon in the Chrome toolbar to open the popup interface.

2. Click the "Fetch Source Code" button to retrieve the source code of the current tab.

3. Use the provided options to select and download files from the fetched source code.

## Files Overview

- **src/background.js**: Background script that listens for events and manages fetching the source code.
- **src/content.js**: Content script that interacts with the web page and handles file downloads.
- **src/popup.js**: Logic for the popup interface, managing user interactions.
- **src/popup.html**: HTML structure for the popup interface.
- **src/styles/popup.css**: CSS styles for the popup interface.
- **manifest.json**: Configuration file for the Chrome extension.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.