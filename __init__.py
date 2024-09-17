# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2022 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import re
import requests
from typing import Optional

from ovos_bus_client.message import Message
from ovos_workshop.decorators import intent_handler
from neon_utils.skills.instructor_skill import InstructorSkill
from neon_utils.message_utils import get_message_user
from ovos_utils import classproperty
from ovos_utils.process_utils import RuntimeRequirements
from .recipe_utils import Recipe, RecipeStorage


API_KEY = '1'
API_URL = 'https://www.themealdb.com/api/json/v1/{}/'.format(API_KEY)
SEARCH = API_URL + 'search.php'
RANDOM = API_URL + 'random.php'
FILTER = API_URL + 'filter.php'


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
    def __init__(self, **kwargs):
        InstructorSkill.__init__(self, **kwargs)
        self.internal_language = "en"
        self.recipe_storage = RecipeStorage()

    @classproperty
    def runtime_requirements(self):
        return RuntimeRequirements(network_before_load=False,
                                   internet_before_load=False,
                                   gui_before_load=False,
                                   requires_internet=True,
                                   requires_network=True,
                                   requires_gui=False,
                                   no_internet_fallback=False,
                                   no_network_fallback=False,
                                   no_gui_fallback=True)

    # intent handlers
    @intent_handler('get.recipe.by.name.intent')
    def handle_search_recipe_by_name(self, message: Message):
        user = get_message_user(message=message)
        recipe_data = self._search_in_data_source(search_strategy=execute_search_by_name, message=message)
        self._after_search(recipe_data=recipe_data, user=user)

    @intent_handler('get.recipe.by.ingredient.intent')
    def handle_search_recipe_by_ingredient(self, message: Message):
        user = get_message_user(message=message)
        recipe_data = self._search_in_data_source(search_strategy=execute_search_by_ingredient, message=message)
        self._after_search(recipe_data=recipe_data, user=user)

    @intent_handler('get.random.recipe.intent')
    def handle_search_random(self, message: Message):
        user = get_message_user(message=message)
        recipe_data = self._search_in_data_source(search_strategy=execute_search_random, message=message)
        self._after_search(recipe_data=recipe_data, user=user)

    @intent_handler('get.the.recipe.name.intent')
    def handle_get_recipe_name(self, message: Message):
        user = get_message_user(message=message)
        current_recipe = self.recipe_storage.get_current_recipe(user=user)
        recipe_name = current_recipe.get(item="strMeal")
        if recipe_name:
            self.speak_dialog("CurrentRecipe", {"recipe_name": recipe_name})
        else:
            self.speak_dialog("NoRecipe")

    @intent_handler('recite.the.instructions.intent')
    def handle_recite_instructions(self, message: Message):
        user = get_message_user(message=message)
        current_recipe = self.recipe_storage.get_current_recipe(user=user)
        recipe_data = current_recipe.get_recipe_data()

        instructions = self._get_instructions(recipe_data)
        if instructions:
            for index in range(len(instructions)):
                current_recipe.update_current_index(new_index=index)
                self.speak_dialog("ReciteStep", {"step": instructions[index]}, wait=True)
        else:
            self.speak_dialog("NoInstructions")

    @intent_handler('get.the.ingredients.intent')
    def handle_get_ingredients(self, message: Message):
        user = get_message_user(message=message)
        current_recipe = self.recipe_storage.get_current_recipe(user=user)
        recipe_data = current_recipe.get_recipe_data()

        ingredients = self._get_ingredients(recipe_data)
        string_ingredients = self._to_string_ingredients(ingredients)
        recipe_name = current_recipe.get(item='strMeal', default='the meal')
        if ingredients:
            self.speak_dialog("YouWillNeed", {"recipe_name": recipe_name, "ingredients": string_ingredients})
        else:
            self.speak_dialog("NoIngredients")

    @intent_handler('get.the.current.step.intent')
    def handle_get_current_step(self, message: Message):
        user = get_message_user(message=message)
        current_recipe = self.recipe_storage.get_current_recipe(user=user)
        current_index = current_recipe.get_current_index()
        recipe_data = current_recipe.get_recipe_data()

        instructions = self._get_instructions(recipe_data)
        recipe_name = current_recipe.get(item='strMeal', default='the meal')
        try:
            self.speak_dialog("CurrentStep", {"recipe_name": recipe_name,
                                              "step": instructions[current_index]})
        except IndexError:  # the instruction list is empty
            self.speak_dialog("NoInstructions")

    @intent_handler('get.the.previous.step.intent')
    def handle_get_previous_step(self, message: Message):
        user = get_message_user(message=message)
        current_recipe = self.recipe_storage.get_current_recipe(user=user)
        recipe_data = current_recipe.get_recipe_data()
        current_index = current_recipe.get_current_index()

        instructions = self._get_instructions(recipe_data)
        previous_index = current_index - 1
        recipe_name = current_recipe.get(item='strMeal', default='the meal')
        if current_index > 0:
            self.speak_dialog("PreviousStep", {"recipe_name": recipe_name,
                                               "step": instructions[previous_index]})
            current_recipe.update_current_index(new_index=previous_index)
        else:
            self.speak_dialog("NoPreviousStep")

    @intent_handler('get.the.next.step.intent')
    def handle_get_next_step(self, message: Message):
        user = get_message_user(message=message)
        current_recipe = self.recipe_storage.get_current_recipe(user=user)
        recipe_data = current_recipe.get_recipe_data()
        current_index = current_recipe.get_current_index()

        instructions = self._get_instructions(recipe_data)
        next_index = current_index + 1
        if next_index < len(instructions):
            self.speak_dialog("NextStep", {"recipe_name": recipe_data.get("strMeal"),
                                           "step": instructions[next_index]})
            current_recipe.update_current_index(new_index=next_index)
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
        return ingredients

    @staticmethod
    def _to_string_ingredients(ingredients: dict) -> Optional[str]:
        """Make ingredients dict into a string of ingredients and their quantities."""
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
    def _create_new_recipe(self, recipe_data: dict, user: str):
        """Create a new recipe with side effects."""
        # TODO: consider using recipe manager to store a queue of recipes
        recipe = Recipe(recipe_data)
        self.recipe_storage.assign_recipe(user=user, recipe=recipe)

    def _after_search(self, recipe_data: dict, user: str):
        """A set of statements to execute after searching."""
        if recipe_data:
            self._create_new_recipe(recipe_data=recipe_data, user=user)
            ingredients = self._get_ingredients(recipe_data)
            string_ingredients = self._to_string_ingredients(ingredients)
            recipe_name = recipe_data.get('strMeal', 'the meal')
            self.speak_dialog("YouWillNeed",
                              {"recipe_name": recipe_name,
                               "ingredients": string_ingredients})
        else:
            self.speak_dialog("SearchFailed")

