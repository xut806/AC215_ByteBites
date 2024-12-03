"use client"

import React, { useEffect, useState } from "react"
import { Input } from "@/components/ui/input"

type Nutrient = {
  value: number;
  unit: string;
};

type NutritionData = Record<string, Nutrient>;

type NutritionAnalysisProps = {
  ingredients: string | string[];
};

const NutritionAnalysis: React.FC<NutritionAnalysisProps> = ({ ingredients }) => {
  const [nutritionData, setNutritionData] = useState<NutritionData | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    const fetchNutritionData = async () => {
      if (ingredients) {
        try {
          const response = await fetch("http://localhost:9000/nutrition", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ ingredients: Array.isArray(ingredients) ? ingredients : ingredients.split(", ") }),
          });

          if (response.ok) {
            const data = await response.json();
            setNutritionData(data.nutrition_data);
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

  const filteredData = nutritionData
    ? Object.entries(nutritionData).filter(([key]) =>
        key.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : [];

  return (
    <div className="rounded-lg bg-white p-6 shadow-md">
      <h2 className="mb-4 text-center text-2xl font-bold">Nutrition Analysis</h2>
      {loading ? (
        <p className="text-center text-lg text-gray-600">Loading nutrition data...</p>
      ) : (
        <div>
          <Input
            type="text"
            placeholder="Search for a nutrient..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="mb-4"
          />
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Nutrient
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Value
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Unit
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredData.map(([key, { value, unit }]) => (
                  <tr key={key}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{key}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{value}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{unit}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default NutritionAnalysis;
