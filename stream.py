#!/usr/bin/env python3
import pandas as pd
import random
import streamlit as st
from PIL import Image
import os

# --- Load Pokémon data ---
data1 = pd.read_csv('FirstGenPokemon.csv')
# Use row index + 1 as Pokémon index to match image files
allpokemon1 = [[i + 1, name] for i, name in enumerate(data1[' Name'].tolist())]

# --- Function to scramble letters ---
def scramble_word_lower(word):
    letters = list(word)
    while True:
        random.shuffle(letters)
        scrambled = ''.join(letters)
        if scrambled.lower() != word.lower() and scrambled.strip() != "":
            return scrambled

# --- Session state setup ---
if "pokemon" not in st.session_state:
    st.session_state.pokemon = random.choice(allpokemon1)  # [index, name]
    st.session_state.scrambled = scramble_word_lower(st.session_state.pokemon[1])
    st.session_state.count = 0
    st.session_state.message = ""
    st.session_state.show_clue_image = False  # Show image as clue after first wrong guess
    st.session_state.show_answer_image = False  # Show image with answer reveal
    st.session_state.last_pokemon = None  # Store the previous Pokémon for answer image
    st.session_state.attempts = 0  # Track attempts for current Pokémon

st.title("Pokémon Anagram Game")
st.write("Guess the Pokémon from this anagram:")
st.write(f"**{st.session_state.scrambled}**")

# --- Show clue image if first guess was wrong ---
if st.session_state.show_clue_image:
    current_index = st.session_state.pokemon[0]
    current_name = st.session_state.pokemon[1]
    image_path = os.path.join("red-blue", f"{current_index}.png")
    
    st.write("Here's a clue:")
    if os.path.exists(image_path):
        img = Image.open(image_path)
        st.image(img, width=200)
    else:
        st.write(f"❌ Image not found at: {image_path}")

# --- Form to handle Enter key properly ---
with st.form(key="guess_form", clear_on_submit=True):
    guess = st.text_input("Your guess:", key="guess_input")
    submit_button = st.form_submit_button("Submit")

# --- Check guess when form is submitted (Enter or Submit button) ---
if submit_button and guess:
    correct_name = st.session_state.pokemon[1]
    correct_index = st.session_state.pokemon[0]
    st.session_state.attempts += 1
    
    if guess.lower() == "quit":
        st.session_state.message = "Thanks for playing!"
        st.session_state.show_clue_image = False
        st.session_state.show_answer_image = False
    elif guess.lower() == correct_name.lower():
        st.session_state.count += 1
        st.session_state.message = f"✅ Correct! It was {correct_name}."
        st.session_state.show_answer_image = True
        st.session_state.show_clue_image = False
        st.session_state.last_pokemon = [correct_index, correct_name]
        # Pick next Pokémon
        st.session_state.pokemon = random.choice(allpokemon1)
        st.session_state.scrambled = scramble_word_lower(st.session_state.pokemon[1])
        st.session_state.attempts = 0
        st.rerun()
    else:
        # First wrong guess - show clue image
        if st.session_state.attempts == 1:
            st.session_state.message = f"❌ Incorrect! Try again with this clue:"
            st.session_state.show_clue_image = True
            st.rerun()
        # Second wrong guess - reveal answer and move to next
        else:
            st.session_state.message = f"❌ Oops! The correct answer was {correct_name}."
            st.session_state.show_answer_image = True
            st.session_state.show_clue_image = False
            st.session_state.last_pokemon = [correct_index, correct_name]
            # Pick next Pokémon
            st.session_state.pokemon = random.choice(allpokemon1)
            st.session_state.scrambled = scramble_word_lower(st.session_state.pokemon[1])
            st.session_state.attempts = 0
            st.rerun()

# --- Display messages and score ---
st.write(st.session_state.message)
st.write(f"Your running total of correct anagrams: {st.session_state.count}")

if st.session_state.count > 2:
    st.write("🎉 Well done — keep going!")
if st.session_state.count > 3:
    st.write("🏆 As a prize, you receive a Pokédex!")

# --- Display answer image after correct guess or giving up ---
if st.session_state.show_answer_image and st.session_state.last_pokemon:
    image_index = st.session_state.last_pokemon[0]
    image_name = st.session_state.last_pokemon[1]
    image_path = os.path.join("red-blue", f"{image_index}.png")
    
    if os.path.exists(image_path):
        img = Image.open(image_path)
        st.image(img, caption=image_name)
    else:
        st.write(f"❌ Image not found at: {image_path}")