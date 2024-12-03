"use client"

import React, { useEffect, useState } from "react"

type NutritionAnalysisProps = {
  ingredients: string | string[]; // Update type to allow both string and string array
};

const NutritionAnalysis: React.FC<NutritionAnalysisProps> = ({ ingredients }) => { // Accept ingredients as a prop
  const [nutritionData, setNutritionData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchNutritionData = async () => {
      if (ingredients) {
        try {
          const response = await fetch("http://localhost:9000/nutrition", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ ingredients: Array.isArray(ingredients) ? ingredients : ingredients.split(", ") }), // Ensure ingredients is an array
          });

          if (response.ok) {
            const data = await response.json();
            setNutritionData(data);
          } else {
            console.error("Failed to fetch nutrition data");
          }
        } catch (error) {
          console.error("Error:", error);
        } finally {
          setLoading(false);
        }
      }
    };

    fetchNutritionData();
  }, [ingredients]);

  return (
    <div className="rounded-lg bg-white p-6 shadow-md">
      <h2 className="mb-4 text-center text-2xl font-bold">Nutrition Analysis</h2>
      {loading ? (
        <p className="text-center text-lg text-gray-600">Loading nutrition data...</p>
      ) : (
        <div>
          {nutritionData ? (
            <pre>{JSON.stringify(nutritionData, null, 2)}</pre> // Display nutrition data
          ) : (
            <p>No nutrition data available.</p>
          )}
        </div>
      )}
    </div>
  );
};

export default NutritionAnalysis;
