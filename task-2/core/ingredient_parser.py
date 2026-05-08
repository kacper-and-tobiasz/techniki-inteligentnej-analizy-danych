import re
import json
import os
from typing import List, Set
MULTI_WORD_PATTERNS = [('kapust\\w*\\s+kiszon\\w*', 'kapusta kiszona'), ('ogór\\w*\\s+kiszon\\w*', 'ogórek kiszony'), ('mlek\\w*\\s+kokos\\w*', 'mleko kokosowe'), ('win\\w*\\s+biał\\w*', 'wino białe'), ('zakwas\\w*\\s+żur\\w*', 'zakwas żurowy'), ('buł\\w*\\s+tart\\w*', 'bułka tarta'), ('oliw\\w*\\s+z\\s+oliw\\w*', 'oliwa z oliwek'), ('ser\\w*\\s+fet\\w*', 'ser feta'), ('mięs\\w*\\s+miel\\w*', 'mięso mielone'), ('prosz\\w*\\s+do\\s+pieczeni\\w*', 'proszek do pieczenia'), ('cuk\\w*\\s+waniliow\\w*', 'cukier waniliowy'), ('cuk\\w*\\s+pud\\w*', 'cukier puder')]
INGREDIENT_STEMS = {'pomidor': 'pomidor', 'cebul': 'cebula', 'czosn': 'czosnek', 'ziemniak': 'ziemniaki', 'kartofl': 'ziemniaki', 'marchew': 'marchew', 'marchewk': 'marchew', 'pietrus': 'pietruszka', 'seler': 'seler', 'kapust': 'kapusta', 'ogórek': 'ogórek', 'ogórk': 'ogórek', 'kiszony': 'ogórek kiszony', 'papryk': 'papryka', 'szpinak': 'szpinak', 'brokuł': 'brokuły', 'dyni': 'dynia', 'dynię': 'dynia', 'cukini': 'cukinia', 'bakłażan': 'bakłażan', 'burak': 'buraki', 'groszek': 'groszek', 'groszk': 'groszek', 'fasol': 'fasola', 'kukuryd': 'kukurydza', 'sałat': 'sałata', 'koper': 'koperek', 'koperk': 'koperek', 'jabłk': 'jabłko', 'jabłek': 'jabłko', 'cytryn': 'cytryna', 'śliwk': 'śliwki', 'kurczak': 'kurczak', 'kurcz': 'kurczak', 'schab': 'schab', 'wieprzow': 'wieprzowina', 'wołow': 'wołowina', 'boczek': 'boczek', 'boczk': 'boczek', 'kiełbas': 'kiełbasa', 'szynk': 'szynka', 'indyk': 'indyk', 'tuńczyk': 'tuńczyk', 'jajk': 'jajka', 'jajec': 'jajka', 'mlek': 'mleko', 'masł': 'masło', 'śmietan': 'śmietana', 'jogurt': 'jogurt', 'twaróg': 'twaróg', 'twarog': 'twaróg', 'feta': 'ser feta', 'mozzarell': 'mozzarella', 'parmezan': 'parmezan', 'mąk': 'mąka', 'ryż': 'ryż', 'makaron': 'makaron', 'chleb': 'chleb', 'bułk': 'bułka tarta', 'drożdż': 'drożdże', 'pieprz': 'pieprz', 'cukier': 'cukier', 'cukr': 'cukier', 'cynamon': 'cynamon', 'oregano': 'oregano', 'bazyli': 'bazylia', 'curry': 'curry', 'imbir': 'imbir', 'chrzan': 'chrzan', 'musztard': 'musztarda', 'oliw': 'oliwa z oliwek', 'olej': 'olej', 'grzyb': 'grzyby', 'oliwk': 'oliwki', 'ocet': 'ocet', 'bulio': 'bulion', 'majonez': 'majonez', 'majones': 'majonez', 'wino': 'wino białe', 'zakwas': 'zakwas żurowy', 'mleko kokos': 'mleko kokosowe', 'kokos': 'mleko kokosowe'}
SHORT_STEMS = {'sól', 'sol', 'ser', 'por'}
SHORT_STEM_MAP = {'sól': 'sól', 'sol': 'sól', 'soli': 'sól', 'ser': 'ser', 'sera': 'ser', 'serem': 'ser', 'por': 'por', 'pora': 'por', 'pory': 'por', 'porem': 'por'}

def _build_ingredient_set_from_recipes(recipes_path: str) -> Set[str]:
    try:
        with open(recipes_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        ingredients = set()
        for recipe in data.get('recipes', []):
            for ing in recipe.get('ingredients', []):
                ingredients.add(ing.lower())
        return ingredients
    except Exception:
        return set()

def parse_ingredients(text: str, recipes_path: str=None) -> List[str]:
    if not text or not text.strip():
        return []
    text_lower = text.lower().strip()
    text_clean = re.sub('[^\\w\\sąćęłńóśźżĄĆĘŁŃÓŚŹŻ]', ' ', text_lower)
    found = set()
    for pattern, canonical in MULTI_WORD_PATTERNS:
        if re.search(pattern, text_clean):
            found.add(canonical)
            text_clean = re.sub(pattern, ' ', text_clean)
    words = text_clean.split()
    for stem, canonical in INGREDIENT_STEMS.items():
        stem_lower = stem.lower()
        for word in words:
            if word.startswith(stem_lower):
                found.add(canonical)
                break
    for word in words:
        if word in SHORT_STEM_MAP:
            found.add(SHORT_STEM_MAP[word])
    return sorted(list(found))

def get_all_known_ingredients() -> List[str]:
    all_ingredients = set(INGREDIENT_STEMS.values())
    all_ingredients.update(SHORT_STEM_MAP.values())
    return sorted(list(all_ingredients))