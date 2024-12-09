import json

data = {
    "train": [
        {
            "prompt": "Please write a spicy dessert recipe that takes approximately 40 minutes and includes the following ingredients: chocolate, cayenne, cinnamon, sugar, and cream.",
            "chosen": "Ingredients:\n- Chocolate\n- Cayenne\n- Cinnamon\n- Sugar\n- Cream\n\nInstructions:\n1. Melt the chocolate in a double boiler.\n2. Stir in cinnamon, sugar, and a pinch of cayenne.\n3. Whip cream and fold into the chocolate mixture.\n4. Chill in serving glasses and top with a sprinkle of cayenne before serving.",
            "rejected": "Ingredients:\n- Chocolate\n- Sugar\n- Cream\n\nInstructions:\n1. Melt the chocolate in a double boiler.\n2. Stir in sugar and fold in whipped cream.\n3. Chill in serving glasses."
        },
        {
            "prompt": "Please write a spicy soup recipe that takes approximately 30 minutes and includes the following ingredients: tomatoes, chili powder, cumin, garlic, and onion.",
            "chosen": "Ingredients:\n- Tomatoes\n- Chili powder\n- Cumin\n- Garlic\n- Onion\n\nInstructions:\n1. Sauté chopped onion and minced garlic in a pot.\n2. Add diced tomatoes, chili powder, and cumin.\n3. Simmer for 20 minutes and blend until smooth.\n4. Serve hot with a sprinkle of fresh cilantro.",
            "rejected": "Ingredients:\n- Tomatoes\n- Garlic\n- Onion\n\nInstructions:\n1. Sauté chopped onion and minced garlic in a pot.\n2. Add diced tomatoes and simmer for 20 minutes.\n3. Blend until smooth and serve."
        }
    ],
    "test": [
        {
            "prompt": "Please write a spicy appetizer recipe that takes approximately 15 minutes and includes the following ingredients: jalapeños, cream cheese, cheddar cheese, and bacon.",
            "chosen": "Ingredients:\n- Jalapeños\n- Cream cheese\n- Cheddar cheese\n- Bacon\n\nInstructions:\n1. Preheat oven to 400°F.\n2. Slice jalapeños in half lengthwise and remove seeds.\n3. Fill each jalapeño half with cream cheese.\n4. Sprinkle cheddar cheese on top.\n5. Wrap each jalapeño with bacon and secure with a toothpick.\n6. Place on a baking sheet and bake for 12-15 minutes, or until bacon is crispy.",
            "rejected": "Ingredients:\n- Jalapeños\n- Cream cheese\n\nInstructions:\n1. Slice jalapeños in half and remove seeds.\n2. Fill with cream cheese and serve raw."
        },
        {
            "prompt": "Please write a spicy breakfast recipe that takes approximately 20 minutes and includes the following ingredients: eggs, hot sauce, sausage, and green chilies.",
            "chosen": "Ingredients:\n- Eggs\n- Hot sauce\n- Sausage\n- Green chilies\n\nInstructions:\n1. Cook sausage in a skillet over medium heat until browned.\n2. Add chopped green chilies to the skillet and sauté for 2 minutes.\n3. Beat eggs with a splash of hot sauce and pour into the skillet.\n4. Cook and stir until eggs are set.\n5. Serve with additional hot sauce on the side.",
            "rejected": "Ingredients:\n- Eggs\n- Sausage\n\nInstructions:\n1. Cook sausage in a skillet.\n2. Fry eggs in the same skillet.\n3. Serve sausage and eggs side by side with toast."
        }
    ]
}

# Save to file
file_path = './spicy_recipes.json'
with open(file_path, 'w') as file:
    json.dump(data, file, indent=4)