#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers.ocr import router as ocr_router
from api.routers.llm import router as llm_router
from api.routers.nutrition import router as nutrition_router

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the OCR and LLM routers
app.include_router(ocr_router)
app.include_router(llm_router)
app.include_router(nutrition_router)
