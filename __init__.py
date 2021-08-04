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

import re
import requests
from typing import Optional
from abc import ABC, abstractmethod

from lingua_franca import load_language
from mycroft import Message, intent_handler
from neon_utils.skills.neon_skill import NeonSkill


API_KEY = '1'
API_URL = 'https://www.themealdb.com/api/json/v1/{}/'.format(API_KEY)
SEARCH = API_URL + 'search.php'
RANDOM = API_URL + 'random.php'
FILTER = API_URL + 'filter.php'


# TODO: remove InstructorSkill from here (move to NeonCore or neon-skill-utils)
class InstructorSkill(NeonSkill):
    """This skill acts as an interface for other instruction-oriented skills"""

    def __init__(self, name: str = ''):
        super(InstructorSkill, self).__init__(name=name)

    @abstractmethod
    def _access_data_source(self, *args, **kwargs):
        """A method to establish connection to the data source of instructions"""

    @abstractmethod
    def _search_in_data_source(self, *args, **kwargs):
        """Search a data source for instructions"""

    @abstractmethod
    def _get_instructions(self, *args, **kwargs):
        """Extract a set of instruction"""


# strategies for searching (functional approach)
def execute_search_random(message: Message) -> Optional[dict]:
    """
    Search a random meal in the DB
    :param message: a Message object associated with the request, a dummy param here to implement a common interface
    :return: dict with the recipe data, None if request failed
    """
    r = requests.get(RANDOM)
    if 200 <= r.status_code < 300 and r.json().get('meals'):
        return r.json()['meals'][0]
    else:
        return None


def execute_search_by_name(message: Message) -> Optional[dict]:
    """
    Search TheMealsDB for a meal recipe by recipe_name.
    :param message: a Message object associated with the request
    :return: dict with the recipe data, None if request failed
    """
    recipe_name = message.data.get("recipe_name")
    r = requests.get(SEARCH, params={'s': recipe_name})
    if 200 <= r.status_code < 300 and r.json().get('meals'):
        return r.json()['meals'][0]
    else:
        return None


def execute_search_by_ingredient(message: Message) -> Optional[dict]:
    """
    Search TheMealsDB for a meal recipe by main ingredient.
    :param message: a Message object associated with the request
    :return: list with names of recipes filtered by ingredient
    """
    ingredient = message.data.get("ingredient")
    processes_ingredient = re.sub(r' ', '_', ingredient)
    r = requests.get(FILTER, params={'i': processes_ingredient})
    if 200 <= r.status_code < 300 and r.json().get('meals'):
        recipes = r.json()['meals']
        recipe_name = recipes[0].get('strMeal', '')
        message.data["recipe_name"] = recipe_name
        return execute_search_by_name(message)
    else:
        return None


