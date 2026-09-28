# Handles login, facility selection, and session management


import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from login_selectors import USERNAME_FIELD, PASSWORD_FIELD, LOGIN_BUTTON, ERROR_MESSAGE

async def authenticate_and_select_facility(credentials, settings):
    """
    Authenticates to the EMR system and selects the facility.
    Returns: playwright browser, context, and page objects after successful login and facility selection.
    """
    base_url = settings.get('base_url', 'https://www.calystaproemr.com')
    browser_mode = settings.get('browser_mode', 'headless')
    page_timeout = int(settings.get('page_timeout', 30000))

    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=(browser_mode == 'headless'))
    viewport = settings.get('viewport', {"width": 1280, "height": 720})
    context = await browser.new_context(viewport=viewport)
    page = await context.new_page()

    # One shared dialog handler for the whole session.
    # Downloaders must NOT register additional handlers — that causes
    # "Cannot accept dialog which is already handled" races.
    async def _auto_accept_dialog(dialog):
        try:
            await dialog.accept()
        except Exception:
            pass  # already handled by another accept path

    page.on("dialog", _auto_accept_dialog)

    # Go to login page
    login_url = base_url
    await page.goto(login_url, timeout=page_timeout)


    # Fill username and password using Playwright codegen selectors
    await page.wait_for_selector(USERNAME_FIELD, timeout=page_timeout)
    await page.fill(USERNAME_FIELD, credentials['username'])
    await page.fill(PASSWORD_FIELD, credentials['password'])
    await page.click(LOGIN_BUTTON)
    # Wait for post-login UI (avoid networkidle — portals often keep polling)
    try:
        await page.wait_for_selector('#global-facility, .page-wrapper, .dashboard', timeout=page_timeout)
    except PlaywrightTimeoutError:
        try:
            await page.wait_for_load_state('domcontentloaded', timeout=5000)
        except PlaywrightTimeoutError:
            pass
    # Check login success
    url = page.url
    if not (any(x in url for x in ['/dashboard', '/main', '/home']) or not url.endswith('/login')):
        # Check for error message
        error_text = ''
        try:
            error_elem = await page.query_selector(ERROR_MESSAGE)
            if error_elem:
                error_text = await error_elem.inner_text()
        except Exception:
            pass
        await browser.close()
        raise Exception(f"Login failed. {error_text}")

    # Facility selection (if required)
    facility = credentials.get('facility')
    if facility:
        try:
            await page.wait_for_selector('#global-facility', timeout=page_timeout)
            select_el = await page.query_selector('#global-facility')
            found = False
            labels_seen = []
            target = _norm_facility(facility)
            tokens = [t for t in target.replace('-', ' ').split() if len(t) > 1]

            # Dropdown options sometimes populate after the select appears
            for attempt in range(8):
                options = await select_el.query_selector_all('option')
                labels_seen = []
                for option in options:
                    value = (await option.get_attribute('value') or '').strip()
                    title = (await option.get_attribute('title') or '').strip()
                    text = (await option.inner_text() or '').strip()
                    label = title or text
                    if label:
                        labels_seen.append(label)
                    label_n = _norm_facility(label)
                    text_n = _norm_facility(text)
                    # Exact / substring either way
                    if (
                        target == label_n
                        or target == text_n
                        or target in label_n
                        or target in text_n
                        or label_n in target
                    ):
                        await select_el.select_option(value=value)
                        found = True
                        break
                    # Token match: all significant words present (handles dash/space variants)
                    if tokens and all(t in label_n or t in text_n for t in tokens):
                        await select_el.select_option(value=value)
                        found = True
                        break
                if found:
                    break
                # Prefer waiting when select only has placeholder / empty options
                await asyncio.sleep(1.0)

            if not found:
                try:
                    await select_el.select_option(value=facility)
                    found = True
                except Exception:
                    pass
            if not found:
                sample = ', '.join(labels_seen[:12]) or '(no options)'
                raise Exception(
                    f"Facility '{facility}' not found in global-facility select. "
                    f"Available: {sample}"
                )
            await asyncio.sleep(0.5)
        except Exception as e:
            raise Exception(f"Error selecting facility '{facility}': {e}")

    return playwright, browser, context, page


def _norm_facility(s: str) -> str:
    """Normalize facility labels for fuzzy compare (spaces/dashes/case)."""
    out = []
    prev_space = False
    for ch in (s or '').lower().replace('_', ' '):
        if ch in '-–—':
            ch = ' '
        if ch.isspace():
            if not prev_space:
                out.append(' ')
            prev_space = True
        else:
            out.append(ch)
            prev_space = False
    return ''.join(out).strip()
