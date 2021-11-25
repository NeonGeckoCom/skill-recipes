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

class Recipe:

    def __init__(self, recipe_data: dict, current_index: int = 0):
        """Stores recipe-related info.

        Args:
            recipe_data (dict): contains recipe data returned from an API call
            current_index (int): keeps track of the current instruction index
        """
        self.recipe_data = recipe_data
        self.current_index = current_index

    def get(self, item: str, default=None):
        """Get a value for an item-key from the recipe data.

        Args:
            item (str): a key for self.recipe_data dict
            default: the default value to return is no match for item

        Returns:
            value from the dict

        """
        return self.recipe_data.get(item, default)

    def set(self, item, value):
        """Set the value for the item key in self.recipe_data.

        Args:
            item: a key for the dict key-value pair
            value: a value for the dict key-value pair

        Returns:
            None

        """
        self.recipe_data[item] = value

    def get_recipe_data(self) -> dict:
        """Get the recipe data dict.

        Returns:
            dict: self.recipe_data

        """
        return self.recipe_data

    def get_current_index(self) -> int:
        """Get the current step of the recipe instructions

        Returns:
            int: the current index of the instruction

        """
        return self.current_index

    def update_current_index(self, new_index: int) -> None:
        """Update the current instruction index.

        Args:
            new_index (int):  index value to be assigned

        Returns:
            None

        """
        self.current_index = new_index


class RecipeStorage:

    def __init__(self):
        """Maps recipes to users."""
        self.recipes = {}

    def assign_recipe(self, user: str, recipe: Recipe) -> None:
        """Assign recipe to a user.

        Args:
            user (str): a user to assign recipe to
            recipe (Recipe): a recipe to assign to a user

        Returns:
            None

        """
        self.recipes[user] = recipe

    def get_current_recipe(self, user: str) -> Recipe:
        """Get the recipe for a specific user.

        Args:
            user (str): a user to get their recipe for

        Returns:
            Recipe: the recipe object

        """
        return self.recipes.get(user, None)
