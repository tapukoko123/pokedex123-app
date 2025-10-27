import streamlit as st
import pandas as pd
from PIL import Image
import os
from fuzzywuzzy import process

# --- Unlock Pokédex ---
if "count" in st.session_state and st.session_state.count >= 4:
    st.session_state.pokedex_unlocked = True

if "pokedex_unlocked" not in st.session_state or not st.session_state.pokedex_unlocked:
    st.title("🔒 Pokédex Locked")
    st.warning("You need 4 correct answers in the Anagram Game to unlock the Pokédex!")
    if "count" in st.session_state:
        st.write(f"Current score: {st.session_state.count}/4")
    st.stop()

# --- Load CSVs ---
data = pd.read_csv("pokemon.csv")
data2 = pd.read_csv("pokemon2.csv")

# --- Normalize columns ---
data.columns = data.columns.str.strip()
data2.columns = data2.columns.str.strip()
data["Name"] = data["Name"].astype(str).str.strip()
if "Name" in data2.columns:
    data2["Name"] = data2["Name"].astype(str).str.strip()

# --- Detect description column ---
desc_col = next((col for col in data2.columns if "desc" in col.lower()), None)
if desc_col is None:
    st.error("No description column found in pokemon2.csv.")
    st.write("Columns found:", data2.columns.tolist())
    st.stop()

# --- Filter out Mega Pokémon ---
data_filtered = data[~data["Name"].str.contains(r"\bMega\b", regex=True, na=False)].reset_index(drop=True)

# --- Extract lists ---
allpokemon = data_filtered["Name"].tolist()
pokemonhp = data_filtered.get("HP", pd.Series([None]*len(allpokemon))).tolist()
pokemonattack = data_filtered.get("Attack", pd.Series([None]*len(allpokemon))).tolist()
pokemondefence = data_filtered.get("Defence", pd.Series([None]*len(allpokemon))).tolist()
pokemonspeed = data_filtered.get("Speed", pd.Series([None]*len(allpokemon))).tolist()

# --- Session state setup ---
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "filtered_indices" not in st.session_state:
    st.session_state.filtered_indices = []
if "search_index" not in st.session_state:
    st.session_state.search_index = 0

# --- Search form (Enter works) ---
with st.form("search_form"):
    search_input = st.text_input("Enter Pokémon number or name:")
    if st.form_submit_button("Search"):
        if search_input.isdigit():
            idx = int(search_input) - 1
            if 0 <= idx < len(allpokemon):
                st.session_state.current_index = idx
                st.session_state.filtered_indices = []
            else:
                st.warning("Number out of range!")
        else:
            matches = process.extract(search_input, allpokemon, limit=10)
            found = [allpokemon.index(m[0]) for m in matches if m[1] >= 75]
            if found:
                st.session_state.filtered_indices = found
                st.session_state.search_index = 0
                st.session_state.current_index = found[0]
            else:
                st.warning("No Pokémon found.")

# --- Navigation buttons ---
col1, col2 = st.columns(2)
with col1:
    if st.button("Previous"):
        if st.session_state.filtered_indices:
            st.session_state.search_index = max(0, st.session_state.search_index - 1)
            st.session_state.current_index = st.session_state.filtered_indices[st.session_state.search_index]
        else:
            st.session_state.current_index = max(0, st.session_state.current_index - 1)

with col2:
    if st.button("Next"):
        if st.session_state.filtered_indices:
            st.session_state.search_index = min(len(st.session_state.filtered_indices) - 1,
                                                st.session_state.search_index + 1)
            st.session_state.current_index = st.session_state.filtered_indices[st.session_state.search_index]
        else:
            st.session_state.current_index = min(len(allpokemon) - 1, st.session_state.current_index + 1)

# --- Slider ---
def on_slider_change():
    st.session_state.current_index = st.session_state.slider_val - 1
    st.session_state.filtered_indices = []

st.slider(
    "Jump to Pokémon:",
    1, len(allpokemon),
    st.session_state.current_index + 1,
    key="slider_val",
    on_change=on_slider_change
)

# --- Display Pokémon ---
index = st.session_state.current_index
pokemon_name = allpokemon[index]
userpokemon = index + 1

# --- Region and folder ---
if 1 <= userpokemon <= 151:
    folder, region = "red-blue", "Kanto"
elif 152 <= userpokemon <= 251:
    folder, region = "gold", "Johto"
elif 252 <= userpokemon <= 386:
    folder, region = "ruby-sapphire", "Hoenn"
elif 387 <= userpokemon <= 492:
    folder, region = "diamond-pearl", "Sinnoh"
elif 493 <= userpokemon <= 649:
    folder, region = "black-white", "Unova"
elif 650 <= userpokemon <= 721:
    folder, region = "x-y", "Kalos"
elif 722 <= userpokemon <= 809:
    folder, region = "sun-moon", "Alola"
elif 810 <= userpokemon <= 898:
    folder, region = "sword-shield", "Galar"
elif 899 <= userpokemon <= 905:
    folder, region = "sword-shield", "Hisui"    
elif 906 <= userpokemon <= len(allpokemon):
    folder, region = "scarlet-violet", "Paldea"
else:
    folder, region = None, "Unknown"

# --- Show Pokémon info ---
st.subheader(f"{userpokemon}: {pokemon_name}")
st.caption(f"Region: {region}")

st.write(
    f"**HP:** {pokemonhp[index]}  |  "
    f"**Attack:** {pokemonattack[index]}  |  "
    f"**Defence:** {pokemondefence[index]}  |  "
    f"**Speed:** {pokemonspeed[index]}"
)

# --- Description by row number ---
if index < len(data2):
    desc = data2.iloc[index][desc_col]
    if pd.isna(desc):
        desc = "No description available"
else:
    desc = "No description available"

st.markdown(f"**Description:** {desc}")

# --- Image ---
if folder:
    img_path = os.path.join(folder, f"{userpokemon}.png")
    if os.path.exists(img_path):
        img = Image.open(img_path).convert("RGBA")
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        bg.paste(img, (0, 0), img)
        st.image(bg, width=250)
    else:
        st.info(f"No image found for {pokemon_name} in {folder}/")
else:
    st.info("Region folder not found.")
