import urllib.request
from bs4 import BeautifulSoup
import pandas as pd
import re

school_df = pd.read_csv('schools.csv')
schools = list(school_df.school_name)
game_list = []
for year in range(2011, 2020):
    print(year)
    for school in schools:
        temp_url = r'https://www.sports-reference.com/cbb/schools/' + school + '/' + str(year) + '-gamelogs.html'
        try:
            with urllib.request.urlopen(temp_url) as url:
                s = url.read()
                soup = BeautifulSoup(s, 'html.parser')
                for row in soup.tbody.find_all('tr', id=re.compile('^sgl-basic')):
                    d = {}
                    d['school'] = school
                    d['year'] = year
                    for stat in row.find_all('td'):
                        d[stat['data-stat']] = stat.text
                    try:
                        d['opp_id'] = row.find('td', {'data-stat': 'opp_id'}).a['href'].split('/')[-2]
                    except:
                        pass
                    game_list.append(d)
        except:
            pass

df = pd.DataFrame(game_list)
# df.to_csv('all_box_scores.csv', index=False)
