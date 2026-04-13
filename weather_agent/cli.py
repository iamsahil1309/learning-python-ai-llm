from openai import OpenAI
import json
import requests
from pydantic import BaseModel, Field
from typing import Optional
import os


client = OpenAI(
    api_key="AIzaSyAiCw3LvlgV2nlUcE5oAXm6ojnDkCZVpa8",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

WEATHER_API_KEY = "d19fef121990e40610dd36d828cc9eac"

def run_command(cmd : str) :
    result = os.system(cmd)
    return result

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    res = requests.get(url).json()

    return {
        "temp": res["main"]["temp"],
        "feels_like": res["main"]["feels_like"],
        "humidity": res["main"]["humidity"],
        "desc": res["weather"][0]["description"]
    }


TOOLS = {
    "get_weather": get_weather,
    "run_command": run_command
}

# =========================
# SYSTEM PROMPT (IMPORTANT FIXED VERSION)
# =========================
SYSTEM_PROMPT = """
You are an AI CLI agent.

You must respond ONLY in ONE JSON object per message.

Format:
{
  "step": "PLAN" | "TOOL" | "OUTPUT",
  "content": "string",
  "tool": "optional tool name",
  "input": "optional tool input"
}

Rules:
- Only one JSON object per response
- One step per response
- PLAN can happen multiple times across messages
- TOOL must call only from available tools
- After TOOL result, continue reasoning
- Final step must be OUTPUT

Available tools:
1. get_weather (input: city name)
2. run_command (input: shell command)

Example:
User: weather in Delhi
{"step":"PLAN","content":"User wants weather info"}
{"step":"TOOL","tool":"get_weather","input":"Delhi"}
{"step":"PLAN","content":"Received weather data"}
{"step":"OUTPUT","content":"Final weather summary"}
"""

# =========================
# PYDANTIC MODEL
# =========================
class AgentOutput(BaseModel):
    step: str = Field(..., description="PLAN | TOOL | OUTPUT")
    content: Optional[str] = None
    tool: Optional[str] = None
    input: Optional[str] = None


# =========================
# MEMORY
# =========================
message_history = [{"role": "system", "content": SYSTEM_PROMPT}]

# =========================
# USER INPUT
# =========================
user_query = input("👉 ")
message_history.append({"role": "user", "content": user_query})


# =========================
# AGENT LOOP
# =========================
while True:
    response = client.chat.completions.parse(
        model="gemini-2.5-flash",
        response_format=AgentOutput,
        messages=message_history
    )

    parsed = response.choices[0].message.parsed

    step = parsed.step
    content = parsed.content

    # Save assistant raw response
    message_history.append({
        "role": "assistant",
        "content": response.choices[0].message.content
    })

    # =========================
    # PLAN STEP
    # =========================
    if step == "PLAN":
        print("🧠", content)
        continue

    # =========================
    # TOOL STEP
    # =========================
    elif step == "TOOL":
        tool_name = parsed.tool
        tool_input = parsed.input

        print(f"🛠 Using tool: {tool_name}")

        if tool_name in TOOLS:
            result = TOOLS[tool_name](tool_input)
        else:
            result = {"error": "Tool not found"}

        # Send tool result back to model
        message_history.append({
            "role": "user",
            "content": f"Tool result: {result}"
        })

        continue

    # =========================
    # OUTPUT STEP
    # =========================
    elif step == "OUTPUT":
        print("🤖", content)
        break