"use client"

import React, { useState, useEffect } from "react"
import dynamic from 'next/dynamic'
import loadingAnimation from "../../../../public/loading.json"

// Dynamically import Lottie with SSR disabled
const Lottie = dynamic(() => import('lottie-react'), { ssr: false })

interface GenerateRecipeProps {
  onStartOver: () => void
  selectedIngredients: string[]
  dietaryPreferences: string[]
  mealType: string
  cookingTime: number
  onGoToNutrition: () => void;
}

export default function Component({ onStartOver, selectedIngredients, dietaryPreferences, mealType, cookingTime, onGoToNutrition }: GenerateRecipeProps) {
  const [recipe, setRecipe] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const generateRecipe = async () => {
      setLoading(true)
      try {
        // const response = await fetch("http://localhost:9000/llm", {
        //   method: "POST",
        //   headers: {
        //     "Content-Type": "application/json",
        //   },
        //   body: JSON.stringify({
        //     ingredients: selectedIngredients.join(", "),
        //     dietary_preference: dietaryPreferences.join(", "),
        //     meal_type: mealType,
        //     cooking_time: cookingTime,
        //   }),
        // })

        // TODO: replace this
        // const response = await fetch("/api/llm", {
        //   method: "POST",
        //   headers: {
        //     "Content-Type": "application/json",
        //   },
        //   body: JSON.stringify({
        //     ingredients: selectedIngredients.join(", "),
        //     dietary_preference: dietaryPreferences.join(", "),
        //     meal_type: mealType,
        //     cooking_time: cookingTime,
        //   }),
        // })

        const response = await fetch("http://34.82.146.148:8080/generate/", { // Updated endpoint
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            text: `please write a ${dietaryPreferences.join(", ")}, ${mealType} meal recipe that takes approximately ${cookingTime} minutes and includes the following ingredients: ${selectedIngredients.join(", ")}. Include the instructions only.`,
            
            
          }),
        })

        if (response.ok) {
          const data = await response.json()
          // setRecipe(data.recipe)
          // LLM VM version:
          console.log(data); 
          console.log("Generated Recipe:", data.generated_text); 
          setRecipe(data.generated_text);
        } else {
          console.error("Failed to generate recipe", response.statusText)
        }
      } catch (error) {
        console.error("Error:", error)
      } finally {
        setLoading(false)
      }
    }

    generateRecipe()
  }, [selectedIngredients, dietaryPreferences, mealType, cookingTime])

  return (
    <div className="rounded-lg bg-white p-6 shadow-md">
      <h2 className="mb-4 text-center text-2xl font-bold">Your Recipe</h2>
      {loading ? (
        <div className="flex justify-center">
          <Lottie animationData={loadingAnimation} className="w-24 h-24" />
        </div>
      ) : (
        <div className="space-y-6">
          <div className="rounded-lg bg-gray-50 p-5">
            <p className="text-gray-600">
              {recipe ? (
                recipe
                  .split("Instructions:")[1]
                  .split("\n")
                  .map((step, index) => (
                    <span key={index} className="block">
                      {step.trim()}
                    </span>
                  ))
              ) : (
                "(Recipe content would be displayed here after generation by the LLM)"
              )}
            </p>
          </div>
          <button
            onClick={() => {
              onGoToNutrition();
            }}
            className="w-full rounded-md bg-pink-500 px-4 py-2 text-white hover:bg-pink-600 focus:outline-none focus:ring-2 focus:ring-pink-500 focus:ring-offset-2"
          >
            Show Nutrition Analysis
          </button>
        </div>
      )}
    </div>
  )
}

