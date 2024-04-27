#!pip install -U mplsoccer
#!pip install statsbombpy

from statsbombpy import sb
import pandas as pd
from mplsoccer import Pitch,Sbopen
import matplotlib.pyplot as plt

comps = sb.competitions()
comps['competition_name'].unique()

comps[comps['competition_name']=='African Cup of Nations']

matches = sb.matches(competition_id=1267, season_id=107)
matches[matches['home_team']=='Nigeria']

event = sb.events(match_id=3923881)

parser = Sbopen()
df, related,freeze,tactics = parser.event(3923881)

df = df[df['team_name']=='Nigeria']

df['type_name'].unique()

passes = df[df['type_name']=='Pass']
passes = passes[['id','minute','player_id','player_name','x','y','end_x', 'end_y','pass_recipient_id','pass_recipient_name','outcome_id','outcome_name']]


passes['outcome_name'].unique()
successful = passes[passes['outcome_name'].isnull()]

subs = df[df['type_name']=='Substitution']
subs = subs['minute']
firstSub= subs.min()

successful = successful[successful['minute']<firstSub]

df_lineup = parser.lineup(3923881)
jersey_data =df_lineup[['player_id','jersey_number']]

successful = pd.merge(successful,jersey_data,on='player_id')
successful.rename(columns={'jersey_number':'passer'},inplace=True)

jersey_data.rename(columns={'player_id':'pass_recipient_id'},inplace=True)
successful = pd.merge(successful,jersey_data,on='pass_recipient_id')
successful.rename(columns={'jersey_number':'recipient'},inplace=True)

average_locations = successful.groupby('passer').agg({'x':['mean'],'y':['mean','count']})
average_locations.columns = ['x','y','count']

pass_between = successful.groupby(['passer','recipient']).id.count().reset_index()
pass_between.rename(columns={'id':'pass_count'},inplace=True)

pass_between = pd.merge(pass_between, average_locations,on='passer')

average_locations=average_locations.rename_axis('recipient')
pass_between = pd.merge(pass_between, average_locations,on='recipient',suffixes=['','_end'])
pass_between = pass_between[pass_between['pass_count']>1]
pass_between.head()

pitch = Pitch(pitch_color='#aabb97', line_color='white',
              stripe_color='#c2d59d', stripe=True)  

fig,ax = pitch.draw(figsize=(8,6))

#Draw arrows and nodes
pass_lines = pitch.lines(1.2*pass_between.x, 0.8*pass_between.y,
                         1.2*pass_between.x_end, 0.8*pass_between.y_end, lw=pass_between.pass_count*0.5,
                         color='red', zorder=1, ax=ax)

nodes = pitch.scatter(1.2*average_locations.x,0.8*average_locations.y,s=20*average_locations['count'].values,color='white',edgecolors='#a6aab3',linewidth=1,ax=ax)


# Put jersey number in the nodes

for index,row in average_locations.iterrows():
    pitch.annotate(index,xy=(1.2*row.x,0.8*row.y),c='#161A30', fontweight='bold',va='center',ha='center',size=8, ax=ax)

    
ax.set_title('Nigeria vs Ghana',color='red',va='center',ha='center',fontsize=12,fontweight='bold',pad=20)

ax.annotate('African Cup of Nations Final', xy=(0.5, 1), xytext=(0, 0),
             xycoords='axes fraction', textcoords='offset points',
             fontsize=10, color='#0E2954', va='top', ha='center')

ax.text(102, 85, '@PassMapProject', color='#0E2959', va='bottom', ha='center', fontsize=10)
plt.show()

