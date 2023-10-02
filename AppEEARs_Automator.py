'''
NOT INTERACTIVE!
This framework is made to import MODIS data from January, 2001 to the end of December of 2022.
The original data download from this script was MOD16A2GF, which is ET and PET data. Those dates
must be changed if a different dataset is used in order to avoid an error, especially if the data
collection period does not fit between 2001 and 2022. Those parameters can be found on line 47 and 49.
'''
import time
import os
from tqdm import tqdm

from email import message_from_file
import emlx

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


def extractGeoData(dataset, start_date, end_date):
    # create finish log

    file = open('shape_request_log.txt', 'r')
    bug_log = open('appeears_bug_log.txt', 'r')
    finished_shapes = file.readlines()
    bad_shapes = bug_log.readlines()
    # process data!
    for i in range(len(finished_shapes)):
        finished_shapes[i] = finished_shapes[i][:7]

    for i in bad_shapes:
        if len(i) > 7:
            ID = i[:7]
            finished_shapes.append(ID)

    username = input('Enter Username:')
    password = input('Enter Password:')

    driver = webdriver.Chrome()  # Optional argument, if not specified will search path.

    driver.get(
        'https://urs.earthdata.nasa.gov/oauth/authorize?client_id=ZAQpxSrQNpk342OR77kisA&response_type=code&redirect_uri=https://appeears.earthdatacloud.nasa.gov/login&state=/task/area')

    search_box = driver.find_element(By.ID, 'username')

    search_box.send_keys(username)

    search_box = driver.find_element(By.ID, 'password')

    search_box.send_keys(password)

    search_box.submit()

    driver.implicitly_wait(20)

    box = driver.find_element(By.CSS_SELECTOR,
                              "#top > app-root > div > main > app-task > div.card.card-body > div > div > div > div.col.col-lg-4.col-first.mx-auto > div.body > a > img")

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

    # initialize progress bar
    size = 0
    for file in os.listdir('catchment_shapes'):
        size += 1
    loop = tqdm(total=size)

    finishlog = open('shape_request_log.txt', 'a+')
    bug_log = open('appeears_bug_log.txt', 'a+')
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
            # submission
            box = driver.find_element(By.CSS_SELECTOR,
                                      '#top > app-root > div > main > app-task > div.card.card-body > form > div:nth-child(4) > div > button.btn.btn-text.btn-primary')
            time.sleep(2)
            box.click()
            # The catchment request is considered "sent" if the "successful submission" message is output.
            # If not, the error message is saved to a log.
            try:
                box = driver.find_element(By.CSS_SELECTOR, '#top > app-root > div > app-alert > p > ngb-alert')
                message = box.text
                while len(message) < 1:
                    box = driver.find_element(By.CSS_SELECTOR, '#top > app-root > div > app-alert > p > ngb-alert')
                    message = box.text
                if "The area sample request was successfully submitted" in message:
                    finishlog.write(f'{ID}\n')
                else:
                    bug_log.write(f'{ID} ERROR: {message}\n')
            except:
                bug_log.write(f'{ID} ERROR: No completion message detected\n')
            loop.update(1)

    driver.quit()


def verifyRequestsReceived(rootDirectory: str, function="remove"):
    # If you suspect that the web scraping function that forms the heart of this
    # module skipped some catchment requests, you can pass a folder with AppEEARS
    # email files on it to see which catchments you actually have download links for!

    file = open('shape_request_log.txt', 'r')
    finished_shapes = file.readlines()
    # process data!
    for i in range(len(finished_shapes)):
        finished_shapes[i] = finished_shapes[i][:7]

    # count files
    file_count = 0
    for subdir, dirs, files in os.walk(rootDirectory):
        for file in files:
            file_count += 1

    print("Processing Email Folder")
    loop = tqdm(total=file_count)
    completeIDs = []
    for subdir, dirs, files in os.walk(rootDirectory):
        for file in files:
            ending = file[-4:]
            if ending == "emlx":
                path = os.path.join(subdir, file)
                email = emlx.read(path)
                if "appeears" in email['From']:
                    # If Complete in "subject", add Subject ID to list
                    if "Complete" in email['Subject']:
                        completeIDs.append(email['Subject'][9:16])
            loop.update()

    if function is "remove":
        # see which finished shapes don't actually have completed requests
        for ID in finished_shapes:
            if ID not in completeIDs:
                finished_shapes.remove(ID)

        file = open('shape_request_log.txt', 'w')
        for ID in finished_shapes:
            file.write(ID + '\n')

    elif function is "add":
        for ID in completeIDs:
            if ID not in finished_shapes:
                finished_shapes.append(ID)

        file = open('shape_request_log.txt', 'w')
        for ID in finished_shapes:
            file.write(ID + '\n')

    else:
        Exception("Invalid argument!")

    # for testing:
    # print(len(completeIDs))
    # completeIDs = sorted(completeIDs)
    # for ID in completeIDs:
    #     print(ID)


# TODO: Set parameters to parse and organize AND download relevant files


def main():
    extractGeoData('MOD16A2GF', '01-01-01', '12-31-22')
    # verifyRequestsReceived("/Users/calebcrandall/Documents/All Mail.mbox",
    #                        function="add")


if __name__ == '__main__':
    main()
    exit()
