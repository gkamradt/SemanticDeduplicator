# utils.py
import openai
import json
import time

def call_llm(system_prompt="You are a helpful assistant.", human_prompt="Hello!", function_schema=[], model="gpt-4-0613"):
    params = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": human_prompt}
        ]
    }

    max_attempts = 3
    backoff_factor = 1.5

    for attempt in range(max_attempts):
        try:
            if function_schema:
                params["functions"] = function_schema
                params["function_call"] = {"name": function_schema[0]['name']}
                completion = openai.ChatCompletion.create(**params)

                return json.loads(completion.choices[0]['message']['function_call']['arguments'])['items']
            else:
                completion = openai.ChatCompletion.create(**params)
                return completion.choices[0].message['content']
        except openai.error.ServiceUnavailableError:
            if attempt < max_attempts - 1:  # no need to sleep on the last attempt
                sleep_time = backoff_factor * (2 ** attempt)
                time.sleep(sleep_time)
            else:
                raise
    
def get_embedding(string):
    embedding = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=string
    )
    return embedding['data'][0]['embedding']