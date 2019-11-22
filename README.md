# Soccer Stats Scraper
A simple script for scraping data from a soccer statistics webpage and inserting them into a MySQL database.

Player statistics include: goals, assists (by gameweek, opponent and home/away) and minutes (by gameweek).

Team statistics include: goals for and goals against (by opponent and home/away).

## Installation & Usage
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the required packages. 

```bash
pip install -r requirements.txt
```
Then set up the database tables as outlined in schema.sql. This example uses a MySQL database.

Finally, run the soccer-stats-scraper.py script, inputting database credentials when prompted.

## Areas for improvement
Currently this script only works for the set of fixtures first loaded on the webpage i.e. the current month's fixtures. For the 'gameweek' column in the tables to be correct, the script needs to be altered so that the Selenium WebDriver first navigates to the first page of fixtures of the season.