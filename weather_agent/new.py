from openai import OpenAI
import json
import requests
from pydantic import BaseModel, Field
from typing import Optional


client = OpenAI(
    api_key="AIzaSyDUA1kfP7qwgxxInUApLnbIjrSdC7XSoY0",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

WEATHER_API_KEY = "d19fef121990e40610dd36d828cc9eac"

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    res = requests.get(url).json()

    return {
        "temp": res["main"]["temp"],
        "feels_like": res["main"]["feels_like"],
        "humidity": res["main"]["humidity"],
        "desc": res["weather"][0]["description"]
    }


SYSTEM_PROMPT = """
You are a weather AI agent.

You must respond ONLY in JSON:
{ "step": "PLAN" | "TOOL" | "OUTPUT", "content": "string" }

Steps:
- PLAN → reasoning
- TOOL → call weather API
- OUTPUT → final answer

Rules:
- First understand user query
- If weather info needed → call TOOL
- TOOL format:
  { "step": "TOOL", "content": "get_weather:city_name" }
- After TOOL, you will receive data
- Then continue PLAN
- Finally give OUTPUT

Example:
User: weather in Delhi
PLAN: user wants weather
PLAN: need to fetch data
TOOL: get_weather:Delhi
PLAN: received data
OUTPUT: final weather explanation
"""

class MyOutputFormat(BaseModel) :
    step : str = Field(..., description="The id of the step. Example : PLAN, OUTPUT, TOOL")
    content: Optional[str] = Field(None, description="The optional string content")
    tool : Optional[str] = Field(None, description="The ID of the tool to call.")


message_history = [{"role": "system", "content": SYSTEM_PROMPT}]

user_query = input("👉 ")
message_history.append({"role": "user", "content": user_query})

while True:
    response = client.chat.completions.parse(
        model="gemini-2.5-flash",
        response_format=MyOutputFormat,
        messages=message_history
    )

    raw = response.choices[0].message.content
    message_history.append({"role": "assistant", "content": raw})

    # parsed = json.loads(raw) #string -> dictionary
    parsed = response.choices[0].message.parsed

    step = parsed.step
    content = parsed.content

    if step == "PLAN":
        print("🧠", content)
        continue

    elif step == "TOOL":
        print("🛠 Calling tool:", content)

        # Extract city
        city = content.split(":")[1]
        weather_data = get_weather(city)

        message_history.append({
            "role": "user",
            "content": f"Weather data: {weather_data}"
        })
        continue

    elif step == "OUTPUT":
        print("🤖", content)
        break