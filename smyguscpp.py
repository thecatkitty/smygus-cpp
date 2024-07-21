import importlib
import inspect
import pkgutil
import recipes
import sys

if 1 < len(sys.argv):
    recipe_name, func_name = sys.argv[1].split('.')
    recipe = importlib.import_module(f'recipes.{recipe_name}')
    func = getattr(recipe, func_name)

    func(*sys.argv[2:])
    exit()

for module in pkgutil.iter_modules(recipes.__path__):
    print(module.name)
    recipe = importlib.import_module(f'recipes.{module.name}')
    for member in inspect.getmembers(recipe):
        if inspect.isfunction(member[1]):
            print(f'\t{member[0]}')