class RecipeSkill(InstructorSkill):

    def __init__(self):
        super(RecipeSkill, self).__init__(name="RecipeSkill")
        self.internal_language = "en"
        load_language(self.internal_language)
        self.active_recipe = dict()
        self.current_index = 0

    # intent handlers
    @intent_handler('get.recipe.by.name.intent')
    def handle_search_recipe_by_name(self, message: Message):
        recipe = self._search_in_data_source(search_strategy=execute_search_by_name, message=message)
        self._after_search(recipe)

    @intent_handler('get.recipe.by.ingredient.intent')
    def handle_search_recipe_by_ingredient(self, message: Message):
        recipe = self._search_in_data_source(search_strategy=execute_search_by_ingredient, message=message)
        self._after_search(recipe)

    @intent_handler('get.random.recipe.intent')
    def handle_search_random(self, message: Message):
        recipe = self._search_in_data_source(search_strategy=execute_search_random, message=message)
        self._after_search(recipe)

    @intent_handler('get.the.recipe.name.intent')
    def handle_get_recipe_name(self, message: Message):
        recipe_name = self.active_recipe.get("strMeal")
        if recipe_name:
            self.speak_dialog("CurrentRecipe", {"recipe_name": recipe_name})
        else:
            self.speak_dialog("NoRecipe")

    @intent_handler('recite.the.instructions.intent')
    def handle_recite_instructions(self, message: Message):
        instructions = self._get_instructions(self.active_recipe)
        if instructions:
            for index in range(len(instructions)):
                self.current_index = index
                self.speak_dialog("ReciteStep", {"step": instructions[index]}, wait=True)
        else:
            self.speak_dialog("NoInstructions")

    @intent_handler('get.the.ingredients.intent')
    def handle_get_ingredients(self, message: Message):
        ingredients = self._get_ingredients(self.active_recipe)
        string_ingredients = self._to_string_ingredients(ingredients)
        recipe_name = self.active_recipe.get('strMeal', 'the meal')
        if ingredients:
            self.speak_dialog("YouWillNeed", {"recipe_name": recipe_name, "ingredients": string_ingredients})
        else:
            self.speak_dialog("NoIngredients")

    @intent_handler('get.the.current.step.intent')
    def handle_get_current_step(self, message: Message):
        instructions = self._get_instructions(self.active_recipe)
        try:
            self.speak_dialog("CurrentStep", {"recipe_name": self.active_recipe.get("strMeal", "the meal"),
                                              "step": instructions[self.current_index]})
        except IndexError:  # the instruction list is empty
            self.speak_dialog("NoInstructions")

    @intent_handler('get.the.previous.step.intent')
    def handle_get_previous_step(self, message: Message):
        instructions = self._get_instructions(self.active_recipe)
        previous_index = self.current_index - 1
        if self.current_index > 0:
            self.speak_dialog("PreviousStep", {"recipe_name": self.active_recipe.get("strMeal", "the meal"),
                                               "step": instructions[previous_index]})
            self.current_index = previous_index
        else:
            self.speak_dialog("NoPreviousStep")

    @intent_handler('get.the.next.step.intent')
    def handle_get_next_step(self, message: Message):
        instructions = self._get_instructions(self.active_recipe)
        next_index = self.current_index + 1
        if next_index < len(instructions):
            self.speak_dialog("NextStep", {"recipe_name": self.active_recipe.get("strMeal"),
                                           "step": instructions[next_index]})
            self.current_index = next_index
        else:
            self.speak_dialog("NoNextSteps")

    # defining abstract methods
    def _access_data_source(self):
        pass

    def _search_in_data_source(self, search_strategy, message: Message):
        return search_strategy(message)

    @staticmethod
    def _get_instructions(recipe: dict) -> list:
        """
        Get recipe steps
        :param recipe: a dict with all the info about the recipe
        :return: a list with recipe steps
        """
        instruction_text = recipe.get("strInstructions", "")
        instruction_text = re.sub(r'\r+', '', instruction_text)
        instruction_text = re.sub(r'\n+', '', instruction_text)
        instruction_list = [step for step in instruction_text.split(".") if step]
        return instruction_list

    # static utility methods
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
            if not recipe.get(ingredient_key):
                break
            if recipe[measure_key]:
                ingredients[recipe[ingredient_key]] = recipe[measure_key]
            else:  # No measurement -> None
                ingredients[recipe[ingredient_key]] = None
        # self._beautify_ingredients(ingredients)
        return ingredients

    @staticmethod
    def _to_string_ingredients(ingredients: dict) -> Optional[str]:
        """Make ingredients dict into a string of ingredients and their quantities"""
        substrings = []
        for ingredient, quantity in ingredients.items():
            substrings.append(ingredient + " " + quantity)
        return ' '.join(substrings) if substrings else None

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

    # other utilities
    def _create_new_recipe(self, recipe: dict) -> dict:
        """Create a new recipe with side effects"""
        # TODO: consider using recipe manager to store a queue of recipes
        self.current_index = 0
        return recipe

    def _after_search(self, recipe):
        """A set of statements to execute after searching"""
        if recipe:
            self.active_recipe = self._create_new_recipe(recipe)
            ingredients = self._get_ingredients(recipe)
            string_ingredients = self._to_string_ingredients(ingredients)
            recipe_name = recipe.get('strMeal', 'the meal')
            self.speak_dialog("YouWillNeed", {"recipe_name": recipe_name, "ingredients": string_ingredients})
        else:
            self.speak_dialog("SearchFailed")


def create_skill():
    return RecipeSkill()
