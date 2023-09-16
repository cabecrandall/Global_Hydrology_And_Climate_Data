

import time

from selenium import webdriver
from selenium.webdriver.common.by import By

username = input('Enter Username:')
password = input('Enter Password:')

driver = webdriver.Chrome()  # Optional argument, if not specified will search path.

driver.get('https://urs.earthdata.nasa.gov/oauth/authorize?client_id=ZAQpxSrQNpk342OR77kisA&response_type=code&redirect_uri=https://appeears.earthdatacloud.nasa.gov/login&state=/task/area')

search_box = driver.find_element(By.ID, 'username')

search_box.send_keys(username)

search_box = driver.find_element(By.ID, 'password')

search_box.send_keys(password)

search_box.submit()


driver.quit()