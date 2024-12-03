"use client"

import React, { useState } from "react"

interface SelectIngredientsProps {
  onGenerate: (selectedIngredients: string[], dietaryPreferences: string[], mealType: string, cookingTime: number) => void
  ingredients: string[]
}

export default function Component({ onGenerate, ingredients }: SelectIngredientsProps) {
  const [selectedIngredients, setSelectedIngredients] = useState<string[]>([])
  const [dietaryPreferences, setDietaryPreferences] = useState<string[]>([])
  const [mealType, setMealType] = useState<string>("")
  const [cookingTime, setCookingTime] = useState<number | "">("")
  const [newIngredient, setNewIngredient] = useState<string>("")
  const [allIngredients, setAllIngredients] = useState<string[]>(ingredients)

  const preferences = ["Vegetarian", "Vegan", "Gluten Free", "Dairy Free", "Low Carb", "Low Sodium", "Healthy"]
  const mealTypes = ["Breakfast", "Lunch", "Dinner", "Brunch", "Desserts", "Soup", "Salad", "Appetizer"]

  const handleIngredientChange = (ingredient: string) => {
    setSelectedIngredients(prev =>
      prev.includes(ingredient) ? prev.filter(i => i !== ingredient) : [...prev, ingredient]
    )
  }

  const handlePreferenceChange = (preference: string) => {
    setDietaryPreferences(prev =>
      prev.includes(preference) ? prev.filter(p => p !== preference) : [...prev, preference]
    )
  }

  const handleAddIngredient = () => {
    if (newIngredient && !allIngredients.includes(newIngredient)) {
      setAllIngredients(prev => [...prev, newIngredient])
      setSelectedIngredients(prev => [...prev, newIngredient])
      setNewIngredient("")
    }
  }

  return (
    <div className="rounded-lg bg-white p-6 shadow-md mx-auto">
      <h2 className="mb-4 text-center text-2xl font-semibold">Select Ingredients</h2>
      <div className="space-y-5">
        <div className="grid gap-4 sm:grid-cols-2">
          {allIngredients.map(ingredient => (
            <div key={ingredient} className="flex items-center space-x-2">
              <input
                type="checkbox"
                id={ingredient}
                checked={selectedIngredients.includes(ingredient)}
                onChange={() => handleIngredientChange(ingredient)}
                className="h-4 w-4 rounded border-gray-300 text-pink-600 focus:ring-pink-500"
              />
              <label htmlFor={ingredient} className="text-sm font-medium text-gray-700">
                {ingredient}
              </label>
            </div>
          ))}
        </div>
        <div className="flex space-x-2">
            <input
              type="text"
              value={newIngredient}
              onChange={(e) => setNewIngredient(e.target.value)}
              className="mt-2 w-full rounded-md border-gray-300 p-2 focus:ring-pink-500"
              placeholder="Enter new ingredient"
            />
            <button
              onClick={handleAddIngredient}
              className="mt-2 rounded-md bg-pink-500 px-4 py-2 text-white hover:bg-pink-600 focus:outline-none focus:ring-2 focus:ring-pink-500 focus:ring-offset-2"
            >
              Add
            </button>
          </div>


        <hr className="my-4" />

        <div>
          <h2 className="mb-4 text-center text-2xl font-semibold">Select Dietary Preferences</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            {preferences.map(preference => (
              <div key={preference} className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id={preference}
                  checked={dietaryPreferences.includes(preference)}
                  onChange={() => handlePreferenceChange(preference)}
                  className="h-4 w-4 rounded border-gray-300 text-pink-600 focus:ring-pink-500"
                />
                <label htmlFor={preference} className="text-sm font-medium text-gray-700">
                  {preference}
                </label>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h2 className="mb-4 text-center text-2xl font-semibold">Select Meal Type</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            {mealTypes.map(type => (
              <div key={type} className="flex items-center space-x-2">
                <input
                  type="radio"
                  id={type}
                  name="mealType"
                  checked={mealType === type}
                  onChange={() => setMealType(type)}
                  className="h-4 w-4 rounded border-gray-300 text-pink-600 focus:ring-pink-500"
                />
                <label htmlFor={type} className="text-sm font-medium text-gray-700">
                  {type}
                </label>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h2 className="mb-4 text-center text-2xl font-semibold">Enter Cooking Time (in minutes)</h2>
          <input
            type="number"
            value={cookingTime}
            onChange={(e) => setCookingTime(Number(e.target.value))}
            className="mt-2 w-full rounded-md border-gray-300 p-2 focus:ring-pink-500"
            placeholder="Enter cooking time"
          />
        </div>

        <button
          onClick={() => onGenerate(selectedIngredients, dietaryPreferences, mealType, Number(cookingTime))}
          className="mt-6 w-full rounded-md bg-pink-500 px-4 py-2 text-white hover:bg-pink-600 focus:outline-none focus:ring-2 focus:ring-pink-500 focus:ring-offset-2"
        >
          Get Recipe
        </button>
      </div>
    </div>
  )
}
