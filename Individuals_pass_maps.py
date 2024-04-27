#!pip install highlight-text
#!#pip install cmasher
from statsbombpy import sb
import pandas as pd
from mplsoccer import Pitch,Sbopen
import matplotlib.pyplot as plt
from PIL import Image
from IPython.display import display
from urllib.request import urlopen
import warnings
import cmasher as cmr
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from highlight_text import ax_text
from mplsoccer import Pitch, VerticalPitch, add_image, FontManager, Sbopen

comps = sb.competitions()
comps['competition_name'].unique()
comps[comps['competition_name']=='UEFA Euro']
matches = sb.matches(competition_id=55, season_id=43)
matches[matches['home_team']=='Italy']

event = sb.events(match_id =3795220)

parser = Sbopen()
events,related,freeze, tactics = parser.event(3795220)
lineup = parser.lineup(3795220)

# df with player_id and subbed off time
time_off = events.loc[(events.type_name == 'Substitution'),
                      ['player_id', 'minute']]
time_off.rename({'minute': 'off'}, axis='columns', inplace=True)
# df with player_id and subbed on time
time_on = events.loc[(events.type_name == 'Substitution'),
                     ['substitution_replacement_id', 'minute']]
time_on.rename({'substitution_replacement_id': 'player_id',
                'minute': 'on'}, axis='columns', inplace=True)
players_on = time_on.player_id
# merge on times subbed on/off
lineup = lineup.merge(time_on, on='player_id', how='left')
lineup = lineup.merge(time_off, on='player_id', how='left')
lineup

# filtering the Italy lineup
# assigning Spain as team 2

team1, team2 = lineup.team_name.unique()  # Italy (team1), Spain (team2)
team = team1
lineup_team = lineup[lineup.team_name == team].copy()

# filter the events to exclude some set pieces
set_pieces = ['Throw-in', 'Free Kick', 'Corner', 'Kick Off', 'Goal Kick']
# for the team pass map
pass_receipts = events[(events.team_name == team) & (events.type_name == 'Ball Receipt')].copy()
# for the player pass maps
passes_excl_throw = events[(events.team_name == team) & (events.type_name == 'Pass') &
                           (events.sub_type_name != 'Throw-in')].copy()

# identify how many players played and how many subs were used
# we will use this in the loop for only plotting pass maps for as
# many players who played
num_players = len(lineup_team)
num_sub = num_players - 11

#pass_receipts
#num_players
#num_sub

# add padding to the top so we can plot the titles, and raise the pitch lines
pitch = Pitch(pad_top=10, line_zorder=2)

# arrow properties for the sub on/off
green_arrow = dict(arrowstyle='simple, head_width=0.7',
                   connectionstyle="arc3,rad=-0.8", fc="green", ec="green")
red_arrow = dict(arrowstyle='simple, head_width=0.7',
                 connectionstyle="arc3,rad=-0.8", fc="red", ec="red")

# a fontmanager object for using a google font
fm_scada = FontManager('https://raw.githubusercontent.com/googlefonts/scada/main/fonts/ttf/'
                       'Scada-Regular.ttf')

SB_LOGO_URL = ('https://raw.githubusercontent.com/statsbomb/open-data/'
               'master/img/SB%20-%20Icon%20Lockup%20-%20Colour%20positive.png')

sb_logo = Image.open(urlopen(SB_LOGO_URL))
spain = Image.open('sp.png')
italy = Image.open('ita.png')


import warnings

# Filtering out some highlight_text warnings - the warnings aren't correct as the
# text fits inside the axes.
warnings.simplefilter("ignore", UserWarning)

# Plot the 7 * 3 grid
fig, axs = pitch.grid(nrows=6, ncols=4, figheight=30,
                      endnote_height=0.03, endnote_space=0,
                      axis=False,
                      title_height=0.08, grid_height=0.84)

