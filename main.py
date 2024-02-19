from bs4 import BeautifulSoup
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import ElementClickInterceptedException


def scrape_payscale_data(url):
    all_data = []
    # Set up Chrome WebDriver
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("detach", True)
    #service = ChromeService("path/to/chromedriver")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)
        time.sleep(2)  # Add a small delay to allow dynamic content to load
        cookie_button = driver.find_element(By.XPATH, "//*[@id='onetrust-accept-btn-handler']")
        cookie_button.click()
        page_counter = 1
        pages_element = driver.find_element(By.XPATH, "//*[@id='__next']/div/div[1]/article/div[3]/a[6]/div")
        number_of_pages = int(pages_element.text)

        while True:
            # Parse the HTML content of the page
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Find the table containing the data
            table = soup.find('table')

            # Extract column headers
            headers = [th.text.strip() for th in table.find('thead').find_all('th')]

            # Extract data rows
            data_rows = []
            for row in table.find('tbody').find_all('tr'):
                data_rows.append([td.text.strip() for td in row.find_all(class_="data-table__value")])

            # Extend the list of all data with the data from the current page
            all_data.extend(data_rows)

            # Check if there is a next page

            next_page_link = driver.find_element(By.CLASS_NAME, 'pagination__next-btn')
            if page_counter < number_of_pages:
                next_page_link.click()
                page_counter += 1
                print(page_counter)
                time.sleep(3)
            else:
                break
        time.sleep(5)

    finally:
        driver.quit()

    # Create a DataFrame from all the collected data
    if all_data:
        df = pd.DataFrame(all_data, columns=headers)
        return df
    else:
        return None


# URL of the first page with the table
url = "https://www.payscale.com/college-salary-report/majors-that-pay-you-back/bachelors"

# Scrape data from all pages
result_df = scrape_payscale_data(url)

# Save to CSV
if result_df is not None:
    result_df.to_csv('payscale_data_all_pages.csv', index=False)
    print("Data saved to 'payscale_data_all_pages.csv'")

