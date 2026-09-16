
from encounter_selectors import DOWNLOAD_BUTTON, NEXT_BUTTON, LAST_BUTTON
import os
import asyncio
import yaml

def load_settings():
    """Load timeout from settings."""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'settings.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

async def download_encounter_documents(page, download_dir, patient_id="233957", per_page=10):
    """
    Downloads all encounter PDFs for a patient, paginating as needed.
    Args:
        page: Playwright page object (already authenticated)
        download_dir: Directory to save downloads
        patient_id: Patient ID (hardcoded for now)
        per_page: Number of items per page (for pagination testing)
    """
    settings = load_settings()
    page_timeout = settings.get('page_timeout', 60000)
    
    base_url = f"https://www.calystaproemr.com/patient-encounters/encounter-history/{patient_id}/global_view?count={per_page}&page=1"
    current_page = 1
    while True:
        url = base_url.replace("page=1", f"page={current_page}")
        await page.goto(url, timeout=page_timeout)
        await page.wait_for_load_state('networkidle')

        # Find all download buttons
        download_links = await page.query_selector_all(DOWNLOAD_BUTTON)
        print(f"[DEBUG] Page {current_page}: Found {len(download_links)} download button(s)")
        for idx, link in enumerate(download_links):
            try:
                link_text = await link.inner_text()
            except Exception:
                link_text = "(no text)"
            try:
                href = await link.get_attribute('href')
            except Exception:
                href = None
            print(f"[DEBUG] Button {idx+1}: text='{link_text}', href='{href}'")
        for idx, link in enumerate(download_links):
            # Start download
            async with page.expect_download() as download_info:
                await link.click()
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
            # Optionally validate PDF here

        # Check for next page
        next_btn = await page.query_selector(NEXT_BUTTON)
        last_btn = await page.query_selector(LAST_BUTTON)
        if not next_btn or not last_btn:
            break  # No more pages
        # If next is disabled or not visible, break
        if not await next_btn.is_visible():
            break
        current_page += 1
        await asyncio.sleep(0.5)  # Small delay for navigation
