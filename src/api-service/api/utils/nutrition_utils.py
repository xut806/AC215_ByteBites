import os
import requests

# Use environment variable for the USDA API key
USDA_API_KEY = os.getenv("USDA_API_KEY")

def get_nutrition_info(ingredients):
    nutrition_data = {}
    base_url = "https://api.nal.usda.gov/fdc/v1/foods/search"

    for ingredient in ingredients:
        params = {"query": ingredient, "api_key": USDA_API_KEY, "pageSize": 3}
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data["foods"]:
                fndds_foods = [
                    food
                    for food in data["foods"]
                    if food.get("dataType") == "Survey (FNDDS)"
                ]

                if fndds_foods:
                    sorted_foods = sorted(
                        fndds_foods,
                        key=lambda x: len(x.get("foodNutrients", [])),
                        reverse=True,
                    )
                    most_complete_food = sorted_foods[0]

                    if most_complete_food.get("servingSize") is None:
                        serving_size = 100
                        serving_size_unit = "g"
                    print(
                        f"Reminder: Raw ingredient data found for {ingredient}. "
                        "The nutrition calculation for this ingredient is based "
                        "on the FNDDS database from USDA."
                    )

                else:
                    print(
                        f"Reminder: No raw ingredient data found for {ingredient}. "
                        "General USDA nutrition facts search is used for "
                        "nutrition calculation for this ingredient."
                    )
                    non_fndds_foods = [
                        food
                        for food in data["foods"]
                        if food.get("dataType") != "Survey (FNDDS)"
                    ]

                    if non_fndds_foods:
                        sorted_foods = sorted(
                            non_fndds_foods,
                            key=lambda x: len(x.get("foodNutrients", [])),
                            reverse=True,
                        )
                        most_complete_food = next(
                            (
                                food
                                for food in sorted_foods
                                if food.get("servingSize") is not None
                            ),
                            sorted_foods[0],
                        )
                        serving_size = most_complete_food.get(
                            "servingSize", "N/A"
                        )
                        serving_size_unit = most_complete_food.get(
                            "servingSizeUnit", ""
                        )
                    else:
                        print(
                            f"Warning: No nutrition data available for {ingredient}. "
                            "This ingredient will not be included in the nutrition facts calculation."
                        )
                        continue

                nutrition_data[ingredient] = {
                    "description": most_complete_food["description"],
                    "dataType": most_complete_food["dataType"],
                    "servingSize": serving_size,
                    "servingSizeUnit": serving_size_unit,
                    "nutrients": {
                        nutrient["nutrientName"]: {
                            "value": nutrient["value"],
                            "unit": nutrient.get("unitName", ""),
                        }
                        for nutrient in most_complete_food["foodNutrients"]
                    },
                }
        else:
            print(f"Failed to retrieve data for {ingredient}")

    return nutrition_data

def aggregate_nutrition_info_with_units(nutrition_info_dict):
    """
    Aggregates the nutrients info for each ingredient,
    and scales the serving size to display nutrition facts for 100g.
    """
    overall_nutrition = {}

    for ingredient, info in nutrition_info_dict.items():
        serving_size = info.get("servingSize", None)
        serving_size_unit = info.get("servingSizeUnit", "").lower()

        if serving_size and serving_size_unit == "g":
            scale_factor = 100 / serving_size

            for nutrient_name, nutrient_info in info["nutrients"].items():
                value = nutrient_info["value"] * scale_factor
                unit = nutrient_info["unit"]

                if nutrient_name in overall_nutrition:
                    overall_nutrition[nutrient_name]["value"] += value
                else:
                    overall_nutrition[nutrient_name] = {
                        "value": value,
                        "unit": unit,
                    }
        else:
            print(f"Warning: Cannot scale {ingredient}; serving size is missing.")

    return overall_nutrition
