### Imports
from collections import Counter
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib import colors

from DiceFunctions import StreamlitStyle as SS, Dice, PlotResults



def main():
    """ """
    ### Set up sidebar
    st.sidebar.title("Game Options")
    players_radio = st.sidebar.radio("Number of Players", [3, 4], index=1)

    pl1 = st.sidebar.beta_container()
    p1c1, _, p1c2 = pl1.beta_columns([7, 1, 2])
    player1 = p1c1.text_input("Player 1", "Player 1")
    color1 = p1c2.color_picker(f"{player1}'s Color", value="#D70404", key="c1")

    pl2 = st.sidebar.beta_container()
    p2c1, _, p2c2 = pl2.beta_columns([7, 1, 2])
    player2 = p2c1.text_input("Player 2", "Player 2")
    color2 = p2c2.color_picker(f"{player2}'s Color", value="#0434E5", key="c2")

    pl3 = st.sidebar.beta_container()
    p3c1, _, p3c2 = pl2.beta_columns([7, 1, 2])
    player3 = p3c1.text_input("Player 3", "Player 3")
    color3 = p3c2.color_picker(f"{player3}'s Color", value="#F76E02", key="c3")

    players = {0: player1, 1: player2, 2: player3}
    player_colors = {0: color1, 1: color2, 2: color3}
    if players_radio == 4:
        pl4 = st.sidebar.beta_container()
        p4c1, _, p4c2 = pl2.beta_columns([7, 1, 2])
        player4 = p4c1.text_input("Player 4", "Player 4")
        color4 = p4c2.color_picker(f"{player4}'s Color", value="#FFFFFF",
                                   key="c4")
        players[3] = player4
        player_colors[3] = color4

    random_rate_slider = st.sidebar.slider("Randomness Parameter", 0., 1., 0.15)
    convergence_rate_slider = st.sidebar.slider("Convergence Rate", 0., 1., 0.5)
    convergence_rate_slider = convergence_rate_slider * 250 + 200
    random_turns_slider = st.sidebar.slider("Starting Random Turns", 1, 32, 8)


    ### Set up main page
    title_text = ("<h1 style='text-align: center; font-size: 4.0em; "
                   "color: gold; background-color: maroon; "
                   "font-family: Georgia;'> CATAN DICE (2) </h1>")
    st.markdown(title_text, unsafe_allow_html=True)

    number_text = st.empty()
    player_name_text = st.empty()
    buttons = st.beta_container()
    stats_cont = st.beta_expander("Game Statistics", False)

    b1, b2, b3 = buttons.beta_columns(3)
    reset_button = b1.button("Reset")
    roll_button = b2.button("Roll!")
    undo_button = b3.button("Undo")
    ###
    trial_button = b2.button("**Roll 50 times**")
    ###

    ### Get cached variables
    roll_history = get_roll_history()
    player_history = get_player_history()
    stats_history = get_statistics_history()


    ### Actions
    if roll_button:
        # Update the player
        if not player_history:
            current_player = 0
        else:
            current_player = int((player_history[-1] + 1) % len(players))
        player_name = players[current_player]
        player_history.append(current_player)

        # Roll the dice
        next_roll = Dice().new_roll(roll_history, list(players.values()),
                                    players[current_player],
                                    random_turns_slider,
                                    random_rate_slider, convergence_rate_slider)
        roll_history.append(next_roll)



    # "Undo" removes last turn from history
    elif undo_button:
        roll_history.pop()
        player_history.pop()

    # "Reset" clears the cache and the history
    elif reset_button:
        st.caching.clear_cache()
        roll_history = player_history = None

    ### Temporary:
    # roll a bunch of times
    elif trial_button:
        n = 50
        if not player_history:
            current_player = 0
        else:
            current_player = int((player_history[-1] + 1) % len(players))
        next_rolls = [Dice().new_roll(roll_history, list(players.values()),
                      players[current_player], random_turns_slider,
                      random_rate_slider, convergence_rate_slider) for _ in
                      range(n)]
        roll_history.extend(next_rolls)
        next_p = (player_history[-1] + 1) % 4 if player_history else 0
        player_history.extend([x % 4 for x in range(next_p, n + next_p)])
    ###




    ### Display name and number (or starting text and image)
    if not roll_history:
        number_text.image(dice_image, use_column_width=True)
        player_name_text.markdown(SS.get_name_text("Roll to start game!"),
                                  unsafe_allow_html=True)
    else:
        number_text.markdown(SS.get_number_text(roll_history[-1]),
                             unsafe_allow_html=True)
        player_name = players[player_history[-1]]
        player_color = player_colors[player_history[-1]]
        player_name_text.markdown(SS.get_name_text(player_name, player_color),
                                  unsafe_allow_html=True)

        ### Game Statistics
        player_names = [players[k] for k in sorted(players)]
        plotter = PlotResults(roll_history, player_names, player_colors)

        stats_cont.markdown("<h2 style='text-align: center; font-size: 1.5em;"
                            "font-family: Arial;'> Turn Count </h2>",
                            unsafe_allow_html=True)
        stats_cont.table(plotter.get_turn_count())
        stats_cont.altair_chart(plotter.get_divergence_chart(),
                                use_container_width=True)
        stats_cont.altair_chart(plotter.player_diff_chart())
        stats_cont.altair_chart(plotter.player_roll_chart())




### Cached Functions
@st.cache(allow_output_mutation=True)
def get_roll_history():
    return []

@st.cache(allow_output_mutation=True)
def get_player_history():
    return []

@st.cache(allow_output_mutation=True)
def get_statistics_history():
    return {}




if __name__ == "__main__":
    dice_image = Image.open("DicePic.png")
    st.set_page_config(page_title="Gambler's Fallacy Dice",
                       page_icon="🎲", layout="centered")
    main()


### Future possible features:
# Freeze statistics and load on button (not blank spac)
# Players get colors: change player's names and plot color
