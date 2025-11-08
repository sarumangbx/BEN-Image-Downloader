import customtkinter as ctk
from tkinter import filedialog, messagebox, Scrollbar
import re
import requests
import os
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import unquote
import threading

# Initialize App with Light Theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("BEN Image Downloader")

# Get screen dimensions and set dynamic scaling
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()

app.geometry(f"{int(screen_width * 0.5)}x{int(screen_height * .85)}")  # Adjusted to 85% of screen height
app.resizable(False, False)  # Prevent resizing

def scale_ui(widget, width_ratio, height_ratio):
    widget.configure(width=int(screen_width * width_ratio), height=int(screen_height * height_ratio))

# Define UI Components Before Scaling
text_html = ctk.CTkTextbox(app, corner_radius=10)
text_urls = ctk.CTkTextbox(app, corner_radius=10)
entry_folder = ctk.CTkEntry(app)
text_status = ctk.CTkTextbox(app, corner_radius=10)

# Apply scaling to key elements
scale_ui(text_html, 0.9, 0.25)  # HTML text box
scale_ui(text_urls, 0.9, 0.25)  # URL list box
scale_ui(entry_folder, 0.4, 0.05)  # Folder selection entry
scale_ui(text_status, 0.9, 0.15)  # Status box


# Global Variables
urls_to_download = []
is_downloading = False
BATCH_SIZE = 5  # Number of concurrent downloads

def reset_ui():
    """Reset all fields except the destination folder."""
    text_html.delete("1.0", "end")
    text_urls.delete("1.0", "end")
    text_status.delete("1.0", "end")
    progress_bar.set(0)
    status_label.configure(text="Status: Waiting")

def extract_image_urls():
    """Extract image URLs from pasted HTML text, remove duplicates, and display count."""
    text_urls.delete("1.0", "end")
    global urls_to_download
    urls_to_download = []

    html_content = text_html.get("1.0", "end").strip()
    
    # Match both project_modules URLs and normal image URLs
    url_pattern = r'https?://[^\s\'"<>]+(?:\.(?:jpg|jpeg|png|gif|bmp|webp|svg))[^\s\'"<>]*'
    all_urls = re.findall(url_pattern, html_content, re.IGNORECASE)

    # Process URLs
    processed_urls = []
    for url in all_urls:
        # Clean the URL
        url = url.split('"')[0].split("'")[0]  # Remove any trailing quotes
        url = unquote(url)  # URL decode
        
        # Handle project_modules URLs
        if "project_modules" in url:
            url = re.sub(r"(project_modules/)[^/]+", r"\1source", url)
        
        processed_urls.append(url)

    # Remove duplicates while preserving order
    urls_to_download = list(dict.fromkeys(processed_urls))

    if urls_to_download:
        count_message = f"Total Unique Image Links: {len(urls_to_download)}\n"
        text_urls.insert("end", count_message + "\n".join(urls_to_download))
    else:
        text_urls.insert("end", "No image URLs found in the HTML text.")

def select_download_folder():
    """Choose folder for image downloads."""
    folder_path = filedialog.askdirectory()
    if folder_path:
        entry_folder.delete(0, "end")
        entry_folder.insert(0, folder_path)
        btn_download.configure(state="normal")

async def download_single_image(session, url, download_folder, semaphore, counter):
    """Download a single image using aiohttp."""
    async with semaphore:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    # Get folder name for the prefix
                    folder_name = os.path.basename(download_folder)
                    # Get file extension from URL
                    _, ext = os.path.splitext(unquote(url))
                    # Create filename with 3-digit counter
                    image_name = f"{folder_name}_{counter:03d}{ext}"
                    image_path = os.path.join(download_folder, image_name)

                    data = await response.read()
                    with open(image_path, mode='wb') as f:
                        f.write(data)
                    return True, url, None
                else:
                    return False, url, f"HTTP {response.status}"
        except Exception as e:
            return False, url, str(e)

