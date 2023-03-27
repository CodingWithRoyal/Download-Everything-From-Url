import os
import platform
import sys
import requests
import zipfile
import tarfile
import urllib
import time
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By

# Determine the operating system
if platform.system() == "Windows":
    os_name = "win32"
elif platform.system() == "Linux":
    os_name = "linux64"
elif platform.system() == "Darwin":
    os_name = "mac64"
else:
    print("Error: Unsupported operating system.")
    sys.exit(1)

# Determine which browser is installed
# Determine the operating system
if platform.system() == "Windows":
    chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
    firefox_path = "C:/Program Files/Mozilla Firefox/firefox.exe"
elif platform.system() == "Linux":
    chrome_path = "/usr/bin/google-chrome"
    firefox_path = "/usr/bin/firefox"
elif platform.system() == "Darwin":
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    firefox_path = "/Applications/Firefox.app/Contents/MacOS/firefox"
else:
    print("Error: Unsupported operating system.")
    sys.exit(1)

# Check if Chrome or Firefox is installed
if os.path.exists(chrome_path):
    browser_name = "chrome"
    print("Chrome is installed.")
elif os.path.exists(firefox_path):
    browser_name = "firefox"
    print("Firefox is installed.")
else:
    print("Error: Neither Chrome nor Firefox found on the system.")
    sys.exit(1)

# Set the URL and download the appropriate driver
if browser_name == "chrome":
    url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE"
    response = requests.get(url)
    version = response.text.strip()
    download_url = f"https://chromedriver.storage.googleapis.com/{version}/chromedriver_{os_name}.zip"
elif browser_name == "firefox":
    url = f"https://api.github.com/repos/mozilla/geckodriver/releases/latest"
    response = requests.get(url)
    version = response.json()["tag_name"]
    download_url = f"https://github.com/mozilla/geckodriver/releases/download/{version}/geckodriver-{version}-{os_name}.tar.gz"

# Download and extract the driver
response = requests.get(download_url)
if browser_name == "chrome":
    with zipfile.ZipFile(BytesIO(response.content)) as z:
        z.extractall("./driver")
elif browser_name == "firefox":
    with tarfile.open(fileobj=BytesIO(response.content), mode="r:gz") as t:
        t.extractall("./driver")

# Set the full path to the driver executable
if browser_name == "chrome":
    driver_path = os.path.abspath("./driver/chromedriver")
elif browser_name == "firefox":
    driver_path = os.path.abspath("./driver/geckodriver")

# Configure the driver
if browser_name == "chrome":
    driver_service = webdriver.chrome.service.Service(driver_path)
    driver = webdriver.Chrome(service=driver_service)
elif browser_name == "firefox":
    driver_service = webdriver.gecko.service.Service(driver_path)
    driver = webdriver.Firefox(service=driver_service)

# Navigate to the url
url = sys.argv[1]
driver.get(url)

# Set the initial scroll height
last_height = driver.execute_script("return document.body.scrollHeight")

infiniteScrollAlert = False
# Auto-scroll down the page until the end
while True:
    # Scroll down to the bottom of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait for the page to load
    time.sleep(2)

    # Calculate the new scroll height and compare with the last height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        # If the new and last heights are the same, the page hasn't loaded any new content, so we're done scrolling
        print("\nDownloading... :D")
        break
    else:
        # If the new and last heights are different, update the last height and keep scrolling
        if infiniteScrollAlert is False:
            infiniteScrollAlert = True
            print("Infinite Scrolling Detected:")
        else:
            print(".",end=".")
        last_height = new_height

# Find all image elements on the page
images = driver.find_elements(by=By.XPATH, value='//img')

# Create the download directory if it doesn't exist
if not os.path.exists("download/images"):
    os.makedirs("download/images")

# Download each image
for i, image in enumerate(images):
    src = image.get_attribute("src")
    if src is not None and src != "":
        file_extension = os.path.splitext(src)[1]
        file_extension = file_extension.split("?")[0]
        epoch_time = int(time.time())
        image_path = "download/images/{}-image{}".format(epoch_time, file_extension)
        urllib.request.urlretrieve(src, image_path)

# Quit the driver
driver.quit()