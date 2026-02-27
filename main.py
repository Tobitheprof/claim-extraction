import re
import os
from fastapi import FastAPI, UploadFile, File
import json
from pydantic import BaseModel

from app import generate_claims, get_keywords_rank, get_similar_claims,get_claims
from fastapi.middleware.cors import CORSMiddleware
import re

app = FastAPI()

class Item(BaseModel):
    file: str
    start_date:str
    end_date:str

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "https://dap-claim-extraction.onrender.com"
    "https://claim-extraction.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/extract")
async def analyze_text(file: UploadFile = File(...)):
    try:
        content = await file.read()

        text = content.decode("latin-1")

        claims = generate_claims(text)
        print('Generated claims raw output:', claims)

        # Extract JSON from the response - handles ```json ... ``` wrapper or raw JSON
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', claims)
        if json_match:
            json_string = json_match.group(1).strip()
        else:
            json_string = claims.strip()

        # Wrap in {} if the response starts with "output_format" (not a full JSON object)
        if not json_string.startswith('{'):
            json_string = '{' + json_string + '}'

        print('Parsed JSON string:', json_string)
        output_format = json.loads(json_string)

        return output_format

    except Exception as e:
        print(f"Error extracting claims: {e}")
        error_message = {"output_format": [
                            {
                            "Title": None,
                            "Claim": None,
                            "Reasoning": None
                            }
                        ]}
        return error_message

@app.post("/keywords/claims")
async def extract_keywords(item: Item):
    try:
        claims = get_claims(item.start_date, item.end_date)
        keywords = get_similar_claims(claims)
        json_string = re.sub(r'``json|`','',keywords)
        print(f'Keywords: {json_string}')

        return json.loads(json_string)

    except Exception as e:
        error_message = {"error": str(e)}
        return error_message

@app.post("/keywords/rank")
async def extract_keywords(item: Item):
    try:
        claims = get_claims(item.start_date, item.end_date)
        keywords = get_similar_claims(claims)
        json_string = re.sub(r'``json|`','',keywords)
        print(f'Keywords: {json_string}')

        ranked_keywords = get_keywords_rank(json_string)
        json_string = re.sub(r'``json|`','',ranked_keywords)
        print(f'Keywords: {json_string}')

        return json.loads(json_string)

    except Exception as e:
        error_message = {"error": str(e)}
        return error_message