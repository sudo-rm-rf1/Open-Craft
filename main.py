import dbm
from datetime import datetime

from flask import Flask, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import os

import emoji

from guidance import models, gen

MAX_RETRIES = 5

MODEL_PATH = input("Enter path to model file: ")

llm = models.LlamaCpp(MODEL_PATH, echo=False)
emoji_dedicated_llm = models.LlamaCpp(MODEL_PATH, echo=False)

class Formula:
    first_ingredient: str
    second_ingredient: str
    result: str
    emoji: str

    def __init__(self, first, second, result):
        first_ingredient, second_ingredient = sorted([first, second])
        self.first_ingredient = first_ingredient
        self.second_ingredient = second_ingredient
        self.result = result
        self.emoji = ""

    def __str__(self):
        return f'{self.first_ingredient} + {self.second_ingredient} = {self.result}'

base_formulas = [
    Formula('air', 'fire', 'energy'),
    Formula('air', 'water', 'rain'),
    Formula('air', 'earth', 'dust'),
    Formula('air', 'air', 'wind'),

    Formula('water', 'fire', 'steam'),
    Formula('water', 'water', 'sea'),
    Formula('water', 'earth', 'mud'),

    Formula('fire', 'fire', '!NONSENSICAL!'),
    Formula('fire', 'earth', 'lava'),

    Formula('earth', 'earth', 'pressure'),
]

secondary_formulas = [
    Formula('mud', 'fire', 'brick'),
    Formula('lava', 'water', 'stone'),
    Formula('rain', 'fire', 'sun'),
    Formula('air', 'steam', 'cloud'),
    Formula('fire', 'dust', 'gunpowder'),
    Formula('mud', 'wind', '!NONSENSICAL!'),
    Formula('lava', 'lava', 'volcano'),
    Formula('sun', 'dust', '!NONSENSICAL!'),
    Formula('water', 'brick', '!NONSENSICAL!'),
    Formula('brick', 'cloud', '!NONSENSICAL!'),
    Formula('brick', 'brick', 'wall'),
    Formula('wall', 'wall', 'house'),
    Formula('house', 'house', 'village'),
    Formula('village', 'village', 'city'),
    Formula('city', 'city', 'country'),
    Formula('country', 'country', 'planet'),
    Formula('sea', 'sea', 'ocean'),
]

whatever_formulas = [
    Formula('planet', 'planet', 'solar system'),
    Formula('earth', 'life', 'human'),
    Formula('electricity', 'primordial soup', 'life'),
    Formula('life', 'land', 'animal'),
    Formula('life', 'death', 'organic matter'),
    Formula('bird', 'metal', 'airplane'),
    Formula('fire', 'stone', 'metal'),
]

formulas = [*base_formulas, *secondary_formulas, *whatever_formulas]

def make_emoji(word):
    prompt = ""
    prompt += "Emoji for water: 💧\n"
    prompt += "Emoji for fire: 🔥\n"
    prompt += "Emoji for air: 🌬️\n"
    prompt += "Emoji for earth: 🌍\n"
    prompt += "Emoji for energy: ⚡\n"
    prompt += "Emoji for rain: 🌧️\n"
    prompt += "Emoji for cloud: ☁\n"
    prompt += "Emoji for martial arts: 🥋\n"
    query = emoji_dedicated_llm + prompt + f"Emoji for {word}: "
    result = query + gen(stop_regex=r"\s", max_tokens=10, name="emoji")
    try:
        res_emoji = result['emoji']
    except KeyError:
        last_try_at_emoji = str(result).split("\n")[-1].split(":")[-1].strip()
        if len(list(emoji.analyze(last_try_at_emoji, join_emoji=False))) > 0:
            res_emoji = last_try_at_emoji
        else:
            return "❔"
    try:
        emoji_only = next(emoji.analyze(res_emoji, join_emoji=False))
        emoji_only = emoji_only.value
        if type(emoji_only) != str:
            emoji_only = emoji_only.emoji
    except StopIteration:
        return "❔"
    return emoji_only

def existing_emoji_or_generate(emoji_db, word):
    if word in emoji_db:
        return emoji_db[word]
    emoji = make_emoji(word)
    emoji_db[word] = emoji
    return emoji

