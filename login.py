from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from constants import email, password, linkedin_login_url
import time
import random

proxies_list = [
    'giK5XZZFO4RG25pP3bdf:RNW78Fm5@185.130.105.109:10000'
]

def login():
    proxy = random.choice(proxies_list)
    chrome_options = Options()
    chrome_options.add_argument('--proxy-server=%s' % proxy)
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path="/chromedriver", options=chrome_options)
    time.sleep(3)
    return driver


def login_with_credentials():
    proxy = random.choice(proxies_list)
    chrome_options = Options()
    chrome_options.add_argument('--proxy-server=%s' % proxy)
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path="/chromedriver", options=chrome_options)

    driver.get(linkedin_login_url)

    time.sleep(5)

    username = driver.find_element(By.ID, "username")
    username.send_keys(email)

    pword = driver.find_element(By.ID, "password")
    pword.send_keys(password)

    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    return driver
