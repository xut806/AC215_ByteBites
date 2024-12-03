"use client"

import React, { useState } from "react"
import Lottie from "lottie-react"
import loadingAnimation from "../../../../public/loading.json"

interface UploadRecipeProps {
  onIngredientsReady: (ingredients: string[]) => void
}

export default function Component({ onIngredientsReady }: UploadRecipeProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleFileUpload = async (file: File) => {
    const formData = new FormData()
    formData.append("file", file)

    setLoading(true)

    try {
      const response = await fetch("http://localhost:9000/ocr", {
        method: "POST",
        body: formData,
      })

      // const response = await fetch("/api/ocr", {
      //   method: "POST",
      //   body: formData,
      // })

      if (response.ok) {
        const data = await response.json()
        console.log("Response data:", data)
        onIngredientsReady(data.ingredients)
      } else {
        console.error("Failed to upload file")
      }
    } catch (error) {
      console.error("Error:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      handleFileUpload(event.target.files[0])
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files[0])
    }
  }

  return (
    <div className="rounded-lg bg-white p-6 shadow-md">
      <h2 className="mb-4 text-center text-2xl font-bold">Upload Grocery Receipt</h2>
      <div
        className={`relative flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-12 transition-colors ${
          isDragging ? "border-pink-500 bg-pink-50" : "border-gray-300"
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {loading ? (
          <div className="flex justify-center">
            <Lottie animationData={loadingAnimation} className="w-24 h-24" />
          </div>
        ) : (
          <>
            <svg
              className="mb-4 h-8 w-8 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
            <label
              htmlFor="file-upload"
              className="mb-2 cursor-pointer text-sm font-medium text-pink-500 hover:text-pink-600"
            >
              Click to upload
            </label>
            <p className="text-sm text-gray-500">or drag and drop</p>
            <input
              id="file-upload"
              type="file"
              className="hidden"
              onChange={handleFileChange}
              accept="image/*"
            />
          </>
        )}
      </div>
    </div>
  )
}
