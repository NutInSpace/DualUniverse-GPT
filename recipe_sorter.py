import json
import random
import re

item_data = None  # Global variable to store the loaded item data
recipe_data = None  # Global variable to store the recipe data
default_item_file = "items.json"
default_recipe_file = "recipes.json"

def load_item_data(file_path=default_item_file):
    global item_data
    try:
        with open(file_path) as file:
            item_data = json.load(file)
        print("Item data loaded successfully.")
    except FileNotFoundError:
        print("File not found. Unable to load item data.")

def load_recipe_data(file_path=default_recipe_file):
    global recipe_data
    try:
        with open(file_path) as file:
            recipe_data = json.load(file)
        print("Recipe data loaded successfully.")
    except FileNotFoundError:
        print("File not found. Unable to load recipe data.")

def save_item_data(file_path=default_item_file):
    if item_data:
        try:
            with open(file_path, 'w') as file:
                json.dump(item_data, file)
            print("Item data saved successfully.")
        except:
            print("Error occurred while saving item data.")
    else:
        print("No item data to save.")

def save_recipe_data(file_path=default_recipe_file):
    if recipe_data:
        try:
            with open(file_path, 'w') as file:
                json.dump(recipe_data, file)
            print("Recipe data saved successfully.")
        except:
            print("Error occurred while saving recipe data.")
    else:
        print("No recipe data to save.")

def select_random_items(item_list, num_items):
    """
    Selects a specified number of random items from a given list.
    
    Args:
        item_list (list): The list of items to choose from.
        num_items (int): The number of items to select.
        
    Returns:
        list: A list of randomly selected items.
    """
    if num_items > len(item_list):
        num_items = len(item_list)
        
    random_items = random.sample(item_list, num_items)
    return random_items

def print_items(limit=10):
    if item_data:
        count = len(item_data)
        print(f"Item data count: {count}")
        
        if limit:
            for item in select_random_items(item_data, limit):
                print_item(item)
                print()
        else: 
            for item in item_data:
                print_item(item)
                print()
            
    else:
        print("No item data loaded.")

def print_item(item):
    print(f"Item ID: {item['id']}")
    print(f"Display Name with Size: {item['displayNameWithSize']}")
    #print(f"Local Display Name with Size: {item['locDisplayNameWithSize']}")
    #print(f"Description: {item['description']}")
    if item.get('schematics'):
        print("Schematics:", end=" ")
        for schematic_id in item['schematics']:
            schematic_item = next((item for item in item_data if item['id'] == schematic_id), None)
            if schematic_item:
                #print(f"- Schematic ID: {schematic_item['id']}")
                print(f"  Schematic Display Name: {schematic_item['displayNameWithSize']}")
                #print(f"  Schematic Local Display Name with Size: {schematic_item['locDisplayNameWithSize']}")
    else:
        print("No schematics available.")
    if item.get('products'):
        cost = calculate_item_cost(item)
        print(f"Item Cost: {cost}")
    else:
        print("No products available.")

def print_recipes(limit=10):
    if recipe_data:
        count = len(recipe_data)
        print(f"Recipe data count: {count}")
        if limit:
            for recipe in select_random_items(recipe_data, limit):
                print_recipe(recipe)
                print()
        else:
            for recipe in recipe_data:
                print_recipe(recipe)
                print()
    else:
        print("No recipe data loaded.")

def print_recipe(recipe):
    print(f"Recipe ID: {recipe['id']}")
    if recipe.get('ingredients'):
        print("Ingredients:")
        for ingredient in recipe['ingredients']:
            #print(f"- Ingredient ID: {ingredient['id']}")
            print(f"  Ingredient Display Name: {ingredient['displayNameWithSize']}")
    else:
        print("No ingredients available.")
    if recipe.get('products'):
        product = recipe['products'][0]  # Only use the first product in the list
        print("Product:")
        # print(f"- Product ID: {product['id']}")
        print(f"  Product Display Name: {product['displayNameWithSize']}")
    else:
        print("No products available.")

