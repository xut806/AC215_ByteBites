'use client'

import React, { useState } from 'react'
import Image from 'next/image'

interface InitialStepProps {
  onUpload: (event: React.ChangeEvent<HTMLInputElement>) => void
  onCooking: () => void
}

function InitialStep({ onUpload, onCooking }: InitialStepProps) {
  return (
    <>
      <p className="mt-1 text-lg text-gray-600 text-center">
        Welcome to ByteBites!<br />
        We are your trustworthy cooking assistant that helps you come up<br />
        with delicious, nutritious recipes that best utilize your groceries.
      </p>
      <div className="mt-8 flex space-x-4">
        <button 
          className="px-6 py-2 text-white bg-pink-600 rounded-md hover:bg-pink-700 transition duration-300"
          onClick={() => document.getElementById('fileUpload')?.click()}
        >
          Upload grocery receipt
        </button>
        <input
          id="fileUpload"
          type="file"
          accept="image/*"
          className="hidden"
          onChange={onUpload}
        />
        <button 
          className="px-6 py-2 text-white bg-pink-600 rounded-md hover:bg-pink-700 transition duration-300"
          onClick={onCooking}
        >
          Let&apos;s get cooking!
        </button>
      </div>
    </>
  )
}

interface SelectIngredientsStepProps {
  ingredients: string[]
  selectedIngredients: string[]
  setSelectedIngredients: React.Dispatch<React.SetStateAction<string[]>>
  dietaryPreferences: {
    vegetarian: boolean
    vegan: boolean
    glutenFree: boolean
    dairyFree: boolean
  }
  setDietaryPreferences: React.Dispatch<React.SetStateAction<{
    vegetarian: boolean
    vegan: boolean
    glutenFree: boolean
    dairyFree: boolean
  }>>
  onGetRecipe: () => void
}

function SelectIngredientsStep({
  ingredients,
  selectedIngredients,
  setSelectedIngredients,
  dietaryPreferences,
  setDietaryPreferences,
  onGetRecipe
}: SelectIngredientsStepProps) {
  const handleIngredientSelection = (ingredient: string) => {
    setSelectedIngredients((prev) =>
      prev.includes(ingredient)
        ? prev.filter((item) => item !== ingredient)
        : [...prev, ingredient]
    )
  }

  // Define a type for the keys of dietaryPreferences
  type DietaryPreferenceKey = 'vegetarian' | 'vegan' | 'glutenFree' | 'dairyFree';

  const handlePreferenceChange = (preference: DietaryPreferenceKey) => {
    setDietaryPreferences((prev) => ({ ...prev, [preference]: !prev[preference] }))
  }

  return (
    <div className="mt-8 bg-white p-6 rounded-lg shadow-md w-full max-w-md">
      <h2 className="text-2xl font-bold mb-4 text-center">Select Ingredients</h2>
      <div className="grid grid-cols-2 gap-4 mb-6">
        {ingredients.map((ingredient) => (
          <div key={ingredient} className="flex items-center space-x-2">
            <input
              type="checkbox"
              id={ingredient}
              checked={selectedIngredients.includes(ingredient)}
              onChange={() => handleIngredientSelection(ingredient)}
              className="rounded text-pink-600 focus:ring-pink-500"
            />
            <label htmlFor={ingredient} className="text-gray-700">{ingredient}</label>
          </div>
        ))}
      </div>
      <h2 className="text-2xl font-bold mb-4 text-center">Select Dietary Preferences</h2>
      <div className="flex flex-wrap gap-4 mb-6">
        {Object.entries(dietaryPreferences).map(([key, value]) => (
          <div key={key} className="flex items-center space-x-2">
            <input
              type="checkbox"
              id={key}
              checked={value}
              onChange={() => handlePreferenceChange(key as DietaryPreferenceKey)}
              className="rounded text-pink-600 focus:ring-pink-500"
            />
            <label htmlFor={key} className="text-gray-700">{key.charAt(0).toUpperCase() + key.slice(1)}</label>
          </div>
        ))}
      </div>
      <button 
        onClick={onGetRecipe}
        className="w-full px-6 py-2 text-white bg-pink-600 rounded-md hover:bg-pink-700 transition duration-300"
      >
        Get Recipe
      </button>
    </div>
  )
}

interface RecipeGeneratedStepProps {
  onStartOver: () => void
}

function RecipeGeneratedStep({ onStartOver }: RecipeGeneratedStepProps) {
  return (
    <div className="mt-8 bg-white p-6 rounded-lg shadow-md w-full max-w-md">
      <h2 className="text-2xl font-bold mb-4 text-center">Your Recipe</h2>
      <p className="text-center text-gray-600 mb-6">
        Based on your selected ingredients and preferences, here&apos;s your recipe:
      </p>
      <p className="text-center text-gray-600 mb-6">
        (Recipe content would be displayed here after generation by the LLM)
      </p>
      <button 
        onClick={onStartOver}
        className="w-full px-6 py-2 text-white bg-pink-600 rounded-md hover:bg-pink-700 transition duration-300"
      >
        Start Over
      </button>
    </div>
  )
}

export default function Dashboard() {
  const [step, setStep] = useState('initial')
  const [ingredients, setIngredients] = useState<string[]>([])
  const [selectedIngredients, setSelectedIngredients] = useState<string[]>([])
  const [dietaryPreferences, setDietaryPreferences] = useState({
    vegetarian: false,
    vegan: false,
    glutenFree: false,
    dairyFree: false,
  })

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      // TODO: Implement OCR processing here
      // For now, we'll simulate the OCR result
      const mockIngredients = ['Tomatoes', 'Onions', 'Chicken', 'Rice', 'Bell Peppers']
      setIngredients(mockIngredients)
      setStep('selectIngredients')
    }
  }

  const handleGetRecipe = () => {
    // TODO: Implement LLM call to generate recipe
    console.log('Selected Ingredients:', selectedIngredients)
    console.log('Dietary Preferences:', dietaryPreferences)
    setStep('recipeGenerated')
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
      <div className="flex items-center justify-center">
        <Image src="/img/logo.png" alt="ByteBites Icon" width={300} height={300} />
      </div>
      
      {step === 'initial' && (
        <InitialStep
          onUpload={handleFileUpload}
          onCooking={() => setStep('selectIngredients')}
        />
      )}

      {step === 'selectIngredients' && (
        <SelectIngredientsStep
          ingredients={ingredients}
          selectedIngredients={selectedIngredients}
          setSelectedIngredients={setSelectedIngredients}
          dietaryPreferences={dietaryPreferences}
          setDietaryPreferences={setDietaryPreferences}
          onGetRecipe={handleGetRecipe}
        />
      )}

      {step === 'recipeGenerated' && (
        <RecipeGeneratedStep onStartOver={() => setStep('initial')} />
      )}
    </div>
  )
}
