from openai import OpenAI


client = OpenAI(
    api_key="AIzaSyAgB0zEgNvVDimuJFeDOfu1whyPyoebUHg",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def main():
    user_query = input("> ")
    response = client.chat.completions.create(
        model = "gemini-3-flash-preview",
        messages= [
            { "role" : "user", "content" : user_query}
        ]
    )

    print(f"🤖: {response.choices[0].message.content}")

main()