import os
import requests
import chainlit as cl
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])

settings = {
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 500,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
}
augmentation_Settings = {
        "model":"gpt-3.5-turbo",
        "temperature":0.7,
        "max_tokens":100,
        "top_p":1,
        "frequency_penalty":0,
        "presence_penalty":0
}
async def augment_prompt(original_prompt):
    augmentation_prompt = f"Create a list of questions, (in english only), that complement the original question.{original_prompt}, the format must be [question1,question2,...]"
    
    response = await client.chat.completions.create(
                messages=[{"role": "system", "content": "You are an assistant that helps to enhance user prompts."},
                  {"role": "user", "content": augmentation_prompt}],**augmentation_Settings
    )
    augmented_prompt = response.choices[0].message.content
    # print("augmented prompt:" +str(augmented_prompt))
    print("Augmented Questions:")
    for i in augmented_prompt.split(','):
        print(i)
    return augmented_prompt.split(",")

def fetch_content_data(prompt, n_items=20):
    try:
        response = requests.get('http://backend_db:82/query/', params={'prompt': prompt, 'n_items': n_items})
        response.raise_for_status()  # Raise HTTPError for bad responses
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        cl.error(f"Failed to fetch content data: {e}")
        return []

def parse_content_data(data):
    contents = []
    for item in data:
        content = item.get('content', '')
        url = item.get('url', '')
        if content and url:
            contents.append(f"Content: {content}\nURL: {url}\n")

    return '\n'.join(contents) if contents else "No relevant content found."

@cl.on_chat_start
def start_chat():
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": "You are GradAdmissionsBuddy, a very helpful assistant that helps students find information about Universities as well as their application information. You only respond based on the data provided by the CONTENT field."}],
    )

@cl.on_message
async def main(message: cl.Message):
    user_query = message.content
    message_history = cl.user_session.get("message_history")
    
    # Augment the user prompt using OpenAI
    augmented_prompt = await augment_prompt(user_query)
    content_data = list()
    # Fetch and parse content data using the augmented prompt
    for question in augmented_prompt:
        raw_data = fetch_content_data(question)
        content_data.append(parse_content_data(raw_data))
    
    # Add user prompt and fetched content data to the message history
    user_message = f"CONTENT: {content_data}\n{user_query}"
    message_history.append({"role": "user", "content": user_message})
    print(user_message)
    # print(message_history)  # For debugging purposes
    
    # Initialize an empty message
    msg = cl.Message(content="")
    await msg.send()
    
    try:
        # Create a chat completion request
        stream = await client.chat.completions.create(
            messages=message_history, stream=True, **settings
        )
        
        # Stream the response tokens
        async for part in stream:
            if token := part.choices[0].delta.content or "":
                await msg.stream_token(token)
        
        # Update message history with the assistant's response
        message_history.append({"role": "assistant", "content": msg.content})
        await msg.update()
    except Exception as e:
        cl.error(f"Failed to process the chat completion: {e}")

    # Save the updated message history
    cl.user_session.set("message_history", message_history)
