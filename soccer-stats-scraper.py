from selenium import webdriver
from bs4 import BeautifulSoup
import mysql.connector
from mysql.connector import errorcode
import time


def player_mins(home_away):
    """Returns list of players and minutes played for a given fixture"""
    
    player_list = []
    # Get full match length (plus injury time)
    match_length = int(soup.find('div', {'title': "FT'"})['data-minute'])
    players = soup.find_all('div', {'class': 'player', 'data-field': home_away})
    for player in players:
        player_dict = {}
        # Find player name
        player_dict['name'] = player.find('div', class_='player-name-wrapper')['title']
        # All players that started game
        if player.parent['class'] == ['pitch-field']:
            # Check if player was subbed off
            if 'data-is-subbed-off' in player.attrs.keys():
                sub_divs = player.find_all('div', class_='incident-icon')
                for sub_div in sub_divs:
                    if 'data-event-satisfier-suboff' in sub_div.attrs.keys():
                        player_dict['minutes'] = int(sub_div['data-minute'])
                        player_dict['seconds'] = int(sub_div['data-second'])
            else:
                # Player completed full match
                player_dict['minutes'] = match_length
                player_dict['seconds'] = 0
        else:
            # Player started on the bench
            subbed_off = False
            if 'data-subbed-in' in player.attrs.keys():
                # Player was subbed on
                sub_div = player.find('div', {'class': 'incident-icon', 'data-event-satisfier-subon': ''})
                #for sub_div in sub_divs:
                #if 'data-event-satisfier-subon' in sub_div.attrs.keys():
                subon_mins = int(sub_div['data-minute'])
                subon_secs = int(sub_div['data-second'])
                if 'data-event-satisfier-suboff' in sub_div.attrs.keys():
                    subbed_off = True
                    suboff_mins = int(sub_div['data-minute'])
                    suboff_secs = int(sub_div['data-second'])
                if not subbed_off:
                    player_dict['minutes'] = match_length - subon_mins - 1
                    player_dict['seconds'] = 60 - subon_secs
                else:
                    if suboff_secs >= subon_secs:
                        player_dict['minutes'] = suboff_mins - subon_mins
                        player_dict['seconds'] = suboff_secs - subon_secs
                    else:
                        player_dict['minutes'] = suboff_mins - subon_mins - 1
                        player_dict['seconds'] = 60 - (subon_secs - suboff_secs)
            else:
                # Player was not subbed on
                player_dict['minutes'] = 0
                player_dict['seconds'] = 0
        player_list.append(player_dict)
        
    return player_list


def goals_assists(home_away):
    """Returns a list of goals for a given fixture"""
    
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
                    goalscorer = str(div.previous_sibling.previous_sibling.string)
                else:
                    goalscorer = str(div.next_sibling.next_sibling.string)
                goaltime = int(div['data-minute'])+1
                goal['scorer'] = goalscorer
                goal['time'] = goaltime
                # Check for an assist
                assist_parent = div.parent.previous_sibling
                if assist_parent != None:
                    for child in assist_parent.children:
                        if child.name == 'a':
                            goal['assist'] = str(child.string)
                else:
                    # Check for assist in previous minute
                    goal_scored = False
                    assist_found = False
                    prev_row = cell.parent.previous_sibling
                    if prev_row != None:
                        prev_cell = prev_row.find('td', {'class': home_away+'-incident'})
                        for child_div in prev_cell.children:
                            if not child_div.contents:
                                break
                            for sub_div in child_div.children:
                                if any(k in sub_div.attrs.keys() for k in ('data-event-satisfier-goalnormal', 'data-event-satisfier-penaltyscored')):
                                    goal_scored = True
                                elif 'data-event-satisfier-assist' in sub_div.attrs.keys():
                                    if home_away == 'home':
                                        assist = str(sub_div.previous_sibling.string)
                                    else:
                                        assist = str(sub_div.next_sibling.string)
                                    assist_found = True
                        if not goal_scored and assist_found:
                            goal['assist'] = assist
                        else:
                            goal['assist'] = ''
                    else:
                        goal['assist'] = ''
                
                goal['home_away'] = home_away
                goals.append(goal)
                goal = {}
                
    return goals


def games_played(team):
    """Returns number of games a team has already played"""

    query = ("SELECT COUNT(HomeTeam) FROM results WHERE HomeTeam = %s "
             "OR AwayTeam = %s")
    mycursor.execute(query, (team, team))
    n_games = int(mycursor.fetchall()[0][0])

    return n_games 


