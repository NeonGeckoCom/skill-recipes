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
