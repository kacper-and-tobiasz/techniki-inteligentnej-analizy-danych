import json
import os
from typing import List, Dict, Any

def load_recipes(recipes_path: str=None) -> List[Dict[str, Any]]:
    if recipes_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        recipes_path = os.path.join(base_dir, 'data', 'recipes.json')
    try:
        with open(recipes_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('recipes', [])
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as e:
        return []

def filter_recipes(recipes: List[Dict[str, Any]], required_ingredients: List[str]) -> List[Dict[str, Any]]:
    if not required_ingredients:
        return []
    required_set = {ing.lower() for ing in required_ingredients}
    results = []
    for recipe in recipes:
        recipe_ingredients = {ing.lower() for ing in recipe.get('ingredients', [])}
        matched = required_set & recipe_ingredients
        if required_set.issubset(recipe_ingredients):
            results.append({**recipe, '_matched_count': len(matched), '_total_ingredients': len(recipe_ingredients), '_matched_ingredients': matched})
    results.sort(key=lambda r: (-r['_matched_count'], r['_total_ingredients']))
    return results

def get_all_ingredients(recipes: List[Dict[str, Any]]) -> List[str]:
    ingredients = set()
    for recipe in recipes:
        for ing in recipe.get('ingredients', []):
            ingredients.add(ing.lower())
    return sorted(list(ingredients))