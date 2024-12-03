from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from api.utils.nutrition_utils import (
    get_nutrition_info,
    aggregate_nutrition_info_with_units,
)

router = APIRouter()


class NutritionRequest(BaseModel):
    ingredients: list


@router.post("/nutrition")
async def get_nutritional_info(request: NutritionRequest):
    try:
        nutrition_data = get_nutrition_info(request.ingredients)
        overall_nutrition = aggregate_nutrition_info_with_units(nutrition_data)
        return {"nutrition_data": overall_nutrition}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
