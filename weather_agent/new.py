from openai import OpenAI
import json
import requests

client = OpenAI(
    api_key="AIzaSyArvZvzC_9CabFd3EyFCH_wOqRUfxqMJUs",
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


message_history = [{"role": "system", "content": SYSTEM_PROMPT}]

user_query = input("👉 ")
message_history.append({"role": "user", "content": user_query})

while True:
    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        response_format={"type": "json_object"},
        messages=message_history
    )

    raw = response.choices[0].message.content
    message_history.append({"role": "assistant", "content": raw})

    parsed = json.loads(raw) #string -> dictionary

    step = parsed.get("step")
    content = parsed.get("content")

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