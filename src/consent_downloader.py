# Download logic for Consent Documents

from consent_selectors import DOWNLOAD_BUTTON, NEXT_BUTTON, LAST_BUTTON
import os
import asyncio
import yaml

def load_settings():
    """Load timeout from settings."""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'settings.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


async def download_consent_documents(page, download_dir, patient_id="233957", per_page=10):
    """
    Downloads consent form PDFs for a patient directly from the list page.
    Only downloads forms that have a download option available.
    
    Args:
        page: Playwright page object (already authenticated)
        download_dir: Directory to save downloads
        patient_id: Patient ID
        per_page: Number of items per page (for pagination testing)
    """
    settings = load_settings()
    page_timeout = settings.get('page_timeout', 60000)
    
    base_url = f"https://www.calystaproemr.com"
    list_page_url = f"https://www.calystaproemr.com/patients/list-consent-documents/{patient_id}?count={per_page}&page=1"
    current_page = 1
    total_downloaded = 0
    total_skipped = 0
    
    # Add dialog handler to auto-accept popups
    async def handle_dialog(dialog):
        # print(f"[CONSENT] Dialog appeared: {dialog.message}")
        await dialog.accept()
    page.on("dialog", handle_dialog)


    while True:
        url = list_page_url.replace("page=1", f"page={current_page}")
        print(f"[CONSENT] Navigating to list page {current_page}: {url}")
        await page.goto(url, timeout=page_timeout)
        await page.wait_for_load_state('networkidle')

        # Wait a bit for the page to fully render
        await asyncio.sleep(1)

        # Find all download buttons (icon elements) on the list page
        download_icons = await page.query_selector_all(DOWNLOAD_BUTTON)
        print(f"[CONSENT] Page {current_page}: Found {len(download_icons)} download button(s)")
        
        if len(download_icons) == 0:
            print(f"[CONSENT] No consent documents found for patient {patient_id}")
            break
        
        # Process each download button - click directly like encounter_downloader does
        for idx, icon in enumerate(download_icons):
            try:
                # Start download - click directly like encounter_downloader does
                async with page.expect_download() as download_info:
                    await icon.click()
                
                download = await download_info.value
                filename = download.suggested_filename
                save_path = os.path.join(download_dir, filename)
                
                # Handle duplicates
                base, ext = os.path.splitext(filename)
                counter = 2
                while os.path.exists(save_path):
                    save_path = os.path.join(download_dir, f"{base} ({counter}){ext}")
                    counter += 1
                
                await download.save_as(save_path)
                total_downloaded += 1
                print(f"[CONSENT] Downloaded: {filename} -> {save_path}")
                    
            except Exception as e:
                print(f"[CONSENT] Button {idx+1}: Error downloading: {e}")
                total_skipped += 1
            
            # Small delay between downloads
            await asyncio.sleep(0.5)

        # Check for next page
        next_btn = await page.query_selector(NEXT_BUTTON)
        last_btn = await page.query_selector(LAST_BUTTON)
        
        if not next_btn or not last_btn:
            print(f"[CONSENT] No pagination buttons found. Ending download.")
            break
        
        # If next is disabled or not visible, break
        if not await next_btn.is_visible():
            print(f"[CONSENT] Next button not visible. Ending download.")
            break
        
        current_page += 1
        await asyncio.sleep(0.5)  # Small delay for navigation
    
    print(f"[CONSENT] Total consent documents downloaded for patient {patient_id}: {total_downloaded}")
    print(f"[CONSENT] Total consent forms skipped (no download option): {total_skipped}")
    return total_downloaded