# Plot the player pass maps
for idx, ax in enumerate(axs['pitch'].flat):
    # Plot the pass maps up to the total number of players
    if idx < num_players:
        # Filter the complete/incomplete passes for each player excluding throw-ins
        lineup_player = lineup_team.iloc[idx]
        player_id = lineup_player.player_id
        player_pass = passes_excl_throw[passes_excl_throw.player_id == player_id]
        complete_pass = player_pass[player_pass.outcome_name.isnull()]
        incomplete_pass = player_pass[player_pass.outcome_name.notnull()]

        # Plot the arrows
        pitch.arrows(complete_pass.x, complete_pass.y,
                     complete_pass.end_x, complete_pass.end_y,
                     color='#56ae6c', width=2, headwidth=4, headlength=6, ax=ax)
        pitch.arrows(incomplete_pass.x, incomplete_pass.y,
                     incomplete_pass.end_x, incomplete_pass.end_y,
                     color='#7065bb', width=2, headwidth=4, headlength=6, ax=ax)

        # Calculate total passes
        total_pass = len(complete_pass) + len(incomplete_pass)
        if total_pass == 0:
            total_pass = 1  # Ensure denominator is not zero

        # Build annotation string
        annotation_string = (f'{lineup_player.player_name} | '
                             f'<{len(complete_pass)}>/{total_pass} | ')
        if total_pass != 0:
            annotation_string += f'{round(100 * len(complete_pass) / total_pass, 1)}%'

        # Add annotation to the plot
        ax_text(0, -5, annotation_string, ha='left', va='center', fontsize=13,
                fontproperties=fm_scada.prop,  # using the font manager for the Google font
                highlight_textprops=[{"color": '#56ae6c'}], ax=ax)

        # Add information for substitutions on/off and arrows
        if not np.isnan(lineup_team.iloc[idx].off):
            ax.text(116, -10, str(lineup_team.iloc[idx].off.astype(int)), fontsize=20,
                    fontproperties=fm_scada.prop,
                    ha='center', va='center')
            ax.annotate('', (120, -2), (112, -2), arrowprops=red_arrow)
        if not np.isnan(lineup_team.iloc[idx].on):
            ax.text(104, -10, str(lineup_team.iloc[idx].on.astype(int)), fontsize=20,
                    fontproperties=fm_scada.prop,
                    ha='center', va='center')
            ax.annotate('', (108, -2), (100, -2), arrowprops=green_arrow)

# Plot on the last Pass Map
# (Note ax=ax as we have cycled through to the last axes in the loop)
pitch.kdeplot(x=pass_receipts.x, y=pass_receipts.y, ax=ax,
              cmap=cmr.lavender,
              levels=100,
              thresh=0, fill=True)
ax.text(0, -5, f'{team}: Pass Receipt Heatmap', ha='left', va='center',
        fontsize=20, fontproperties=fm_scada.prop)

# Remove unused axes (if any)
for ax in axs['pitch'].flat[11 + num_sub:-1]:
    ax.remove()

# Endnote text
axs['endnote'].text(0, 0.5, 'Grid format: @DymondFormation',
                    fontsize=20, fontproperties=fm_scada.prop, va='center', ha='left')

# Add image
ax_sb_logo = add_image(sb_logo, fig, left=0.701126,
                       # Set the bottom and height to align with the endnote
                       bottom=axs['endnote'].get_position().y0,
                       height=axs['endnote'].get_position().height)

# Title text
axs['title'].text(0.5, 0.65, f'{team1} Pass Maps vs {team2}', fontsize=40,
                  fontproperties=fm_scada.prop, va='center', ha='center')
SUB_TEXT = ('Player Pass Maps: exclude throw-ins only\n'
            'Team heatmap: includes all attempted pass receipts')
axs['title'].text(0.5, 0.35, SUB_TEXT, fontsize=20,
                  fontproperties=fm_scada.prop, va='center', ha='center')

# Plot logos (same height as the title_ax)
# Set the Italy flag to align with the left/bottom of the title axes
ax_italy_logo = add_image(italy, fig,
                          left=axs['title'].get_position().x0,
                          bottom=axs['title'].get_position().y0,
                          height=axs['title'].get_position().height)
# Set the Spain flag to align with the right/bottom of the title axes
ax_spain_logo = add_image(spain, fig, left=0.8521,
                          bottom=axs['title'].get_position().y0,
                          height=axs['title'].get_position().height)

