from typing import List, Dict, Any
import re

class HTMLFormParser:
    """Parses HTML DOM elements & Google Forms to extract input fields, labels, placeholders, and selectors"""

    @staticmethod
    def parse_html_string(html_content: str) -> List[Dict[str, Any]]:
        fields = []
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, "html.parser")

            # 1. Parse standard HTML form elements
            for elem in soup.find_all(["input", "select", "textarea"]):
                field_type = elem.get("type", elem.name).lower()
                if field_type in ["submit", "button", "hidden", "reset"]:
                    continue

                field_id = elem.get("id") or elem.get("name") or f"field_{len(fields)+1}"
                placeholder = elem.get("placeholder", "")

                label_text = ""
                if elem.get("id"):
                    label_tag = soup.find("label", {"for": elem.get("id")})
                    if label_tag:
                        label_text = label_tag.get_text(strip=True)

                if not label_text and elem.parent and elem.parent.name == "label":
                    label_text = elem.parent.get_text(strip=True)

                if not label_text:
                    label_text = placeholder or elem.get("name") or field_id

                fields.append({
                    "field_id": field_id,
                    "label": label_text,
                    "field_type": field_type,
                    "placeholder": placeholder,
                    "selector": f"#{field_id}" if elem.get("id") else f"[name='{elem.get('name')}']"
                })

            # 2. Parse Google Form elements
            gform_items = soup.find_all("div", {"role": "listitem"})
            for idx, item in enumerate(gform_items):
                heading = item.find(["div", "span"], {"role": "heading"}) or item.find("div", class_=re.compile(r'M7eMe|geBpt'))
                if heading:
                    q_label = heading.get_text(strip=True)
                    # Check for input or textarea inside question block
                    input_el = item.find("input") or item.find("textarea")
                    if input_el:
                        ftype = input_el.get("type", input_el.name).lower()
                        fid = input_el.get("name") or f"gform_input_{idx}"
                        fields.append({
                            "field_id": fid,
                            "label": q_label,
                            "field_type": ftype,
                            "selector": f"[name='{input_el.get('name')}']" if input_el.get("name") else f"div[role='listitem']:nth-of-type({idx+1}) input"
                        })
        except Exception as e:
            print(f"[HTMLFormParser] Parsing error: {e}")

        return fields
