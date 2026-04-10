from openai import OpenAI
import json
import requests
import time

# ---------------- CONFIG ----------------

client = OpenAI(
    api_key="AIzaSyBA2CmScTwY2EAs6UCuvugpot5uTUUG0FE",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# ---------------- TOOL ----------------

def get_weather(city: str):
    try:
        url = f"https://wttr.in/{city.lower()}?format=%C+%t"
        response = requests.get(url)

        if response.status_code == 200:
            return f"The weather in {city} is {response.text}"

        return "Weather API failed"
    except Exception as e:
        return f"Error: {str(e)}"


available_tools = {
    "get_weather": get_weather
}

# ---------------- SYSTEM PROMPT ----------------

SYSTEM_PROMPT = """
You are a strict step-by-step AI agent.

You MUST return ONLY ONE valid JSON object per response.

FLOW:
START → PLAN → TOOL → OBSERVE → OUTPUT

RULES:
- One step per response only
- Never return list or multiple JSON objects
- Never use tools except "get_weather"
- Never use "google_search" or any other tool
- After OBSERVE, you MUST produce OUTPUT soon (max 1 PLAN step allowed)
- Do NOT loop PLAN forever

TOOL AVAILABLE:
get_weather(city: str)

OUTPUT FORMAT:
{
 "step": "START" | "PLAN" | "TOOL" | "OUTPUT",
 "content": "string",
 "tool": "string",
 "input": "string"
}
"""

# ---------------- HELPERS ----------------

def safe_parse(text):
    try:
        data = json.loads(text)

        if isinstance(data, list):
            data = data[0]

        if not isinstance(data, dict):
            return None

        return data
    except:
        return None


def call_llm(messages):
    retries = 3
    delay = 5

    for i in range(retries):
        try:
            response = client.chat.completions.create(
                model="gemini-3-flash-preview",
                response_format={"type": "json_object"},
                messages=messages
            )
            return response.choices[0].message.content

        except Exception as e:
            print(f"⚠️ Retry {i+1} after {delay}s...")
            time.sleep(delay)
            delay *= 2

    raise Exception("API failed")


# ---------------- MAIN ----------------

print("\n🤖 Weather Agent Started\n")

message_history = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

user_query = input("👉🏽 ")
message_history.append({"role": "user", "content": user_query})

max_steps = 8
last_steps = []

for _ in range(max_steps):

    raw = call_llm(message_history)
    print("\n📦 RAW:", raw)

    parsed = safe_parse(raw)

    if not parsed:
        print("❌ Invalid JSON")
        break

    message_history.append({"role": "assistant", "content": raw})

    step = parsed.get("step")
    last_steps.append(step)

    if len(last_steps) > 5:
        last_steps.pop(0)

    # detect infinite PLAN loop
    if last_steps.count("PLAN") >= 5:
        print("⚠️ Too many PLAN steps → stopping")
        break

    # ---------------- START ----------------
    if step == "START":
        print(f"START  → {parsed.get('content')}")

    # ---------------- PLAN ----------------
    elif step == "PLAN":
        print(f"PLAN   → {parsed.get('content')}")

    # ---------------- TOOL ----------------
    elif step == "TOOL":
        tool = parsed.get("tool")
        tool_input = parsed.get("input")

        print(f"TOOL   → {tool}({tool_input})")

        if tool == "get_weather":
            result = get_weather(tool_input)
        else:
            result = "❌ Invalid tool used"

        print(f"RESULT → {result}")

        message_history.append({
            "role": "developer",
            "content": json.dumps({
                "step": "OBSERVE",
                "tool": tool,
                "input": tool_input,
                "output": result
            })
        })

    # ---------------- OUTPUT ----------------
    elif step in ["OUTPUT", "FINAL"]:
        print(f"\nOUTPUT → {parsed.get('content')}")
        break

    else:
        print("❌ Unknown step → stopping")
        break

    time.sleep(2)

else:
    print("⚠️ Max steps reached")