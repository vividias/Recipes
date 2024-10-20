from pydantic import BaseModel
from typing import List, Optional, Literal

class Ingredient(BaseModel):
    name: str
    quantity: Optional[float|int]
    measure: Optional[str] = 'unit'
    group: Optional[str]

class Step(BaseModel):
    number: int
    description: str

class Recipe(BaseModel):
    title: str
    category: Literal['main','snack','dessert']
    ingredients: List[Ingredient]
    steps: List[Step]

class Recipes(BaseModel):
    recipes: List[Recipe]

class RecipeExists(BaseModel):
    answer: bool
    