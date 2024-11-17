'use client';

import React, { useState } from "react"
import UploadRecipe from "./_components/UploadRecipe"
import SelectIngredients from "./_components/SelectIngredients"
import GenerateRecipe from "./_components/GenerateRecipe"

export default function Component() {
  const [step, setStep] = useState<"main" | "upload" | "select" | "generate">("main")
  const [ingredients, setIngredients] = useState<string[]>([])

  const handleUploadClick = () => setStep("upload")
  const handleSelectClick = () => setStep("select")
  const handleIngredientsReady = (newIngredients: string[]) => {
    setIngredients(newIngredients)
    setStep("select")
  }
  const handleGenerateRecipe = () => setStep("generate")
  const handleStartOver = () => setStep("main")

  return (
    <div className="w-full">
      {step === "main" && (
        <div className="rounded-lg bg-white p-6 shadow-md">
          <h1 className="mb-4 text-center text-2xl font-bold">Welcome to ByteBites!</h1>
          <p className="mb-6 text-center text-lg text-gray-600">
            We are your trustworthy cooking assistant that helps you come up with delicious, nutritious recipes that best utilize your groceries.
          </p>
          <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
            <button
              onClick={handleUploadClick}
              className="rounded-md bg-pink-500 px-4 py-2 text-white hover:bg-pink-600 focus:outline-none focus:ring-2 focus:ring-pink-500 focus:ring-offset-2"
            >
              Upload grocery receipt
            </button>
            <button
              onClick={handleSelectClick}
              className="rounded-md bg-pink-500 px-4 py-2 text-white hover:bg-pink-600 focus:outline-none focus:ring-2 focus:ring-pink-500 focus:ring-offset-2"
            >
              Let&apos;s get cooking!
            </button>
          </div>
        </div>
      )}
      {step === "upload" && <UploadRecipe onIngredientsReady={handleIngredientsReady} />}
      {step === "select" && <SelectIngredients onGenerate={handleGenerateRecipe} ingredients={ingredients} />}
      {step === "generate" && <GenerateRecipe onStartOver={handleStartOver} />}
    </div>
  )
}