def add_goals(goals, home_away):
    """Inserts goals into database"""

    if home_away == 'home':
        i = 1
        games = home_games
    else:
        i = 0
        games = away_games
    for goal in goals:
        add_goal = ("INSERT INTO goals "
                    "(PlayerName, Opponent, Time, Home_Away, Gameweek, Assist)"
                    " VALUES (%s, %s, %s, %s, %s, %s)")
        mycursor.execute(add_goal, (goal['scorer'], teams[i], goal['time'],
                         home_away, games+1, goal['assist']))
        mydb.commit()


def add_mins(mins, home_away):
    """Inserts minutes into database and player if applicable"""

    if home_away == 'home':
        i = 0
        games = home_games
    else:
        i = 1
        games = away_games
    for player in mins:
        # Check whether player already in player_teams
        query = ("SELECT * FROM player_teams WHERE PlayerName = %s "
                 "AND TeamName = %s")
        mycursor.execute(query, (player['name'], teams[i]))
        if len(mycursor.fetchall()) == 0:
            # Insert player into player_teams
            add_player = ("INSERT INTO player_teams (PlayerName, TeamName) "
                          " VALUES (%s, %s)")
            mycursor.execute(add_player, (player['name'], teams[i]))
            mydb.commit()
        # Insert player mins into player_mins
        add_mins = ("INSERT INTO player_mins (PlayerName, Minutes, Seconds, "
                    "Gameweek) VALUES (%s, %s, %s, %s)")
        mycursor.execute(add_mins, (player['name'], player['minutes'],
                         player['seconds'], games+1))
        mydb.commit()


# Connect to database
print('Please enter database credentials')
host = input('Host: ')
user = input('User: ')
passwd = input('Password: ')
database = input('Database name: ')
print(f'Connecting to database: {database}...')

try:
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        passwd=passwd,
        database=database
    )
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print('Invalid user name or password')
    elif err.errmp == errorcode.ER_BAD_DB_ERROR:
        print('The database does not exist')
    else:
        print(err)
else:
    print('Successfully connected!')
    mycursor = mydb.cursor()

# Configure Selenium driver
options = webdriver.FirefoxOptions()
driver = webdriver.Firefox(options=options)
# Tell driver to navigate to page URL (fixtures)
url = 'https://www.whoscored.com/Regions/252/Tournaments/2/Seasons/7811/Stages/17590/Fixtures/England-Premier-League-2019-2020'
driver.get(url)
# Parse html from webpage
soup = BeautifulSoup(driver.page_source, 'html.parser')

# List for storing fixtures
fixtures = []
# Find all results. Append each link to list
fixture_links = soup.find_all('a', class_='result-1')
print('Finding fixtures...')
i = 0
for f in fixture_links:
    fixtures.append(f['href'])
    i += 1
print(f'{i} fixtures found')
driver.close()

# Iterate over all fixtures
i = 1
for fixture in fixtures:
    # Check whether fixture is already in database
    query = ("SELECT * FROM results WHERE FixtureURL = %s")
    mycursor.execute(query, (fixture,))
    if len(mycursor.fetchall()) != 0:
        continue

    driver = webdriver.Firefox(options=options)
    # Tell driver to navigate to page URL
    url = 'https://www.whoscored.com'+fixture
    print(f'Loading fixture {i} in Selenium...')
    driver.get(url)
    # Wait to ensure driver fully executed
    time.sleep(20)
    print(f'Fixture {i} loaded')
    # Parse html from webpage
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find teams [Home, Away]
    teams = []
    team = soup.find_all('a', class_='team-link')
    for t in team:
        teams.append(str(t.string))
    print(f'Fixture {i} is {teams[0]} vs {teams[1]}')

    # Find how many games each team has played from results database
    home_games = games_played(teams[0])
    away_games = games_played(teams[1])

    # Find result, insert into database
    print('Inserting result into database...')
    result = soup.find('td', class_='result')
    add_result = ("INSERT INTO results (HomeTeam, HomeGoals, AwayTeam, "
                  "AwayGoals, FixtureURL) VALUES (%s, %s, %s, %s, %s)")
    mycursor.execute(add_result, (teams[0], int(result.string[:2]), 
                     teams[1], int(result.string[-2:]), fixture))
    mydb.commit()
    print('Result inserted')
    
    # Find goals
    print('Finding goals/assists...')
    home_goals = goals_assists('home')
    away_goals = goals_assists('away')
    print(f'{len(home_goals)} home goals found!')
    print(f'{len(away_goals)} away goals found!')

    # Insert goals into database
    add_goals(home_goals, 'home')
    add_goals(away_goals, 'away')
    print('Goals inserted')

    # Insert player minutes into database
    # If not already inserted, also insert player into team database
    print('Inserting minutes...')
    home_player_mins = player_mins('home')
    away_player_mins = player_mins('away')
    add_mins(home_player_mins, 'home')
    add_mins(away_player_mins, 'away')
    print('Minutes inserted')

    driver.close()
    i += 1


