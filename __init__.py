# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
#
# Copyright 2008-2021 Neongecko.com Inc. | All Rights Reserved
#
# Notice of License - Duplicating this Notice of License near the start of any file containing
# a derivative of this software is a condition of license for this software.
# Friendly Licensing:
# No charge, open source royalty free use of the Neon AI software source and object is offered for
# educational users, noncommercial enthusiasts, Public Benefit Corporations (and LLCs) and
# Social Purpose Corporations (and LLCs). Developers can contact developers@neon.ai
# For commercial licensing, distribution of derivative works or redistribution please contact licenses@neon.ai
# Distributed on an "AS IS” basis without warranties or conditions of any kind, either express or implied.
# Trademarks of Neongecko: Neon AI(TM), Neon Assist (TM), Neon Communicator(TM), Klat(TM)
# Authors: Guy Daniels, Daniel McKnight, Regina Bloomstine, Elon Gasper, Richard Leeds
#
# Specialized conversational reconveyance options from Conversation Processing Intelligence Corp.
# US Patents 2008-2021: US7424516, US20140161250, US20140177813, US8638908, US8068604, US8553852, US10530923, US10530924
# China Patent: CN102017585  -  Europe Patent: EU2156652  -  Patents Pending

import time
import os
import re
from typing import Optional
from datetime import datetime, date
from adapt.intent import IntentBuilder
from lingua_franca.parse import extract_datetime, extract_duration
from lingua_franca import load_language

from mycroft import Message
from mycroft.util.log import LOG
from mycroft.skills.core import MycroftSkill
from neon_utils import stub_missing_parameters, skill_needs_patching
from neon_utils.transcript_utils import write_transcript_file, update_csv

from mycroft import MycroftSkill, intent_handler, AdaptIntent
import requests
import time


API_KEY = '1'
API_URL = 'https://www.thecocktaildb.com/api/json/v1/{}/'.format(API_KEY)
SEARCH = API_URL + 'search.php'
RANDOM = API_URL + 'random.php'


class RecipeSkill(MycroftSkill):

    def __init__(self):
        super(RecipeSkill, self).__init__(name="RecipeSkill")
        if skill_needs_patching(self):
            stub_missing_parameters(self)
        self.internal_language = "en"
        load_language(self.internal_language)
        self.active_recipe = None

    def initialize(self):
        search_recipe = IntentBuilder("search_recipe").require("").require("").optionally(""). \
            optionally("").build()
        self.register_intent(search_recipe, self.handle_search_recipe)

        search_random = IntentBuilder("search_random").require().optionally().build()
        self.register_intent(search_random, self.handle_search_random)

        recite_recipe = IntentBuilder("recite_recipe").require("").optionally("").build()
        self.register_intent(recite_recipe, self.handle_recite_recipe)

    def handle_search_recipe(self, message: Message):
        recipe_name = message.data.get("recipe_name")
        recipe = self._search_recipe(recipe_name)
        if recipe:
            self.active_recipe = recipe
            ingredients = self._get_ingredients(recipe)
            self.speak_dilog("You will need", {"recipe": recipe_name, "ingredients": ingredients})

    def handle_search_random(self, message: Message):
        recipe = self._search_random()
        if recipe:
            self.active_recipe = recipe
            ingredients = self._get_ingredients(recipe)
            recipe_name = recipe.get('strMeal', 'the meal')
            self.speak_dilog("You will need", {"recipe": recipe_name, "ingredients": ingredients})

    def handle_recite_recipe(self, message: Message):
        pass

    def handle_repeat_ingredients(self, message: Message):
        pass

    def handle_repeat_last_step(self, message: Message):
        pass

    def converse(self, message: Message):
        user = self.get_utterance_user(message)
        confirmed = self.check_yes_no_response(message)
        if confirmed == -1:
            pass
            # self._speak_dialog_with_transcribe(message=message, args=("AskAgain",))
            # self.active_conversation[user]["next_action"] = "friendly_chat"
        elif confirmed:
            pass
            # self._speak_dialog_with_transcribe(message=message,
            #                                    args=("StaffToBeInformed", {"caregiver": caregiver}))
            # self._inform_staff(entry_message, tags=["not-identified intent"])
            # self.active_conversation[user].pop("entry_message")
            # self.active_conversation[user]["next_action"] = None
        else:
            pass

    @staticmethod
    def _search_recipe(name: str) -> Optional[dict]:
        """
        Search TheMealsDB for a meal recipe.
        :param name: recipe name to look up in the DB
        :return: dict with the recipe data, None if request failed
        """
        r = requests.get(SEARCH, params={'s': name})
        if 200 <= r.status_code < 300 and r.json().get('meals'):
            return r.json()['meals'][0]
        else:
            return None

    @staticmethod
    def _search_random() -> Optional[dict]:
        """
        Search a random meal in the DB
        :return: dict with the recipe data, None if request failed
        """
        r = requests.get(RANDOM)
        if 200 <= r.status_code < 300 and r.json().get('meals'):
            return r.json()['meals'][0]
        else:
            return None

    @staticmethod
    def _get_ingredients(recipe: dict) -> dict:
        """
        Get ingredients from recipe
        :param recipe: a dict with all the info about the recipe
        :return: a dict with ingredient-quantity and key-value pairs
        """
        ingredients = {}
        for i in range(1, 21):
            ingredient_key = 'strIngredient' + str(i)
            measure_key = 'strMeasure' + str(i)
            if not recipe[ingredient_key]:
                break
            if recipe[measure_key]:
                ingredients[ingredient_key] = measure_key
            else:  # No measurement -> None
                ingredients[ingredient_key] = None
        # self._beautify_ingredients(ingredients)
        return ingredients

    @staticmethod
    def _beautify_ingredients(ingredients: dict) -> None:
        """Make ingredient list easier to pronounce."""
        units = {
            'oz': 'ounce',
            '1 tbl': '1 table spoon',
            'tbl': 'table spoons',
            '1 tsp': 'tea spoon',
            'tsp': 'tea spoons',
            'ml ': 'milliliter ',
            'cl ': 'centiliter '
        }
        for key in ingredients:
            for word, replacement in units.items():
                ingredients[key] = ingredients[key].lower().replace(word, replacement)
        return

    @staticmethod
    def _get_instructions(recipe: dict) -> list:
        """
        Get recipe steps
        :param recipe: a dict with all the info about the recipe
        :return: a list with recipe steps
        """
        instruction_text = recipe.get("strInstructions")
        instruction_text = re.sub(r'\r+', '', instruction_text)
        instruction_text = re.sub(r'\n+', '', instruction_text)
        return instruction_text.split(".")


def create_skill():
    return RecipeSkill()
