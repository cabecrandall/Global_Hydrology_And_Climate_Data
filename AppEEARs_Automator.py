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
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


def extractGeoData(dataset, start_date, end_date, directory):
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
            ID = longest_numeric_substring(i)
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
    for file in os.listdir(directory):
        size += 1
    loop = tqdm(total=(size - len(finished_shapes)))

    finishlog = open('shape_request_log.txt', 'a+')
    bug_log = open('appeears_bug_log.txt', 'a+')
    finishlog.write('\n')
    for file in os.listdir(directory):
        ID = longest_numeric_substring(file)
        if ID not in finished_shapes:
            driver.implicitly_wait(10)
            box = driver.find_element(By.ID, 'taskName')
            box.clear()
            box.send_keys(ID)
            box = driver.find_element(By.ID, 'shapeFileUpload')
            path = os.path.join(directory, file)
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
                while len(message) < 1 or "too complex" in message:
                    box = driver.find_element(By.CSS_SELECTOR, '#top > app-root > div > app-alert > p > ngb-alert')
                    message = box.text
                if "The area sample request was successfully submitted" in message:
                    finishlog.write(f'{ID}\n')
                elif "tomorrow" in message:
                    print("You reached the limit for daily requests!")
                    exit(0)
                else:
                    bug_log.write(f'{ID} ERROR: {message}\n')
            except:
                bug_log.write(f'{ID} ERROR: No completion message detected\n')
            loop.update(1)

    driver.quit()

def longest_numeric_substring(input_string):
    current_numeric = ""
    longest_numeric = ""

    for char in input_string:
        if char.isnumeric():
            current_numeric += char
        else:
            if len(current_numeric) > len(longest_numeric):
                longest_numeric = current_numeric
            current_numeric = ""

    # Check if the last numeric substring is the longest
    if len(current_numeric) > len(longest_numeric):
        longest_numeric = current_numeric

    return longest_numeric


def findAppEEARSCompletedCatchments(rootDirectory: str):
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
    return completeIDs


def verifyRequestsReceived(rootDirectory: str):
    """
    # If you suspect that the web scraping function that forms the heart of this
    # module skipped some catchment requests, you can pass a folder with AppEEARS
    # email files on it to see which catchments you actually have download links for!
    """

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
    completeIDs = findAppEEARSCompletedCatchments(rootDirectory)

    if len(finished_shapes) > len(completeIDs):
        # see which finished shapes don't actually have completed requests
        for ID in finished_shapes:
            if ID not in completeIDs:
                finished_shapes.remove(ID)

        file = open('shape_request_log.txt', 'w')
        for ID in finished_shapes:
            file.write(ID + '\n')

    else:
        for ID in completeIDs:
            if ID not in finished_shapes:
                finished_shapes.append(ID)

        file = open('shape_request_log.txt', 'w')
        for ID in finished_shapes:
            file.write(ID + '\n')

    # for testing:
    # print(len(completeIDs))
    # completeIDs = sorted(completeIDs)
    # for ID in completeIDs:
    #     print(ID)


# TODO: Set parameters to parse and organize AND download relevant files

def isDownloaded(file_stub):
    if len(file_stub) > 0:
        downloads = os.listdir("/Users/calebcrandall/Downloads")
        for thing in downloads:
            if file_stub in thing:
                return True
        return False


def renameDownloadToID(key_word, ID):
    """
    renames a downloaed file to the desired ID. The file must be in a computer root folder named "Downloads".
    :param key_word: A means of finding the file, either the entire name or a unique substring of the file.
    :param ID: The desired name for the file.
    :return:
    """
    directory = "/Users/calebcrandall/Downloads"
    for file in os.listdir(directory):
        if key_word in file:
            os.rename(os.path.join(directory, file), os.path.join(directory, f"{ID}.csv"))


def findNumberofPages(driver):
    page_count = 0
    page_list_location = driver.find_element(By.CSS_SELECTOR,
                                             "#top > app-root > div > main > app-explore > div.table-responsive > table > thead")
    for element in page_list_location.find_elements(By.TAG_NAME, "a"):
        if element.text.isnumeric():
            page_count += 1
    return page_count



