import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config
from core.field_matcher import SemanticFieldMatcher

class PlaywrightFormFiller:
    """Automated Web & Live Google Form Filling Driver using Playwright"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.matcher = SemanticFieldMatcher()

    def fill_form(
        self,
        form_target: str,
        user_profile: Dict[str, Dict[str, Any]],
        overrides: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Launches Playwright browser, parses target form fields (supports Google Forms & standard web forms),
        matches against user profile, auto-fills fields directly on the live webpage, and returns results.
        """
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return {
                "status": "ERROR",
                "message": "Playwright is not installed. Run `pip install playwright && playwright install`."
            }

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()

            # Format URL or local file path
            if Path(form_target).exists():
                url = Path(form_target).resolve().as_uri()
            else:
                url = form_target if form_target.startswith("http") else f"http://{form_target}"

            print(f"[PlaywrightFiller] Navigating to: {url}")
            page.goto(url)
            page.wait_for_load_state("networkidle", timeout=15000)

            is_google_form = "docs.google.com/forms" in url.lower()

            if is_google_form:
                # Extract Google Form fields via JS evaluate
                extracted_inputs = page.evaluate("""
                    () => {
                        const fields = [];
                        const items = document.querySelectorAll('div[role="listitem"]');
                        items.forEach((item, index) => {
                            const heading = item.querySelector('div[role="heading"]') || item.querySelector('.M7eMe') || item.querySelector('.geBpt');
                            const qText = heading ? heading.innerText.trim() : '';

                            const input = item.querySelector('input[type="text"], input[type="email"], input[type="date"], textarea');
                            if (input && qText) {
                                fields.push({
                                    field_id: input.getAttribute('name') || `gform_item_${index}`,
                                    label: qText,
                                    field_type: input.tagName.toLowerCase() === 'textarea' ? 'textarea' : (input.getAttribute('type') || 'text'),
                                    gform_index: index
                                });
                            }
                        });
                        return fields;
                    }
                """)
            else:
                # Extract standard HTML form fields
                extracted_inputs = page.evaluate("""
                    () => {
                        const fields = [];
                        const inputs = document.querySelectorAll('input, select, textarea');
                        inputs.forEach((el, index) => {
                            const type = el.getAttribute('type') || el.tagName.toLowerCase();
                            if (['submit', 'button', 'hidden', 'reset'].includes(type)) return;

                            let labelText = '';
                            if (el.id) {
                                const lbl = document.querySelector(`label[for="${el.id}"]`);
                                if (lbl) labelText = lbl.innerText.trim();
                            }
                            if (!labelText && el.closest('label')) {
                                labelText = el.closest('label').innerText.trim();
                            }
                            if (!labelText) {
                                labelText = el.getAttribute('placeholder') || el.getAttribute('name') || el.id || `Field ${index + 1}`;
                            }

                            fields.push({
                                field_id: el.id || el.getAttribute('name') || `input_${index}`,
                                label: labelText,
                                field_type: type,
                                selector: el.id ? `#${el.id}` : (el.getAttribute('name') ? `[name="${el.getAttribute('name')}"]` : null)
                            });
                        });
                        return fields;
                    }
                """)

            # Match extracted fields against user profile
            match_results = self.matcher.match_and_fill(extracted_inputs, user_profile)

            # Apply user manual overrides if provided
            if overrides:
                for res in match_results:
                    if res["field_id"] in overrides:
                        res["derived_value"] = overrides[res["field_id"]]
                        res["action"] = "MANUAL_OVERRIDE"

            # Execute Auto-fill action in browser
            filled_count = 0
            flagged_count = 0

            for match in match_results:
                value = match.get("derived_value")
                action = match.get("action")

                if action in ["AUTO_FILL", "INFERRED", "MANUAL_OVERRIDE"] and value is not None:
                    try:
                        if is_google_form:
                            g_idx = match.get("gform_index")
                            if g_idx is not None:
                                items = page.query_selector_all('div[role="listitem"]')
                                if g_idx < len(items):
                                    input_elem = items[g_idx].query_selector('input[type="text"], input[type="email"], input[type="date"], textarea')
                                    if input_elem:
                                        input_elem.fill(str(value))
                                        filled_count += 1
                        else:
                            selector = match.get("selector") or f"#{match['field_id']}"
                            element = page.query_selector(selector)
                            if element:
                                ftype = match.get("field_type", "text")
                                if ftype in ["select", "dropdown"]:
                                    page.select_option(selector, label=str(value))
                                elif ftype == "checkbox":
                                    if str(value).lower() in ["true", "yes", "1"]:
                                        page.check(selector)
                                else:
                                    page.fill(selector, str(value))
                                filled_count += 1
                    except Exception as e:
                        print(f"[PlaywrightFiller] Could not fill field {match.get('label')}: {e}")
                else:
                    flagged_count += 1

            # Give DOM a moment to reflect input values
            page.wait_for_timeout(1000)

            # Retrieve screenshot for verification
            screenshot_path = str(Path(config.BASE_DIR) / "filled_form_preview.png")
            page.screenshot(path=screenshot_path, full_page=True)

            browser.close()

            return {
                "status": "COMPLETED" if flagged_count == 0 else "REVIEW_NEEDED",
                "target_url": url,
                "is_google_form": is_google_form,
                "total_fields": len(extracted_inputs),
                "filled_count": filled_count,
                "flagged_count": flagged_count,
                "match_details": match_results,
                "screenshot_path": screenshot_path
            }
