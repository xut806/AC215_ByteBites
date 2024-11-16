"use client"

import React from "react"

interface GenerateRecipeProps {
  onStartOver: () => void
}

export default function Component({ onStartOver }: GenerateRecipeProps) {
  const fakeRecipe = "Based on your selected ingredients and preferences, here's your recipe:"

  return (
    <div className="rounded-lg bg-white p-6 shadow-md">
      <h2 className="mb-4 text-center text-2xl font-bold">Your Recipe</h2>
      <p className="mb-6 text-center text-lg text-gray-600">{fakeRecipe}</p>
      <div className="space-y-6">
        <div className="rounded-lg bg-gray-50 p-6">
          <p className="text-gray-600">
            (Recipe content would be displayed here after generation by the LLM)
          </p>
        </div>
        <button
          onClick={onStartOver}
          className="w-full rounded-md bg-pink-500 px-4 py-2 text-white hover:bg-pink-600 focus:outline-none focus:ring-2 focus:ring-pink-500 focus:ring-offset-2"
        >
          Start Over
        </button>
      </div>
    </div>
  )
}