def downloadCatchmentTimeSeries():
    # tODO: Make the loop "while new files are not found in the page iteration" and see what happens
    skip = False

    username = input('Enter Username:')
    password = input('Enter Password:')

    driver = webdriver.Chrome()  # Optional argument, if not specified will search path.

    driver.get('https://appeears.earthdatacloud.nasa.gov/explore')

    driver.implicitly_wait(20)
    search_box = driver.find_element(By.ID, 'username')
    search_box.send_keys(username)
    search_box = driver.find_element(By.ID, 'password')
    search_box.send_keys(password)
    search_box.submit()
    driver.implicitly_wait(20)

    num_pages = findNumberofPages(driver)

    for page in range(num_pages - 1):
        print(f"Page {page + 1} starting...")
        table = driver.find_element(By.CSS_SELECTOR,
                                    "#top > app-root > div > main > app-explore > div.table-responsive > table")
        links = table.find_elements(By.TAG_NAME, "a")

        fresh_links = driver.find_elements(By.TAG_NAME, "a")
        page_to_find = page + 2
        # loop = tqdm(total=len(links))
        for link in range(len(links)):
            fresh_link = fresh_links[link]
            # resets fresh_links to eliminate staleness
            try:
                fresh_links, skip = analyze_link(driver, fresh_link, fresh_links, links, skip, page, page_to_find)
            except:
                print("Exception: " )
                fresh_links = driver.find_elements(By.TAG_NAME, "a")
                fresh_link = fresh_links[link]
                fresh_links, skip = analyze_link(driver, fresh_link, fresh_links, links, skip, page, page_to_find)
            # loop.update(1)
        go_to_page(driver, links, page_to_find)
        print(f"page {page + 1} finished!")


def go_to_page(driver, links, page_to_find):
    fresh_links = driver.find_elements(By.TAG_NAME, "a")
    for link in range(len(fresh_links)):
        fresh_link = fresh_links[link]
        try:
            link_text = fresh_link.text
        except:
            print("Stale Element Exception")
            fresh_links = driver.find_elements(By.TAG_NAME, "a")
            fresh_link = fresh_links[link]
            link_text = fresh_link.text

        if link_text == str(page_to_find):
            box = driver.find_element(By.LINK_TEXT, fresh_link.text)
            actions = ActionChains(driver)
            actions.move_to_element(box).click().perform()
            break


def analyze_link(driver, fresh_link, fresh_links, links, skip, page, page_to_find):
    if not skip:
        if isDownloaded(fresh_link.text):
            skip = True
    if fresh_link.get_attribute("title") == "Download the contents of the request":
        if not skip:
            fresh_link.click()
            # download file!
            target = driver.find_element(By.CSS_SELECTOR,
                                         "#top > app-root > div > main > app-download-task > div.row > div > div.panel.panel-default.table-responsive > table > tbody > tr:nth-child(7) > td:nth-child(1) > a")
            target.click()
            ID = driver.find_element(By.CSS_SELECTOR,
                                     "#top > app-root > div > main > app-download-task > div.row > div > div:nth-child(1) > div.panel-heading > a").text
            renameDownloadToID("MOD16A2GF", ID)
            driver.back()
            # This dummy variable (below) is needed to prove that the page loaded
            driver.implicitly_wait(20)
            table = driver.find_element(By.CSS_SELECTOR,
                                        "#top > app-root > div > main > app-explore > div.table-responsive > table")
            if page > 0:
                go_to_page(driver, links, page_to_find - 1)
                driver.implicitly_wait(20)

            # This dummy variable is needed to prove that the page loaded
            table = driver.find_element(By.CSS_SELECTOR,
                                        "#top > app-root > div > main > app-explore > div.table-responsive > table")
            fresh_links = driver.find_elements(By.TAG_NAME, "a")
        skip = False
    return fresh_links, skip


def main():
    extractGeoData('MOD16A2GF', '01-01-01', '12-31-22', 'GAGES_shapefiles')
    # verifyRequestsReceived("/Users/calebcrandall/Documents/All Mail.mbox")
    # downloadCatchmentTimeSeries()


if __name__ == '__main__':
    main()
    exit()
