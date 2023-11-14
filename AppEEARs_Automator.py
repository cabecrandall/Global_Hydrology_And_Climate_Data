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

global exception_counter


def extractGeoData(dataset, start_date, end_date, directory):
    # create finish log
    if not os.path.exists('shape_request_log.txt'):
        file = open('shape_request_log.txt', 'w+')
        file.close()
    file = open("shape_request_log.txt", "r")

    # create bug log
    if not os.path.exists('appeears_bug_log.txt'):
        bugfile = open('appeears_bug_log.txt', 'w+')
        bugfile.close()
    bug_log = open('appeears_bug_log.txt', 'r')

    finished_shapes = []


    # process data!
    for line in file:
        ID = longest_numeric_substring(line)
        finished_shapes.append(ID)

    for line in bug_log:
        ID = longest_numeric_substring(line)
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
                    time.sleep(0.25)   # wait for error message to appear
                    box = driver.find_element(By.CSS_SELECTOR, '#top > app-root > div > app-alert > p > ngb-alert')
                    message = box.text
                if "The area sample request was successfully submitted" in message:
                    finishlog.write(f'{ID}\n')
                elif "tomorrow" in message:
                    print("You reached the limit for daily requests!")
                    input("Press enter to continue...")
                    exit(0)
                else:
                    bug_log.write(f'{ID} ERROR: {message}\n')
            except:
                bug_log.write(f'{ID} ERROR: No completion message detected\n')
            loop.update(1)


    finishlog.close()
    bug_log.close()
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


def verifyRequestsReceived(page_to_break = 2):
    """
    This function checks the "Explore" tab of AppEEARS to see if all requests have been received.
    :return:
    """

    listed_IDs = []
    file = open('shape_request_log.txt', 'r')
    for line in file:
        ID = longest_numeric_substring(line)
        listed_IDs.append(ID)
    file.close()

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

    requested_IDs = []

    for page in range(num_pages):
        print(f"Page {page + 1} starting...")
        table = driver.find_element(By.CSS_SELECTOR,
                                    "#top > app-root > div > main > app-explore > div.table-responsive > table")
        links = table.find_elements(By.TAG_NAME, "td")

        fresh_links = driver.find_elements(By.TAG_NAME, "td")
        page_to_find = page + 2
        if page_to_find == page_to_break + 2:
            break
        # loop = tqdm(total=len(links))
        for link in range(len(links)):
            table_cells = driver.find_elements(By.TAG_NAME, "td")
            cell = fresh_links[link]
            # resets fresh_links to eliminate staleness
            if len(cell.text) > 6 and cell.text.isnumeric():
                if cell.text not in listed_IDs:
                    requested_IDs.append(cell.text)
        go_to_page(driver, links, page_to_find)
        print(f"page {page + 1} finished!")
    file = open('shape_request_log.txt', 'a+')
    for ID in requested_IDs:
        file.write(f'{ID}\n')
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



def downloadCatchmentTimeSeries(skip_to_page=0):
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

    for page in range(num_pages - (1 + skip_to_page)):
        print(f"Page {page + 1} starting...")
        table = driver.find_element(By.CSS_SELECTOR,
                                    "#top > app-root > div > main > app-explore > div.table-responsive > table")
        links = table.find_elements(By.TAG_NAME, "a")

        fresh_links = driver.find_elements(By.TAG_NAME, "a")
        page_to_find = page + 2
        # loop = tqdm(total=len(links))
        for link in range(len(links)):
            fresh_links = driver.find_elements(By.TAG_NAME, "a")
            fresh_link = fresh_links[link]
            # resets fresh_links to eliminate staleness
            fresh_links, skip = analyze_link(driver, fresh_link, fresh_links, links, skip, page, page_to_find, link)
            # print("Exception: ")
            # fresh_links = driver.find_elements(By.TAG_NAME, "a")
            # fresh_link = fresh_links[link]
            # fresh_links, skip = analyze_link(driver, fresh_link, fresh_links, links, skip, page, page_to_find)
            # loop.update(1)
        go_to_page(driver, links, page_to_find)
        print(f"page {page + 1} finished!")


def go_to_page(driver, links, page_to_find):
    fresh_links = driver.find_elements(By.TAG_NAME, "a")
    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.CONTROL + Keys.HOME)
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
            time.sleep(1)
            break


def analyze_link(driver, fresh_link, fresh_links, links, skip, page, page_to_find, link):
    try:
        if not skip:
            if isDownloaded(fresh_link.text):
                skip = True
        if fresh_link.get_attribute("title") == "Download the contents of the request":
            if not skip:
                actions = ActionChains(driver)
                actions.move_to_element(fresh_link)
                actions.click()
                actions.perform()
                # download file!
                target = driver.find_element(By.CSS_SELECTOR,
                                             "#top > app-root > div > main > app-download-task > div.row > div > div.panel.panel-default.table-responsive > table > tbody > tr:nth-child(7) > td:nth-child(1) > a")
                actions.move_to_element(target).click().perform()
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
    except (Exception):
        print("Exception: ")
        driver.get('https://appeears.earthdatacloud.nasa.gov/explore')
        go_to_page(driver, links, page_to_find)
        fresh_links = driver.find_elements(By.TAG_NAME, "a")
        fresh_link = fresh_links[link]
        fresh_links, skip = analyze_link(driver, fresh_link, fresh_links, links, skip, page, page_to_find, link)
        return fresh_links, skip


def main():
    extractGeoData('MOD16A2GF', '01-01-01', '12-31-22', 'GAGES_shapefiles')
    # verifyRequestsReceived(page_to_break=6)
    # downloadCatchmentTimeSeries()


if __name__ == '__main__':
    main()
    exit()
