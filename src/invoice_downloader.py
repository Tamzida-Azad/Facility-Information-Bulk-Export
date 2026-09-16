# Download logic for Invoice Documents

import os
import asyncio
import yaml
from invoice_selectors import VIEW_BUTTON, VIEW_BUTTON_BY_HREF, DOWNLOAD_BUTTON, NEXT_BUTTON, LAST_BUTTON

def load_settings():
    """Load timeout from settings."""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'settings.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


async def download_invoice_documents(page, download_dir, patient_id="233957", per_page=10):
    """
    Downloads all invoice PDFs for a patient by:
    1. Visiting the invoice list page
    2. Clicking each view button to open the invoice detail
    3. Clicking the download PDF button on each invoice
    
    Args:
        page: Playwright page object (already authenticated)
        download_dir: Directory to save downloads
        patient_id: Patient ID
        per_page: Number of items per page (for pagination testing)
    """
    settings = load_settings()
    page_timeout = settings.get('page_timeout', 60000)
    
    base_url = f"https://www.calystaproemr.com"
    list_page_url = f"https://www.calystaproemr.com/patient-services-invoices/all-invoices/{patient_id}?count={per_page}&page=1"
    current_page = 1
    total_downloaded = 0
    total_skipped = 0
    
    # Add dialog handler to auto-accept popups
    async def handle_dialog(dialog):
        try:
            await dialog.accept()
        except Exception as e:
            print(f"[INVOICE] Dialog handling error (safe to ignore): {e}")
    page.on("dialog", handle_dialog)

    while True:
        url = list_page_url.replace("page=1", f"page={current_page}")
        print(f"[INVOICE] Navigating to list page {current_page}: {url}")
        await page.goto(url, timeout=page_timeout)
        await page.wait_for_load_state('networkidle')
        
        # Wait a bit for the page to fully render
        await asyncio.sleep(1)

        # Find all view buttons on the list page
        view_buttons = await page.query_selector_all(VIEW_BUTTON_BY_HREF)
        print(f"[INVOICE] Page {current_page}: Found {len(view_buttons)} invoice(s)")
        
        if len(view_buttons) == 0:
            print(f"[INVOICE] No invoices found for patient {patient_id}")
            break
        
        # Extract ALL hrefs FIRST before any navigation - this avoids element handle issues
        invoice_urls = []
        for view_btn in view_buttons:
            try:
                href = await view_btn.get_attribute('href')
                if href:
                    invoice_urls.append(base_url + href)
            except Exception:
                pass
        
        print(f"[INVOICE] Found {len(invoice_urls)} invoice URLs to process")
        
        # Now process each invoice URL
        for idx, invoice_url in enumerate(invoice_urls):
            try:
                print(f"[INVOICE] Opening invoice {idx+1}/{len(invoice_urls)}: {invoice_url}")
                
                # Navigate to the invoice detail page
                await page.goto(invoice_url)
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(1)
                
                # Find and click the download PDF button
                download_btn = await page.query_selector(DOWNLOAD_BUTTON)
                if not download_btn:
                    print(f"[INVOICE] Invoice {idx+1}: No download button found, skipping")
                    total_skipped += 1
                    # Go back to list page
                    await page.goto(url)
                    await page.wait_for_load_state('networkidle')
                    await asyncio.sleep(0.5)
                    continue
                
                # Start download
                async with page.expect_download() as download_info:
                    await download_btn.click()
                
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
                print(f"[INVOICE] Downloaded: {filename}")
                total_downloaded += 1
                
                # Go back to list page
                await page.goto(url)
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"[INVOICE] Error processing invoice {idx+1}: {e}")
                total_skipped += 1
                # Try to go back to list page
                try:
                    await page.goto(url)
                    await page.wait_for_load_state('networkidle')
                except Exception:
                    pass
            
            # Small delay between invoices
            await asyncio.sleep(0.5)

        # Check for next page
        next_btn = await page.query_selector(NEXT_BUTTON)
        last_btn = await page.query_selector(LAST_BUTTON)
        
        if not next_btn or not last_btn:
            print(f"[INVOICE] No pagination buttons found. Ending download.")
            break
        
        # If next is disabled or not visible, break
        if not await next_btn.is_visible():
            print(f"[INVOICE] Next button not visible. Ending download.")
            break
        
        current_page += 1
        await asyncio.sleep(0.5)  # Small delay for navigation
    
    print(f"[INVOICE] Total invoices downloaded for patient {patient_id}: {total_downloaded}")
    print(f"[INVOICE] Total invoices skipped: {total_skipped}")
    return total_downloaded
