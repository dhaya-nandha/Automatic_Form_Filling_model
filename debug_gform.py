from playwright.sync_api import sync_playwright

def inspect_gform():
    url = "https://docs.google.com/forms/d/e/1FAIpQLSeuoP6EKvaRjYLa0rWlGFlsZpOwKJNVufoNg4oy7o5sdnswMw/viewform"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_load_state("networkidle")

        items = page.query_selector_all('div[role="listitem"]')
        print(f"Discovered {len(items)} questions in Google Form:")

        for idx, item in enumerate(items):
            text = item.inner_text().split("\n")
            q_title = text[0] if text else "Unknown"
            inputs = item.query_selector_all('input[type="text"], input[type="email"], textarea')
            print(f"  Q{idx+1}: '{q_title}' | Found {len(inputs)} text inputs")

        browser.close()

if __name__ == "__main__":
    inspect_gform()
