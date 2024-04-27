from statsbombpy import sb
import pandas as pd
from mplsoccer import Pitch, add_image, FontManager
from PIL import Image
from urllib.request import urlopen
import warnings
import cmasher as cmr
import numpy as np
from highlight_text import ax_text
from mplsoccer import Sbopen
import matplotlib.pyplot as plt  # Import plt module from matplotlib

def plot_pass_maps(home_team, away_team, events, lineup):
    """Plot pass maps for the given match."""
 
    # Add padding to the top so we can plot the titles, and raise the pitch lines
    pitch = Pitch(pad_top=10, line_zorder=2)

    # Arrow properties for the sub on/off
    green_arrow = dict(arrowstyle='simple, head_width=0.7',
                       connectionstyle="arc3,rad=-0.8", fc="green", ec="green")
    red_arrow = dict(arrowstyle='simple, head_width=0.7',
                     connectionstyle="arc3,rad=-0.8", fc="red", ec="red")

    # Font manager object for using a Google font
    fm_scada = FontManager('https://raw.githubusercontent.com/googlefonts/scada/main/fonts/ttf/'
                           'Scada-Regular.ttf')

    # URL for the StatsBomb logo
    SB_LOGO_URL = ('https://raw.githubusercontent.com/statsbomb/open-data/'
                   'master/img/SB%20-%20Icon%20Lockup%20-%20Colour%20positive.png')

    # Load images for Italy and Spain flags
    sb_logo = Image.open(urlopen(SB_LOGO_URL))
    #spain = Image.open('sp.png')
    #italy = Image.open('ita.png')

    # Filtering out some highlight_text warnings
    warnings.simplefilter("ignore", UserWarning)

    # Plot the 7 * 3 grid
    fig, axs = pitch.grid(nrows=7, ncols=4, figheight=30,
                          endnote_height=0.03, endnote_space=0,
                          axis=False,
                          title_height=0.08, grid_height=0.84)

    # Plot the player pass maps
    for idx, ax in enumerate(axs['pitch'].flat):
        # Plot the pass maps up to the total number of players
        if idx < len(lineup):
            # Filter the complete/incomplete passes for each player excluding throw-ins
            lineup_player = lineup.iloc[idx]
            player_id = lineup_player.player_id
            player_pass = events[(events.player_id == player_id) & (events.type_name == 'Pass') &
                                 (events.sub_type_name != 'Throw-in')]
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
            if not pd.isna(lineup_player.get('off')):
                ax.text(116, -10, str(lineup_player.off.astype(int)), fontsize=20,
                        fontproperties=fm_scada.prop,
                        ha='center', va='center')
                ax.annotate('', (120, -2), (112, -2), arrowprops=red_arrow)
            if not pd.isna(lineup_player.get('on')):
                ax.text(104, -10, str(lineup_player.on.astype(int)), fontsize=20,
                        fontproperties=fm_scada.prop,
                        ha='center', va='center')
                ax.annotate('', (108, -2), (100, -2), arrowprops=green_arrow)

    # Plot on the last Pass Map
    # (Note ax=ax as we have cycled through to the last axes in the loop)
    pitch.kdeplot(x=events[events.type_name == 'Ball Receipt'].x, 
                  y=events[events.type_name == 'Ball Receipt'].y, ax=ax,
                  cmap=cmr.lavender,
                  levels=100,
                  thresh=0, fill=True)
    ax.text(0, -5, f'{home_team}: Pass Receipt Heatmap', ha='left', va='center',
            fontsize=20, fontproperties=fm_scada.prop)

    # Remove unused axes (if any)
    for ax in axs['pitch'].flat[len(lineup):]:
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
    axs['title'].text(0.5, 0.65, f'{home_team} Pass Maps vs {away_team}', fontsize=40,
                      fontproperties=fm_scada.prop, va='center', ha='center')
    SUB_TEXT = ('Player Pass Maps: exclude throw-ins only\n'
                'Team heatmap: includes all attempted pass receipts')
    axs['title'].text(0.5, 0.35, SUB_TEXT, fontsize=20,
                      fontproperties=fm_scada.prop, va='center', ha='center')

    # Plot badge/flag (same height as the title_ax)
    # Set the Italy flag to align with the left/bottom of the title axes
    #ax_italy_logo = add_image(italy, fig,
                            #  left=axs['title'].get_position().x0,
                             # bottom=axs['title'].get_position().y0,
                             # height=axs['title'].get_position().height)
    # Set the Spain flag to align with the right/bottom of the title axes
    #ax_spain_logo = add_image(spain, fig, left=0.8521,
                             # bottom=axs['title'].get_position().y0,
                             # height=axs['title'].get_position().height)

def get_user_input():
    """Get user input for competition, season, and home team."""
    competition_id = input("Enter the competition ID: ")
    season_id = input("Enter the season ID: ")
    home_team = input("Enter the home team name: ")
    return competition_id, season_id, home_team

# Get user input
competition_id, season_id, home_team = get_user_input()

# Get all matches involving the home team
matches = sb.matches(competition_id=int(competition_id), season_id=int(season_id))
home_matches = matches[(matches['home_team'] == home_team) | (matches['away_team'] == home_team)]

# Loop through each match and plot pass maps
for index, match in home_matches.iterrows():
    match_id = match['match_id']
    away_team = match['away_team']
    # Retrieve events, lineup, and other necessary data for the current match
    parser = Sbopen()
    events, related, freeze, tactics = parser.event(match_id=int(match_id))
    lineup = parser.lineup(match_id=int(match_id))
    # Plot pass maps for the current match
    plot_pass_maps(home_team, away_team, events, lineup)
