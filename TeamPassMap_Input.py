from statsbombpy import sb
import pandas as pd
from mplsoccer import Pitch, Sbopen
import matplotlib.pyplot as plt

# Prompt the user for competition_id, season_id, and home_team
competition_id = input("Enter competition_id: ")
season_id = input("Enter season_id: ")
home_team = input("Enter home_team: ")

# Convert competition_id and season_id to integers
competition_id = int(competition_id)
season_id = int(season_id)

comps = sb.competitions()
competition_name = comps[(comps['competition_id'] == competition_id) & (comps['season_id'] == season_id)]['competition_name'].iloc[0]

matches = sb.matches(competition_id=competition_id, season_id=season_id)
matches = matches[matches['home_team'] == home_team]

# Assuming there's at least one match
match_id = matches.iloc[0]['match_id']

event = sb.events(match_id=match_id)

parser = Sbopen()
df, related, freeze, tactics = parser.event(match_id)

df = df[df['team_name'] == home_team]

df['type_name'].unique()

passes = df[df['type_name'] == 'Pass']
passes = passes[['id', 'minute', 'player_id', 'player_name', 'x', 'y', 'end_x', 'end_y', 'pass_recipient_id',
                 'pass_recipient_name', 'outcome_id', 'outcome_name']]

passes['outcome_name'].unique()
successful = passes[passes['outcome_name'].isnull()]

subs = df[df['type_name'] == 'Substitution']
subs = subs['minute']
firstSub = subs.min()

successful = successful[successful['minute'] < firstSub]

df_lineup = parser.lineup(match_id)
jersey_data = df_lineup[['player_id', 'jersey_number']]

successful = pd.merge(successful, jersey_data, on='player_id')
successful.rename(columns={'jersey_number': 'passer'}, inplace=True)

jersey_data.rename(columns={'player_id': 'pass_recipient_id'}, inplace=True)
successful = pd.merge(successful, jersey_data, on='pass_recipient_id')
successful.rename(columns={'jersey_number': 'recipient'}, inplace=True)

average_locations = successful.groupby('passer').agg({'x': ['mean'], 'y': ['mean', 'count']})
average_locations.columns = ['x', 'y', 'count']

pass_between = successful.groupby(['passer', 'recipient']).id.count().reset_index()
pass_between.rename(columns={'id': 'pass_count'}, inplace=True)

pass_between = pd.merge(pass_between, average_locations, on='passer')

average_locations = average_locations.rename_axis('recipient')
pass_between = pd.merge(pass_between, average_locations, on='recipient', suffixes=['', '_end'])
pass_between = pass_between[pass_between['pass_count'] > 1]

pitch = Pitch(pitch_color='#aabb97', line_color='white',
              stripe_color='#c2d59d', stripe=True)

fig, ax = pitch.draw(figsize=(8, 6))

# Draw arrows and nodes
pass_lines = pitch.lines(1.2 * pass_between.x, 0.8 * pass_between.y,
                         1.2 * pass_between.x_end, 0.8 * pass_between.y_end, lw=pass_between.pass_count * 0.5,
                         color='red', zorder=1, ax=ax)

nodes = pitch.scatter(1.2 * average_locations.x, 0.8 * average_locations.y, s=20 * average_locations['count'].values,
                      color='white', edgecolors='#a6aab3', linewidth=1, ax=ax)

# Put jersey number in the nodes
for index, row in average_locations.iterrows():
    pitch.annotate(index, xy=(1.2 * row.x, 0.8 * row.y), c='#161A30', fontweight='bold', va='center', ha='center',
                    size=8, ax=ax)

ax.set_title(f'{home_team} Pass Map', color='red', va='center', ha='center', fontsize=12, fontweight='bold', pad=20)

ax.annotate(f'{competition_name}', xy=(0.5, 1), xytext=(0, 0),
             xycoords='axes fraction', textcoords='offset points',
             fontsize=10, color='#0E2954', va='top', ha='center')

ax.text(102, 85, '@PassMapProject', color='#0E2959', va='bottom', ha='center', fontsize=10)

plt.show()
