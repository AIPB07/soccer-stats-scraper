from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import html
import time

# Configure Selenium driver
options = webdriver.FirefoxOptions()
driver = webdriver.Firefox(options=options)

# Tell driver to navigate to page URL
url = 'https://www.whoscored.com/Matches/1375943/Live/England-Premier-League-2019-2020-Norwich-Newcastle-United'
driver.get(url)

# Wait to ensure driver fully executed
time.sleep(20)

# Parse html from webpage
soup = BeautifulSoup(driver.page_source, 'html.parser')

def goals_assists(home_away):
    """Function that returns a list of goals for a given fixture"""
    
    goal = {}
    goals = []
    
    if home_away not in ('home', 'away'):
        print('Unexpected input to goals_assists() function')
        return
    else:
        cells = soup.find_all('td', {'class': home_away+'-incident'})
        
    for cell in cells:
        divs = cell.find_all('div', {'class': 'incident-icon'})
        for div in divs:
            # Check for a goal (normal or penalty)
            if any(k in div.attrs.keys() for k in ('data-event-satisfier-goalnormal', 'data-event-satisfier-penaltyscored')):
                if home_away == 'home':
                    goalscorer = div.previous_sibling.previous_sibling.string
                else:
                    goalscorer = div.next_sibling.next_sibling.string
                goaltime = int(div['data-minute'])+1
                goal['scorer'] = goalscorer
                goal['time'] = goaltime
                # Check for an assist
                assist_parent = div.parent.previous_sibling
                if assist_parent != None:
                    for child in assist_parent.children:
                        if child.name == 'a':
                            goal['assist'] = child.string
                else:
                    # Check for assist in previous minute
                    goal_scored = False
                    no_assist = False
                    prev_row = cell.parent.previous_sibling
                    if prev_row != None:
                        prev_cell = prev_row.find('td', {'class': home_away+'-incident'})
                        for child_div in prev_cell.children:
                            if not child_div.contents:
                                no_assist = True
                                break
                            for sub_div in child_div.children:
                                if any(k in sub_div.attrs.keys() for k in ('data-event-satisfier-goalnormal', 'data-event-satisfier-penaltyscored')):
                                    goal_scored = True
                                elif 'data-event-satisfier-assist' in sub_div.attrs.keys():
                                    assist = sub_div.previous_sibling.string
                        if not goal_scored and not no_assist:
                            goal['assist'] = assist
                        else:
                            goal['assist'] = ''
                    else:
                        goal['assist'] = ''

                goal['home_away'] = home_away        
                goals.append(goal)
                goal = {}
                
    return goals


# Find teams [Home, Away]
teams = []
rows = soup.find_all('tr')
for row in rows:
    cells = row.find_all('td', {'class': 'team'})
    for cell in cells:
        team = cell.find_all('a', {'class': 'team-link'})
        for t in team:
            print(t.string)
            teams.append(t.string)

# Find goals
home_goals = goals_assists('home')
away_goals = goals_assists('away')

for goal in home_goals:
	print(goal)
for goal in away_goals:
	print(goal)

    		
    		

    	

		

		



