import streamlit as st
import pandas as pd
from PIL import Image
import os
from fuzzywuzzy import process

# --- Load CSV ---
data = pd.read_csv('pokemon.csv')

# --- Filter out 'Mega' Pokémon ---
substring = r'\bMega\b'
filter = data['Name'].str.contains(substring, regex=True)
data = data[~filter].reset_index(drop=True)

# --- Lists for stats ---
allpokemon = data['Name'].tolist()
pokemonhp = data['HP'].tolist()
pokemonattack = data['Attack'].tolist()
pokemondefence = data['Defence'].tolist()
pokemonspeed = data['Speed'].tolist()

st.title("Pokédex")

# --- Initialize session_state ---
if "current" not in st.session_state:
    st.session_state.current = 1  # Pokémon number
if "search_index" not in st.session_state:
    st.session_state.search_index = 0
if "filtered_indices" not in st.session_state:
    st.session_state.filtered_indices = []

# --- Search input ---
search_input = st.text_input("Enter Pokémon number or name:")

current_index = None

if search_input:
    # Check if input is a number
    if search_input.isdigit():
        idx = int(search_input)
        if 1 <= idx <= len(allpokemon):
            current_index = idx
        else:
            st.warning("Index out of range!")
    else:
        # Fuzzy search (allow slight spelling errors)
        matches = process.extract(search_input, allpokemon, limit=10)
        filtered_indices = [allpokemon.index(match[0]) + 1 for match in matches if match[1] >= 80]
        if filtered_indices:
            st.session_state.filtered_indices = filtered_indices
            current_index = filtered_indices[st.session_state.search_index]
        else:
            st.warning("No Pokémon found!")
            current_index = None
else:
    st.session_state.filtered_indices = []
    current_index = st.session_state.current

# --- Next / Previous buttons ---
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Previous"):
        if st.session_state.filtered_indices:
            st.session_state.search_index = max(0, st.session_state.search_index - 1)
            current_index = st.session_state.filtered_indices[st.session_state.search_index]
        else:
            st.session_state.current = max(1, st.session_state.current - 1)
            current_index = st.session_state.current
with col2:
    if st.button("Next"):
        if st.session_state.filtered_indices:
            st.session_state.search_index = min(len(st.session_state.filtered_indices)-1,
                                                st.session_state.search_index + 1)
            current_index = st.session_state.filtered_indices[st.session_state.search_index]
        else:
            st.session_state.current = min(len(allpokemon), st.session_state.current + 1)
            current_index = st.session_state.current

# --- Display Pokémon ---
if current_index is not None:
    userpokemon = current_index
    list_index = userpokemon - 1  # Correct for list indexing

    # Determine folder for image
    if 1 <= userpokemon <= 151:
        folder = 'red-blue'
    elif 152 <= userpokemon <= 251:
        folder = 'gold'
    elif 252 <= userpokemon <= 386:
        folder = 'ruby-sapphire'
    elif 387 <= userpokemon <= 492:
        folder = 'diamond-pearl'
    elif 493 <= userpokemon <= 649:
        folder = 'black-white'
    else:
        folder = None

    if folder and allpokemon[list_index]:
        st.subheader(f"{userpokemon}: {allpokemon[list_index]}")
        st.write(
            f"HP: {pokemonhp[list_index]}  |  "
            f"Attack: {pokemonattack[list_index]}  |  "
            f"Defence: {pokemondefence[list_index]}  |  "
            f"Speed: {pokemonspeed[list_index]}"
        )

        # Display image with transparency handled
        img_path = os.path.join(folder, f"{userpokemon}.png")
        try:
            img = Image.open(img_path).convert("RGBA")
            bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
            bg.paste(img, (0, 0), img)
            st.image(bg, width=200)  # Adjust width here
        except FileNotFoundError:
            st.warning(f"Image not found in {folder}!")
