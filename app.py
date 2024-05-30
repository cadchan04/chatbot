from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
import openai
import os
import streamlit as st
import shelve

def main():
    # configure model and messages
    load_dotenv()
    
    st.title("Personal Chatbot")
    USER_AVATAR = "🤩"
    BOT_AVATAR = "🤖"
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # make sure model is initialized in session state
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"
    
    # load chat history from shelve file
    def load_chat_history():
        with shelve.open("chat_history") as db:
            return db.get("messages", [])
    
    # save chat history to shelve file
    def save_chat_history(messages):
        with shelve.open("chat_history") as db:
            db["messages"] = messages
    
    # initialize or load chat history
    if "messages" not in st.session_state:
        st.session_state.messages = load_chat_history()
        
    # sidebar with a button to delete chat history
    if "delete_button" not in st.session_state:
        st.session_state["delete_button"] = False
    if "no_delete_button" not in st.session_state:
        st.session_state["no_delete_button"] = False
    if "yes_delete_button" not in st.session_state:
        st.session_state["yes_delete_button"] = False
    
    # sidebar to delete chat history
    with st.sidebar:            
        if st.button("Delete Chat History"):
            st.session_state["delete_button"] = True
        
        if st.session_state["delete_button"]:            
            st.error("Are you sure you want to DELETE chat history? This action CANNOT be undone.")
            
            left_col, right_col = st.columns([1,1])
            with left_col:
                clicked = st.button("No")
                if clicked:
                    st.session_state["no_delete_button"] = True
                if st.session_state["no_delete_button"]:
                    st.session_state.messages = []
 
            with right_col:
                clicked = st.button("Yes")
                if clicked:
                    st.session_state["yes_delete_button"] = True
                if st.session_state["yes_delete_button"]:
                    st.session_state.messages = []
                    save_chat_history([])
                            
    # main chat interface
    for message in st.session_state.messages:
        avatar = ""
        if message["role"] == "user":
            avatar = USER_AVATAR
        else:
            avatar = BOT_AVATAR
        with st.chat_message("user", avatar=avatar):
            st.markdown(message["content"])
            
    prompt = st.chat_input("How can I assist you?")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(prompt)
            
        with st.chat_message("assistant", avatar=BOT_AVATAR):
            placeholder = st.empty()
            full_response = ""
            
            for response in client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=st.session_state["messages"],
                stream=True,
            ):
                full_response += response.choices[0].delta.content or ""
                placeholder.markdown(full_response + "|")
            placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
    # save chat history after every interaction
    save_chat_history(st.session_state.messages)
    
if __name__ == "__main__":
    main()