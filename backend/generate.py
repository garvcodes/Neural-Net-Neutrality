from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from google import genai
import os

from dotenv import load_dotenv
import os
load_dotenv(".env", override=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai_client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# You can store conversation histories per model here if you want continuity
conversation_history = {
    "openai": [],
    "gemini": []
}

@app.post("/battle")
async def battle(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return {"error": "Missing prompt"}

    # Append user prompt to conversation
    conversation_history["openai"].append({"role": "user", "content": prompt})
    conversation_history["gemini"].append({"role": "user", "content": prompt})

    try:
        # OpenAI response
        openai_response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation_history["openai"]
        )
        openai_text = openai_response.choices[0].message.content

        # Gemini response
        gemini_response = gemini_client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        gemini_text = gemini_response.text

        # Add responses back into conversation for continuity
        conversation_history["openai"].append({"role": "assistant", "content": openai_text})
        conversation_history["gemini"].append({"role": "assistant", "content": gemini_text})

        return {"openai": openai_text, "gemini": gemini_text}

    except Exception as e:
        print("Error:", e)
        return {"error": str(e)}