#scrape site login
#you need to install the Chrome driver
#change the css selectors for your project 

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import time
import json
from bs4 import BeautifulSoup


username = "YOUR USERNAME"
password = "PASSWORD"


# Set up the Selenium WebDriver
driver = webdriver.Chrome()

# Navigate to the first login page
driver.get("https://YOUR FIRST LOGIN URL")

# Find the username and password input fields and enter the credentials
driver.find_element(By.CSS_SELECTOR, 'div[data-v-76bc89e0] input').send_keys(username)
driver.find_element(By.CSS_SELECTOR, 'div[data-v-313bf9a3] input').send_keys(password)

password_input = driver.find_element(By.CSS_SELECTOR, 'div[data-v-313bf9a3] input')
password_input.send_keys(Keys.RETURN)

# Wait for the redirection to the second login page
WebDriverWait(driver, 10).until(EC.url_changes(driver.current_url))
time.sleep(1)
# Check if the current URL is the second login page
if driver.current_url == "https://EXAMPLE234.COM":
    # Find the username and password input fields and enter the credentials
    #driver.find_element(By.NAME, 'username').send_keys(username)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'username'))).send_keys(username)
    #driver.find_element(By.NAME, 'password').send_keys(password)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'password'))).send_keys(password)

    # Submit the form
    driver.find_element(By.CSS_SELECTOR, 'form').submit()

    # Wait for the redirection to the home page
    WebDriverWait(driver, 10).until(EC.url_changes(driver.current_url))
    WebDriverWait(driver, 10).until(EC.url_to_be("https://EXAMPLE234.COM/home"))

    # Locate the button or link to navigate to the reports page and click on it
    # Locate the button or link element by its class and href attribute and click on it to navigate to the reports page
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.nav-link.py-3[href="/reports"]'))).click()

    # Wait for the reports page to load
    WebDriverWait(driver, 10).until(EC.url_changes(driver.current_url))
    WebDriverWait(driver, 10).until(EC.url_to_be("https://EXAMPLE234.COM//reports"))


    # Locate the button or link to navigate to the inventory report page and click on it
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, 'Inventory'))).click()

    # Wait for the inventory report page to load
    WebDriverWait(driver, 10).until(EC.url_changes(driver.current_url))
    WebDriverWait(driver, 10).until(EC.url_to_be("https://EXAMPLE234.COM//reports/inventory-report"))

    inventory_report_page_source = driver.page_source

    # Parse the source code using BeautifulSoup
    soup = BeautifulSoup(inventory_report_page_source, 'html.parser')

    # Find the desired elements using appropriate tags and attributes
    # For example, if the data is in a table, you can use the following code
    table_rows = soup.find_all('tr')

    # Iterate through the table rows and extract the required data
    for row in table_rows:
        columns = row.find_all('td')
        # Extract the data from each column and store it in a list or any other data structure
        data = [column.text.strip() for column in columns]

        # Process the data as needed
        # For example, print the data
        print(data)

driver.quit()


