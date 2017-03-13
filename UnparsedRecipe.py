from RecipeClass import *
from StepClass import *
import nltk, string
from bs4 import BeautifulSoup
import urllib

class UnparsedRecipe:
    def __init__(self, url):
        self.url = url
        if url != None:
            self.soup = self.extract_soup()
            self.title = self.extract_title()
            self.ingredients = self.extract_ingredients()
            self.directions = self.extract_directions()

    def dummy(self, ingredients, directions):
        self.ingredients = ingredients
        self.directions = directions

    def extract_soup(self):
        data = urllib.urlopen(self.url)
        soup = BeautifulSoup(data, "lxml")
        return soup

    def extract_title(self):
        title_html = soup.find_all("h1", class_="recipe-summary__h1")
        title = title_html[0].get_text()
        return title

    def extract_ingredients(self):
        ingredients_html = self.soup.find_all("span", class_="recipe-ingred_txt added")
        ingredients = [ingredient.get_text() for ingredient in ingredients_html]
        return ingredients

    def extract_directions(self):
        directions_html = self.soup.find_all("span", class_="recipe-directions__list--item")
        directions = []
        for direction in directions_html:
            tokens = nltk.sent_tokenize(str(direction.get_text()))
            for token in tokens:
                directions.append(token)
        count = 1
        for idx, item in enumerate(directions):
            directions[idx] = (str(count) + ". ") + item
            count += 1
        return directions
