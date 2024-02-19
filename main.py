import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_payscale_data(url):
    all_data = []

    while url:
        # Send a GET request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.content, 'html.parser')

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
            next_page_link = soup.find('a', {'class': 'pagination__next-btn'})
            if next_page_link:
                url = f"https://www.payscale.com{next_page_link['href']}"
            else:
                url = None

        else:
            print("Failed to retrieve the webpage. Status code:", response.status_code)
            break

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

