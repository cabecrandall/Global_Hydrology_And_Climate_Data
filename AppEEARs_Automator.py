'''
NOT INTERACTIVE!
This framework is made to import MODIS data from January, 2001 to the end of December of 2022.
The original data download from this script was MOD16A2GF, which is ET and PET data. Those dates
must be changed if a different dataset is used in order to avoid an error, especially if the data
collection period does not fit between 2001 and 2022. Those parameters can be found on line 47 and 49.
'''
import time
import os

from email import message_from_file
import emlx

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

def extractGeoData(dataset, start_date, end_date):
    # create finish log

    file = open('shape_request_log.txt', 'r')
    finished_shapes = file.readlines()
    # process data!
    for i in range(len(finished_shapes)):
        finished_shapes[i] = finished_shapes[i][:7]

    username = input('Enter Username:')
    password = input('Enter Password:')

    driver = webdriver.Chrome()  # Optional argument, if not specified will search path.

    driver.get('https://urs.earthdata.nasa.gov/oauth/authorize?client_id=ZAQpxSrQNpk342OR77kisA&response_type=code&redirect_uri=https://appeears.earthdatacloud.nasa.gov/login&state=/task/area')

    search_box = driver.find_element(By.ID, 'username')

    search_box.send_keys(username)

    search_box = driver.find_element(By.ID, 'password')

    search_box.send_keys(password)

    search_box.submit()

    driver.implicitly_wait(20)

    box = driver.find_element(By.CSS_SELECTOR, "#top > app-root > div > main > app-task > div.card.card-body > div > div > div > div.col.col-lg-4.col-first.mx-auto > div.body > a > img")

    box.click()

    # Specify parameters (start and end date)
    box = driver.find_element(By.ID, 'startDate')
    box.send_keys(start_date)
    box = driver.find_element(By.ID, 'endDate')
    box.send_keys(end_date)
    box = driver.find_element(By.ID, 'product')
    box.send_keys(dataset)
    time.sleep(0.5)
    box.send_keys(Keys.TAB)

    # Specify desired layers
    box = driver.find_element(By.CSS_SELECTOR,
                              '#top > app-root > div > main > app-task > div.card.card-body > form > div:nth-child(2) > div > app-area-selector > div > div:nth-child(4) > div:nth-child(1) > div.list-group-item.layers.layers-available.ng-tns-c38-1 > div:nth-child(2)')
    box.click()
    box = driver.find_element(By.CSS_SELECTOR,
                              '#top > app-root > div > main > app-task > div.card.card-body > form > div:nth-child(2) > div > app-area-selector > div > div:nth-child(4) > div:nth-child(1) > div.list-group-item.layers.layers-available.ng-tns-c38-1 > div:nth-child(5)')
    box.click()
    box = driver.find_element(By.ID, 'projection')
    box.send_keys('Native Projection')
    time.sleep(0.5)
    box.send_keys(Keys.TAB)

    # TODO: Make a finished log.txt file
    # TODO: Clear all boxes, or initialize only with best boxes
    finishlog = open('shape_request_log.txt', 'a+')
    finishlog.write('\n')
    for file in os.listdir('catchment_shapes'):
        ID = file[6:13]
        if ID not in finished_shapes:
            driver.implicitly_wait(10)
            box = driver.find_element(By.ID, 'taskName')
            box.clear()
            box.send_keys(ID)
            box = driver.find_element(By.ID, 'shapeFileUpload')
            path = os.path.join('catchment_shapes', file)
            box.send_keys(os.path.abspath(path))
            #submission
            box = driver.find_element(By.CSS_SELECTOR, '#top > app-root > div > main > app-task > div.card.card-body > form > div:nth-child(4) > div > button.btn.btn-text.btn-primary')
            time.sleep(2)
            box.click()
            finishlog.write(f'{ID}\n')



    driver.quit()

def verifyRequestsReceived(rootDirectory):
    # create finish log

    file = open('shape_request_log.txt', 'r')
    finished_shapes = file.readlines()
    # process data!
    for i in range(len(finished_shapes)):
        finished_shapes[i] = finished_shapes[i][:7]

    print(os.listdir(rootDirectory))
    for subdir, dirs, files in os.walk(rootDirectory):
        for file in files:
            ending = file[-4:]
            if ending == "emlx":
                path = os.path.join(subdir, file)
                email = emlx.read(path)
                if "appeears" in email['From']:
                    print(path)
# TODO: Set parameters to parse and organize AND download relevant files




def main():
    # extractGeoData('MOD16A2GF', '01-01-01', '12-31-22')
    verifyRequestsReceived("/Users/calebcrandall/Documents/Gmail/All Mail.mbox/6D75E799-CD81-4BCD-B786-D68CB1D2112D")


if __name__ == '__main__':
    main()
    exit()

