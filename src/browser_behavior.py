import sys
import time
from pathlib import Path

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Runs before any page script, so popups and alerts can be counted
INIT_JS = """
window.__bb = {popups: 0, alerts: 0};
window.open = function() { window.__bb.popups += 1; return null; };
window.alert = function() { window.__bb.alerts += 1; };
"""

COLLECT_JS = """
const host = location.hostname;
const ext = Array.from(document.forms).filter(f => {
  try { return new URL(f.action, location.href).hostname !== host; }
  catch (e) { return false; }
}).length;
const nav = performance.getEntriesByType('navigation')[0];
return {
  popups: window.__bb ? window.__bb.popups : 0,
  alerts: window.__bb ? window.__bb.alerts : 0,
  iframes: document.querySelectorAll('iframe').length,
  hidden_fields: document.querySelectorAll('input[type=hidden]').length,
  password_fields: document.querySelectorAll('input[type=password]').length,
  external_form_submit: ext,
  right_click_disabled: (document.oncontextmenu !== null ||
      (document.body && document.body.oncontextmenu !== null)) ? 1 : 0,
  http_redirects: nav ? nav.redirectCount : 0
};
"""


def make_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,800")
    opts.add_argument("--disable-notifications")
    opts.set_capability("unhandledPromptBehavior", "dismiss")
    driver = webdriver.Chrome(options=opts)
    driver.set_page_load_timeout(15)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": INIT_JS})
    return driver


def collect(driver, url, wait=1.5):
    driver.get(url)
    time.sleep(wait)  # let redirects and page scripts finish
    data = driver.execute_script(COLLECT_JS)
    changed = int(driver.current_url.rstrip("/") != url.rstrip("/"))
    data["url_changed"] = changed
    data["redirects_total"] = data["http_redirects"] + changed
    data["url"] = url.split("/")[-1] if url.startswith("file:") else url
    return data


if __name__ == "__main__":
    if len(sys.argv) > 1:
        urls = sys.argv[1:]
    else:
        demo = Path("demo_pages")
        urls = [(demo / n).resolve().as_uri()
                for n in ["legit_like.html", "phish_start.html"]]

    driver = make_driver()
    rows = []
    try:
        for u in urls:
            try:
                rows.append(collect(driver, u))
            except Exception as e:
                print("Failed:", u, "-", str(e)[:100])
    finally:
        driver.quit()

    out = pd.DataFrame(rows)
    cols = ["url", "redirects_total", "popups", "iframes", "hidden_fields",
            "password_fields", "external_form_submit", "right_click_disabled"]
    pd.set_option("display.width", 200)
    print(out[cols].to_string(index=False))
    out[cols].to_csv("results/browser_behavior_demo.csv", index=False)
    print("\nSaved results/browser_behavior_demo.csv")