async def download_images_async():
    """Download images asynchronously."""
    if not urls_to_download:
        messagebox.showerror("Error", "No valid image URLs to download!")
        return

    download_folder = entry_folder.get()
    os.makedirs(download_folder, exist_ok=True)

    progress_bar.set(0)
    status_label.configure(text="Downloading...")
    text_status.delete("1.0", "end")

    # Create a semaphore to limit concurrent downloads
    semaphore = asyncio.Semaphore(BATCH_SIZE)
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for index, url in enumerate(urls_to_download, start=1):
            task = asyncio.ensure_future(download_single_image(session, url, download_folder, semaphore, index))
            tasks.append(task)

        total = len(tasks)
        completed = 0

        for task in asyncio.as_completed(tasks):
            success, url, error = await task
            completed += 1
            progress = completed / total
            
            # Update UI
            app.after(0, progress_bar.set, progress)
            if success:
                app.after(0, lambda: text_status.insert("end", f"Successfully downloaded: {url}\n"))
            else:
                app.after(0, lambda: text_status.insert("end", f"Failed to download {url}: {error}\n"))
            
            app.after(0, text_status.see, "end")  # Auto-scroll to bottom

    status_label.configure(text="Download Complete!")
    messagebox.showinfo("Success", "Images downloaded successfully!")

def start_download():
    """Start the download process in a separate thread."""
    global is_downloading
    if is_downloading:
        return
    
    is_downloading = True
    btn_download.configure(state="disabled")

    def run_async_download():
        asyncio.run(download_images_async())
        global is_downloading
        is_downloading = False
        app.after(0, lambda: btn_download.configure(state="normal"))

    thread = threading.Thread(target=run_async_download)
    thread.daemon = True
    thread.start()

# UI Components
frame_top = ctk.CTkFrame(app, corner_radius=10)
frame_top.pack(pady=10)

btn_reset = ctk.CTkButton(frame_top, text="Clear & Reset", command=reset_ui)
btn_reset.pack(side="left", padx=5)

text_html = ctk.CTkTextbox(app, width=850, height=250, corner_radius=10)
text_html.pack(pady=10)

btn_extract = ctk.CTkButton(app, text="Extract Image URLs", command=extract_image_urls)
btn_extract.pack(pady=10)

# Scrollable Text Box for Image Links
frame_scroll = ctk.CTkFrame(app, corner_radius=10)
frame_scroll.pack(fill="both", expand=True, pady=10)

scrollbar = Scrollbar(frame_scroll)
scrollbar.pack(side="right", fill="y")

text_urls = ctk.CTkTextbox(frame_scroll, width=850, height=300, corner_radius=10)
text_urls.pack(fill="both", expand=True)
text_urls.configure(yscrollcommand=scrollbar.set)
scrollbar.config(command=text_urls.yview)

frame_folder = ctk.CTkFrame(app, corner_radius=10)
frame_folder.pack(pady=10)

entry_folder = ctk.CTkEntry(frame_folder, width=400)
entry_folder.pack(side="left", padx=5)

btn_select_folder = ctk.CTkButton(frame_folder, text="Download Destination", command=select_download_folder)
btn_select_folder.pack(side="left")

btn_download = ctk.CTkButton(app, text="Download Images", command=start_download, state="disabled")
btn_download.pack(pady=10)

frame_status = ctk.CTkFrame(app, corner_radius=10)
frame_status.pack(pady=10)

status_label = ctk.CTkLabel(frame_status, text="Status: Waiting", text_color="blue")
status_label.pack(side="left", padx=10)

progress_bar = ctk.CTkProgressBar(frame_status, width=300)
progress_bar.pack(side="left", padx=10)

text_status = ctk.CTkTextbox(app, width=850, height=100, corner_radius=10)
text_status.pack(pady=10)

# Run the application
app.mainloop()