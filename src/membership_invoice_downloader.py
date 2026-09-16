# Download logic for Membership Invoices

import os
import asyncio
from membership_invoice_selectors import VIEW_BUTTON_BY_PARENT, DOWNLOAD_BUTTON, NEXT_BUTTON, LAST_BUTTON


async def download_membership_invoices(page, download_dir, patient_id="156640", per_page=10):
    """
    Downloads all membership invoices for a patient by:
    1. Visiting the membership invoice list page
    2. Clicking each view button to open the membership invoice detail
    3. Clicking the download PDF button on each invoice
    
    Args:
        page: Playwright page object (already authenticated)
        download_dir: Directory to save downloads
        patient_id: Patient ID
        per_page: Number of items per page (for pagination testing)
    """
    base_url = f"https://www.calystaproemr.com"
    list_page_url = f"https://www.calystaproemr.com/patient-services-invoices/membership-invoices/{patient_id}?count={per_page}&page=1"
    current_page = 1
    total_downloaded = 0
    total_skipped = 0
    
    # Add dialog handler to auto-accept popups
    async def handle_dialog(dialog):
        await dialog.accept()
    page.on("dialog", handle_dialog)

    while True:
        url = list_page_url.replace("page=1", f"page={current_page}")
        print(f"[MEMBERSHIP] Navigating to list page {current_page}: {url}")
        await page.goto(url)
        await page.wait_for_load_state('networkidle')
        
        # Wait a bit for the page to fully render
        await asyncio.sleep(1)

        # Find all view buttons on the list page
        view_buttons = await page.query_selector_all(VIEW_BUTTON_BY_PARENT)
        print(f"[MEMBERSHIP] Page {current_page}: Found {len(view_buttons)} membership invoice(s)")
        
        if len(view_buttons) == 0:
            print(f"[MEMBERSHIP] No membership invoices found for patient {patient_id}")
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
        
        print(f"[MEMBERSHIP] Found {len(invoice_urls)} membership invoice URLs to process")
        
        # Now process each membership invoice URL
        for idx, invoice_url in enumerate(invoice_urls):
            try:
                print(f"[MEMBERSHIP] Opening membership invoice {idx+1}/{len(invoice_urls)}: {invoice_url}")
                
                # Navigate to the membership invoice detail page
                await page.goto(invoice_url)
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(1)
                
                # Find and click the download PDF button
                download_btn = await page.query_selector(DOWNLOAD_BUTTON)
                if not download_btn:
                    print(f"[MEMBERSHIP] Invoice {idx+1}: No download button found, skipping")
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
                print(f"[MEMBERSHIP] Downloaded: {filename}")
                total_downloaded += 1
                
                # Go back to list page
                await page.goto(url)
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"[MEMBERSHIP] Error processing membership invoice {idx+1}: {e}")
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
            print(f"[MEMBERSHIP] No pagination buttons found. Ending download.")
            break
        
        # If next is disabled or not visible, break
        if not await next_btn.is_visible():
            print(f"[MEMBERSHIP] Next button not visible. Ending download.")
            break
        
        current_page += 1
        await asyncio.sleep(0.5)  # Small delay for navigation
    
    print(f"[MEMBERSHIP] Total membership invoices downloaded for patient {patient_id}: {total_downloaded}")
    print(f"[MEMBERSHIP] Total membership invoices skipped: {total_skipped}")
    return total_downloaded