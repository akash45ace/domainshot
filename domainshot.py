#!/usr/bin/python3

import os
import time
import re
import requests
import argparse
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image

#banner
def print_banner():
    banner = """    
    ==================================
        D O M A I N S H O T
    ==================================
    """                 
    print(banner)

def load_subdomains(file_path):
    with open(file_path, 'r') as file:
        subdomains = [line.strip() for line in file.readlines()]
    return subdomains

def is_reachable(subdomain):
    if not subdomain.startswith("https://"):
        url = f"https://{subdomain}"
    else:
        url = subdomain

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return True
    except requests.RequestException as e:
        print(f"Error reaching {url}: {e}")
    
    return False

def setup_webdriver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=webdriver.chrome.service.Service(ChromeDriverManager().install()), options=options)
    return driver

def capture_screenshot(driver, subdomain, save_path):
    if not subdomain.startswith("https://"):
        url = f"https://{subdomain}"
    else:
        url = subdomain

    driver.get(url)
    time.sleep(3)
    
    # Sanitize the filename
    sanitized_subdomain = re.sub(r'[^\w\-_\. ]', '_', subdomain.replace("https://", ""))
    
    screenshot_path = os.path.join(save_path, f"{sanitized_subdomain}.png")
    driver.save_screenshot(screenshot_path)

    img = Image.open(screenshot_path)
    img.save(screenshot_path)

def main(subdomains_file, save_path):
    subdomains = load_subdomains(subdomains_file)
    driver = setup_webdriver()

    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    for subdomain in subdomains:
        if is_reachable(subdomain):
            print(f"Taking screenshot of: {subdomain}")
            capture_screenshot(driver, subdomain, save_path)
        else:
            print(f"Subdomain not reachable: {subdomain}")
    
    driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Subdomain Screenshot Tool")
    parser.add_argument("subdomains_file", help="Path to the file containing the list of subdomains")
    parser.add_argument("--save_path", default="screenshots", help="Directory where screenshots will be saved")

    args = parser.parse_args()
    main(args.subdomains_file, args.save_path)
