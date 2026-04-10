from openai import OpenAI


client = OpenAI(
    api_key="AIzaSyCjBLh7jvGRerUCbzduThCJ_HKEhr-y5_M",
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