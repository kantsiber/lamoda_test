from openai import OpenAI
import json
from retriever import search_hybrid

client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1"
)


tools = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "Ищет информацию в базе знаний академии селлеров Lamoda",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Поисковый запрос"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

def run_agent(user_question):
    messages = [
        {"role": "system", "content": "Ты помощник по академии селлеров Lamoda. Для ответа на вопросы используй инструмент search_knowledge_base. В конце ответа указывай источники."},
        {"role": "user", "content": user_question}
    ]


    while True:
        response = client.chat.completions.create(
            model="llama3.1",
            messages=messages,
            tools=tools
        )

        message = response.choices[0].message


        if message.tool_calls:
            messages.append(message)

            for tool_call in message.tool_calls:
                args = json.loads(tool_call.function.arguments)
                query = args["query"]
                print(f"Поиск: {query}")

                results = search_hybrid(query, top_k=3)

                tool_result = "\n\n".join([
                    f"Источник: {r['source']}\n{r['text']}"
                    for r in results
                ])

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                })

        else:
            print(f"\nОтвет: {message.content}")
            break

run_agent("Как зарегистрироваться в Lamoda Seller?")