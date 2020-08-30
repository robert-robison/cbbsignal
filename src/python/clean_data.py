# %%

import pandas as pd 
import numpy as np

from pyprojroot import here


df = pd.read_csv(here("data/all_box_scores.csv"), parse_dates=['date_game'])
# %%

prefs = ['', 'opp_']
fta_coeff = 0.44
for pref in prefs:
    df[f'{pref}possessions'] = df[f'{pref}fga'] + df[f'{pref}tov'] - df[f'{pref}orb'] + fta_coeff * df[f'{pref}fta']

df['avg_possessions'] = df[[f'{pref}possessions' for pref in prefs]].mean(axis=1)
df['efficiency'] = df['pts'] / df['avg_possessions']
df['opp_efficiency'] = df['opp_pts'] / df['avg_possessions']


# %%

win_mask = df['game_result'].str.startswith('W')
rel_cols = ['efficiency', 'fg3', 'fg3a']
for col in rel_cols:
    df[f'{col}_i'] = np.where(win_mask, df[col], df[f'opp_{col}'])
    df[f'{col}_j'] = np.where(win_mask, df[f'opp_{col}'], df[col])

df['team_i'] = np.where(win_mask, df['school'], df['opp_id'])
df['team_j'] = np.where(win_mask, df['opp_id'], df['school'])
df['game_loc_corrected'] = df['game_location'].replace({np.nan: 1, '@': -1, 'N': 0})
df['home_i'] = np.where(win_mask, df['game_loc_corrected'], -1 * df['game_loc_corrected'])
df['orig_win'] = win_mask
keep_cols = [col + suff for col in rel_cols + ['team'] for suff in ['_i', '_j']]
keep_cols += ['home_i', 'date_game', 'year', 'avg_possessions']
final_df = df[keep_cols].drop_duplicates()


# Assign gos to each team
final_df['game_id'] = np.arange(len(final_df))
temp_df = final_df.copy()
temp_df[['team_i', 'team_j']] = temp_df[['team_j', 'team_i']]
temp_df = pd.concat([final_df, temp_df]).sort_values(['year', 'team_i', 'date_game'])
new_team = ((temp_df[['year', 'team_i']] != temp_df[['year', 'team_i']].shift(1)).any(axis=1))#.astype(int).cumsum().values
new_team_inc = np.where(new_team, np.arange(len(temp_df)), np.nan)
temp_df['temp_gos'] = new_team_inc
temp_df['temp_gos'] = temp_df['temp_gos'].fillna(method='ffill')
temp_df['gos'] = np.arange(len(temp_df)) - temp_df['temp_gos']
gos_lookup = temp_df[['team_i', 'gos', 'game_id']].rename(columns={'team_i': 'temp_team'})
final_df = final_df.merge(gos_lookup, left_on=['team_i', 'game_id'], right_on=['temp_team', 'game_id'], how='left').rename(columns={'gos': 'gos_i'})
final_df = final_df.merge(gos_lookup, left_on=['team_j', 'game_id'], right_on=['temp_team', 'game_id'], how='left').rename(columns={'gos': 'gos_j'})

# %%

if final_df['team_i'].dtype == 'object':
    all_teams = np.sort(np.unique(final_df[['team_i', 'team_j']]))
    team_df = pd.DataFrame({
        'team_id': np.arange(len(all_teams)),
        'team_name': all_teams
    })

    for suff in ['i', 'j']:
        final_df = final_df.merge(team_df, left_on=f'team_{suff}', right_on='team_name', how='left').drop(f'team_{suff}', axis=1).rename(columns={'team_id': f'team_{suff}'})

    final_cols = ['efficiency_i', 'efficiency_j', 'fg3_i', 'fg3_j', 'fg3a_i', 'fg3a_j',
        'home_i', 'date_game', 'year', 'avg_possessions', 'game_id',
        'gos_i', 'gos_j', 'team_i', 'team_j']
    final_df = final_df[final_cols]

team_df.to_csv(here("data/ncaa_teams_all.csv"), index=False)

# %%

final_df.to_csv(here('data/ncaa_games_all.csv'), index=False)

# %%
# teams = ['virginia']
# years = [2018]
# mask = ((final_df['team_i'].isin(teams)) | (final_df['team_j'].isin(teams))) & final_df['year'].isin(years)
# final_df[mask].sort_values('date_game').to_csv(here("data/temp_invest.csv"), index=False)

# %%

acc_teams = ['virginia', 'wake-forest', 'duke', 'north-carolina', 'north-carolina-state', 
            'virginia-tech', 'boston-college', 'syracuse', 'florida-state', 'georgia-tech',
            'pittsburgh', 'clemson', 'notre-dame', 'miami-fl', 'louisville']
acc_ids = team_df.loc[team_df['team_name'].isin(acc_teams), 'team_id'].tolist()

acc_conf_mask = (final_df['team_i'].isin(acc_ids)) & (final_df['team_j'].isin(acc_ids))

acc_2018 = final_df[acc_conf_mask & (final_df['year'] == 2018)]

id_map = {acc_id: i for i, acc_id in enumerate(acc_ids)}
acc_2018['team_i'] = acc_2018['team_i'].replace(id_map)
acc_2018['team_j'] = acc_2018['team_j'].replace(id_map)

acc_team_df = team_df[team_df['team_name'].isin(acc_teams)]
acc_team_df = acc_team_df['team_id'].replace(id_map)

acc_2018.to_csv(here("data/acc_games_2018.csv"), index=False)
acc_2018.to_csv(here("data/acc_teams_2018.csv"), index=False)

# %%