def sample_item_data():
    if item_data:
        if len(item_data) > 0:
            random_item = random.choice(item_data)
            print("Random item:")
            print_item(random_item)
        else:
            print("No item data items.")
    else:
        print("No item data loaded.")

def sample_recipe_data():
    if recipe_data:
        if len(recipe_data) > 0:
            random_recipe = random.choice(recipe_data)
            print("Random recipe:")
            print_recipe(random_recipe)
        else:
            print("No recipe data items.")
    else:
        print("No recipe data loaded.")

def calculate_item_cost(item):
    if 'schematics' in item:
        cost = 0
        for schematic_id in item['schematics']:
            schematic_item = next((recipe for recipe in recipe_data if recipe['id'] == schematic_id), None)
            if schematic_item:
                cost += calculate_recipe_cost(schematic_item)
        return cost
    else:
        return 0

def calculate_recipe_cost(recipe):
    if 'ingredients' in recipe and 'products' in recipe:
        ingredient_costs = [calculate_ingredient_cost(ingredient) for ingredient in recipe['ingredients']]
        schematic_costs = [calculate_schematic_cost(product) for product in recipe['products']]
        total_cost = sum(ingredient_costs) + sum(schematic_costs)
        return total_cost
    else:
        return 0

def calculate_ingredient_cost(ingredient):
    if 'quantity' in ingredient and 'id' in ingredient:
        ingredient_item = next((item for item in recipe_data if item['id'] == ingredient['id']), None)
        if ingredient_item:
            ingredient_cost = calculate_recipe_cost(ingredient_item)
            return ingredient_cost * ingredient['quantity']
    return 0



def find_item_by_display_name(display_name):
    if item_data:
        regex_pattern = re.compile(display_name, re.IGNORECASE)
        found_items = [item for item in item_data if item.get('displayNameWithSize') and regex_pattern.search(item['displayNameWithSize'])]
        if found_items:
            print(f"Found {len(found_items)} item(s) with displayNameWithSize matching '{display_name}':")
            for item in found_items:
                print_item(item)
                print()
        else:
            print(f"No item found with displayNameWithSize matching '{display_name}'")
    else:
        print("No item data loaded.")

def menu():
    while True:
        print("\nMENU")
        print("1. Load item data from JSON file (default: {})".format(default_item_file))
        print("2. Save item data to JSON file (default: {})".format(default_item_file))
        print("3. Print item data")
        print("4. Print recipe data")
        print("5. Sample item data")
        print("6. Sample recipe data")
        print("7. Calculate item cost")
        print("8. Find item by displayNameWithSize")
        print("9. Exit")

        choice = input("Enter your choice (1-9): ")

        if choice == '1':
            item_file_path = input("Enter the item data JSON file path (default: {}): ".format(default_item_file)) or default_item_file
            recipe_file_path = input("Enter the recipe data JSON file path (default: {}): ".format(default_recipe_file)) or default_recipe_file
            load_item_data(item_file_path)
            load_recipe_data(recipe_file_path)
        elif choice == '2':
            item_file_path = input("Enter the item data JSON file path (default: {}): ".format(default_item_file)) or default_item_file
            recipe_file_path = input("Enter the recipe data JSON file path (default: {}): ".format(default_recipe_file)) or default_recipe_file
            save_item_data(item_file_path)
            save_recipe_data(recipe_file_path)
        elif choice == '3':
            print_items()
        elif choice == '4':
            print_recipes()
        elif choice == '5':
            sample_item_data()
        elif choice == '6':
            sample_recipe_data()
        elif choice == '7':
            item_id = input("Enter the item ID to calculate the item cost: ")
            item = next((item for item in item_data if item['id'] == item_id), None)
            if item:
                cost = calculate_item_cost(item)
                print("Item cost for item with ID '{}': {}".format(item_id, cost))
            else:
                print("Item with ID '{}' not found.".format(item_id))
        elif choice == '8':
            display_name = input("Enter the displayNameWithSize to find: ")
            find_item_by_display_name(display_name)
        elif choice == '9':
            break
        else:
            print("Invalid choice. Please try again.")

# Load the default data files initially
load_item_data()
load_recipe_data()

# Start the menu
menu()