def prepare_combination_query():
    init_prompt = 'Formulas, dictionary, recipes, alchemy, chemistry, combinations, crafting, NONSENSICAL. <ingredient> + <ingredient> = <combination but different>. Offensive terms allowed.'
    examples = '\n'.join(str(f) for f in formulas)
    prepared = llm + f"{init_prompt}\nExamples:\n{examples}\nReal combinations:\n"
    return prepared

PREPARED_COMBINATION_QUERY = prepare_combination_query()

def gen_combination(first, second):
    first_ingredient, second_ingredient = sorted([first, second])

    query = f'{first_ingredient} + {second_ingredient} = '
    prepared = PREPARED_COMBINATION_QUERY

    retries = MAX_RETRIES
    combination = ''
    while (combination == first_ingredient or combination == second_ingredient or combination == '') and retries > 0:
        temp = 1/retries*2.5
        res = prepared + query + gen(regex=r"([a-z \-]+|!NONSENSICAL!)", max_tokens=10, stop_regex=r"\n", name="combination", temperature=temp)
        combination = res['combination']
        retries -= 1

    if combination == first_ingredient or combination == second_ingredient:
        return combination, MAX_RETRIES - retries
    if combination == '!NONSENSICAL!':
        print("NONSENSICAL!", first, second)
        return None, 0
    return combination, MAX_RETRIES - retries

def try_combo(first, second):
    combo, tries = gen_combination(first, second)
    return f"{first} + {second} = {combo} ({tries} tries)"

def existing_or_generate(ingredient_db, combo_db, first, second):
    first_ingredient, second_ingredient = sorted([first, second])
    first_discovery = False
    if not first_ingredient in ingredient_db:
        print(f"Ingredient {first_ingredient} not in db")
        return None, first_discovery
    if not second_ingredient in ingredient_db:
        print(f"Ingredient {second_ingredient} not in db")
        return None, first_discovery
    if f'{first_ingredient} + {second_ingredient}' in combo_db:
        combo = combo_db[f'{first_ingredient} + {second_ingredient}']
        if type(combo) == bytes:
            combo = combo.decode()
        if combo == '!NONSENSICAL!':
            print("NONSENSICAL!", first_ingredient, second_ingredient)
            return None, first_discovery
        return combo, first_discovery
    combo, tries = gen_combination(first, second)
    if combo is not None:
        if combo not in ingredient_db:
            first_discovery = True
        combo_db[f'{first_ingredient} + {second_ingredient}'] = combo
        ingredient_db[combo] = '1'
    else:
        combo_db[f'{first_ingredient} + {second_ingredient}'] = '!NONSENSICAL!'

    return combo, first_discovery

def prepare_db(ingredient_db, combo_db):
    for formula in formulas:
        ingredient_db[formula.first_ingredient] = '1'
        ingredient_db[formula.second_ingredient] = '1'
        ingredient_db[formula.result] = '1'
    for formula in formulas:
        if f'{formula.first_ingredient} + {formula.second_ingredient}' in combo_db:
            continue
        combo_db[f'{formula.first_ingredient} + {formula.second_ingredient}'] = formula.result
app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["2000 per day", "400 per hour"],
    storage_uri="memory://",
)

ingredient_db = {}
combos_db = {}
emoji_db = {}

@app.get('/')
def index():
    return render_template('index.html')

@app.post('/craft')
def craft():
    first = request.json['first']
    second = request.json['second']
    combo, first_discovery = existing_or_generate(ingredient_db, combos_db, first, second)
    if combo == None:
        return { 'error': 'Not found' }, 404
    emoji = existing_emoji_or_generate(emoji_db, combo)
    return { 'combo': combo, 'first_discovery': first_discovery, 'emoji': emoji }


if __name__ == '__main__':
    
    ingredient_db = dbm.open('data/ingredients.db', 'c')
    combos_db = dbm.open('data/combos.db', 'c')
    emojis_db = dbm.open('data/emojis.db', 'c')
    prepare_db(ingredient_db, combos_db)

    # print('Performing Checks! (This might take a couple minutes)')
    # start = datetime.now()
    # try_combo('fire', 'water')
    # print("Check complete!")
    # end = datetime.now()
    # print('Check performed in: ', end - start)

    app.run(host='0.0.0.0', port=5000, threaded=False)
