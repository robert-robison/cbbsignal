import urllib.request
from bs4 import BeautifulSoup
import pandas as pd

school_list = []
with urllib.request.urlopen(r'https://www.sports-reference.com/cbb/schools/') as url:
    s = url.read()
    soup = BeautifulSoup(s, 'html.parser')

    for row in soup.tbody.find_all('tr'):
        if row.find('th')['class'][0] == 'right':
            d = {}
            d['years'] = int(row.find('td', {'data-stat': 'years'}).text)
            d['year_min'] = int(row.find('td', {'data-stat': 'year_min'}).text)
            d['year_max'] = int(row.find('td', {'data-stat': 'year_max'}).text)
            d['school_name'] = str(row.find('td', {'data-stat': 'school_name'}).a['href']).split('/')[-2]
            school_list.append(d)

df = pd.DataFrame(school_list)
df = df[(df.year_max == 2019) & (df.year_min <= 2010) & (df.years >= 10)]
df.to_csv('schools.csv', index=False)