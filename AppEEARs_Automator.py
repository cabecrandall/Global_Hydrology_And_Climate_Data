

import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.options import BaseOptions
from selenium.webdriver.support.ui import Select

username = input('Enter Username:')
password = input('Enter Password:')

driver = webdriver.Chrome()  # Optional argument, if not specified will search path.

driver.get('https://urs.earthdata.nasa.gov/oauth/authorize?client_id=ZAQpxSrQNpk342OR77kisA&response_type=code&redirect_uri=https://appeears.earthdatacloud.nasa.gov/login&state=/task/area')

search_box = driver.find_element(By.ID, 'username')

search_box.send_keys(username)

search_box = driver.find_element(By.ID, 'password')

search_box.send_keys(password)

search_box.submit()

time.sleep(6)

box = driver.find_element(By.CSS_SELECTOR, "#top > app-root > div > main > app-task > div.card.card-body > div > div > div > div.col.col-lg-4.col-first.mx-auto > div.body > a > img")

box.click()



driver.quit()