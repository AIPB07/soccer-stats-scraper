from selenium import webdriver
from bs4 import BeautifulSoup

# Set up Selenium driver
options = webdriver.FirefoxOptions()
driver = webdriver.Firefox(options=options)

# Tell driver to navigate to page URL
url = 'https://www.whoscored.com/Regions/252/Tournaments/2/Seasons/7811/Stages/17590/Fixtures/England-Premier-League-2019-2020'
driver.get(url)

# Parse html from webpage
soup = BeautifulSoup(driver.page_source, 'html.parser')

# List for storing fixture links
fixtures = []

# Find all results. Append each link to list
Results = soup.find_all("a", {"class": "result-1"})
for result in Results:
	fixtures.append(result["href"])

for fixture in fixtures:
	print(fixture)
