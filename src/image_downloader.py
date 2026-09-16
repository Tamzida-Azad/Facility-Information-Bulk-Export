# Download logic for Patient Images

import os
import asyncio
import yaml
from image_selectors import DOWNLOAD_BUTTON, NEXT_BUTTON, LAST_BUTTON

def load_settings():
    """Load timeout from settings."""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'settings.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


async def download_patient_images(page, download_dir, patient_id="233957", per_page=10, patient_name=None):
    """
    Downloads all patient images from the images list page.
    
    Args:
        page: Playwright page object (already authenticated)
        download_dir: Directory to save downloads
        patient_id: Patient ID
        per_page: Number of items per page (for pagination testing)
        patient_name: Patient name for filename preview (optional)
    """
    settings = load_settings()
    page_timeout = settings.get('page_timeout', 60000)
    
    base_url = f"https://www.calystaproemr.com"
    list_page_url = f"https://www.calystaproemr.com/patient-images/index/{patient_id}?count={per_page}&page=1"
    current_page = 1
    total_downloaded = 0
    total_skipped = 0
    
    # Add dialog handler to auto-accept popups
    async def handle_dialog(dialog):
        try:
            await dialog.accept()
        except Exception:
            pass  # Dialog already handled
    page.on("dialog", handle_dialog)

    while True:
        url = list_page_url.replace("page=1", f"page={current_page}")
        print(f"[IMAGES] Navigating to list page {current_page}: {url}")
        
        try:
            await page.goto(url, timeout=page_timeout)
            await page.wait_for_load_state('networkidle', timeout=page_timeout)
        except Exception as e:
            print(f"[IMAGES] Error navigating to page {current_page}: {e}")
            break
        
        # Wait a bit for the page to fully render
        await asyncio.sleep(1)

        # Find all download buttons on the list page
        try:
            download_buttons = await page.query_selector_all(DOWNLOAD_BUTTON)
            print(f"[IMAGES] Page {current_page}: Found {len(download_buttons)} download button(s)")
        except Exception as e:
            print(f"[IMAGES] Error finding download buttons: {e}")
            break
        
        if len(download_buttons) == 0:
            print(f"[IMAGES] No images found for patient {patient_id}")
            break
        
        # Process each download button
        for idx, btn in enumerate(download_buttons):
            try:
                # Start download - click directly
                async with page.expect_download() as download_info:
                    await btn.click()
                
                download = await download_info.value
                original_filename = download.suggested_filename
                save_path = os.path.join(download_dir, original_filename)
                
                # Show filename transformation preview
                if patient_name:
                    from datetime import datetime
                    date_str = datetime.now().strftime('%m-%d-%Y')
                    base_name = os.path.splitext(original_filename)[0]
                    extension = os.path.splitext(original_filename)[1]
                    
                    # Preview what the renamed file will look like
                    future_filename = f"{base_name}_{patient_name}_{date_str}{extension}"
                    print(f"[IMAGES] Original: {original_filename} → Will rename to: {future_filename}")
                else:
                    print(f"[IMAGES] Downloaded: {original_filename} (will be renamed later)")
                
                # Handle duplicates
                base, ext = os.path.splitext(original_filename)
                counter = 2
                while os.path.exists(save_path):
                    save_path = os.path.join(download_dir, f"{base} ({counter}){ext}")
                    counter += 1
                
                await download.save_as(save_path)
                total_downloaded += 1
                
            except Exception as e:
                print(f"[IMAGES] Error downloading image {idx+1}: {e}")
                total_skipped += 1
            
            # Small delay between downloads
            await asyncio.sleep(0.5)

        # Check for next page
        try:
            next_btn = await page.query_selector(NEXT_BUTTON)
            last_btn = await page.query_selector(LAST_BUTTON)
            
            if not next_btn or not last_btn:
                print(f"[IMAGES] No pagination buttons found. Ending download.")
                break
            
            # If next is disabled or not visible, break
            if not await next_btn.is_visible():
                print(f"[IMAGES] Next button not visible. Ending download.")
                break
            
            current_page += 1
            await asyncio.sleep(0.5)  # Small delay for navigation
        except Exception as e:
            print(f"[IMAGES] Error checking pagination: {e}")
            break
    
    print(f"[IMAGES] Total images downloaded for patient {patient_id}: {total_downloaded}")
    print(f"[IMAGES] Total images skipped: {total_skipped}")
    return total_downloaded