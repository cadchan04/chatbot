# imports
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
import openai
import os
import pickle
import streamlit as st
import shelve

# load chat history using pickle file
def load_history():
    if os.path.exists('chat_history.pkl'):
        with open('chat_history.pkl', 'rb') as pfile:
            messages = pickle.load(pfile)
        pfile.close()
        return messages
    else:
        return []
    
# update and sae new chat history with st.session_state's messages
def save_history(messages):
    with open('chat_history.pkl', 'wb') as pfile: # open a text file
        pickle.dump(messages, pfile) # serialize the list
    pfile.close()

def main():
    # set up
    load_dotenv()
    
    # avatars for user and assistant
    USER_AVATAR = '😀'
    BOT_AVATAR = '🤖'
    
    # store openai model
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-3.5-turbo"
    
    # initialize chat history (chat history deletes every rerun)
    if "messages" not in st.session_state:
        st.session_state.messages = load_history()
        
    # store delete button state
    if "delete_button" not in st.session_state:
        st.session_state.delete_button = False
    if "delete_yes_button" not in st.session_state:
        st.session_state.delete_yes_button = False
    if "delete_no_button" not in st.session_state:
        st.session_state.delete_no_button = False
        
    # create model
    client = OpenAI()
    
    # title of Streamlit
    st.title("Hi! I'm your Personal Chatbot!")
    with st.sidebar:
        delete = st.button("Delete chat history")
        if delete:
            st.session_state.delete_button = True
        if st.session_state.delete_button:
            st.error("Are you sure you want to delete? This action cannot be undone")
            # left and right column for yes and no button
            col1, col2 = st.columns([1,1])
            with col1:
                yes = st.button("Yes")
                if yes:
                    st.session_state.delete_yes_button = True
                if st.session_state.delete_yes_button:
                    st.session_state.messages = []
                    save_history([])
            with col2:
                no = st.button("No")
                if no:
                    st.session_state.delete_no_button = True
                if st.session_state.delete_no_button:
                    print("cancelled")
    
    # load previous chat history
    for message in st.session_state.messages:
        curr_avatar = ""
        if message["role"] == "user":
            curr_avatar = USER_AVATAR
        else:
            curr_avatar = BOT_AVATAR
        with st.chat_message(message["role"], avatar=curr_avatar):
            st.markdown(message["content"])
            
    # input textbox
    prompt = st.chat_input("Ask me a question...")
    if prompt:
        # add user prompt into messages history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(prompt)
        
        # create and add bot answer into messages history
        with st.chat_message("assistant", avatar=BOT_AVATAR): # with st.chat_message creates a chat container
            messages = []
            for m in st.session_state.messages:
                messages.append({"role": m["role"], "content": m["content"]})
            stream = client.chat.completions.create(
                model=st.session_state.openai_model,
                messages=messages,
                stream=True
            )
            response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
        
    # update chat history to pickle file
    save_history(st.session_state.messages)
    
if __name__ == "__main__":
    main()