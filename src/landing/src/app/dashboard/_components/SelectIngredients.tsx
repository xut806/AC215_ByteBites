"use client"

import React, { useState } from "react"

interface SelectIngredientsProps {
  onGenerate: () => void
}

export default function Component({ onGenerate }: SelectIngredientsProps) {
  const [selectedIngredients, setSelectedIngredients] = useState<string[]>([])
  const [dietaryPreferences, setDietaryPreferences] = useState<string[]>([])

  const ingredients = ["Tomatoes", "Chicken", "Bell Peppers", "Onions", "Rice"]
  const preferences = ["Vegetarian", "Vegan", "GlutenFree", "DairyFree"]

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

  return (
    <div className="rounded-lg bg-white p-6 shadow-md">
      <h2 className="mb-4 text-center text-2xl font-bold">Select Ingredients</h2>
      <div className="space-y-10">
        <div className="grid gap-4 sm:grid-cols-2">
          {ingredients.map(ingredient => (
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

        <hr className="my-4" />

        <div>
          <h2 className="mb-4 text-center text-2xl font-bold">Select Dietary Preferences</h2>
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

        <button
          onClick={onGenerate}
          className="mt-6 w-full rounded-md bg-pink-500 px-4 py-2 text-white hover:bg-pink-600 focus:outline-none focus:ring-2 focus:ring-pink-500 focus:ring-offset-2"
        >
          Get Recipe
        </button>
      </div>
    </div>
  )
}
