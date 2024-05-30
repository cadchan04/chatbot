from dotenv import load_dotenv, find_dotenv
import openai
import os


# function to configure environments and load in api key
def configure():
    load_dotenv(find_dotenv())
    
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key is None:
        print(api_key)
        raise ValueError("OpenAI key not found!")
    openai.api_key = api_key


# main function
def main():
    # call configure to set up api key
    configure()
    
    # code
    chat_log = [] # store conversation
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit", "bye"]:
            break
        else:
            chat_log.append({"role": "user", "content": user_input})
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=chat_log
            )
            assistant_response = response['choices'][0]['message']['content']
            print("ChatGPT: ", assistant_response.strip("\n").strip())
            chat_log.append({"role": "assistant", "content": assistant_response.strip("\n").strip()})
            
if __name__ == "__main__":   
    main()
    