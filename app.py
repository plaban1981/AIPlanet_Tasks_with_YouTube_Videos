import streamlit as st
from PIL import Image
import requests
import pandas as pd
import os
import json
#
image_path = "yu.jpg"
image = Image.open(image_path)
#

import openai
from youtube_transcript_api import YouTubeTranscriptApi
from langchain.document_loaders import YoutubeLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken
#
import json
import os
from time import time, sleep

#
#from configparser import ConfigParser
#
#ai_for_world_config = ConfigParser()
#
tokenizer = tiktoken.get_encoding('cl100k_base')
#
def tiktoken_len(text):
  tokens = tokenizer.encode(text,disallowed_special=())
  return len(tokens)
#
def split_text(text):
  text_splitter = RecursiveCharacterTextSplitter(chunk_size =1000,
                                                 chunk_overlap=20,
                                                 length_function = tiktoken_len,
                                                 separators = ['\n\n','\n','  ',' '])
  chunks = text_splitter.split_text(text)
  return chunks

#
def gpt3turbo(prompt):
    #
    messages = [{"role":"system",
             "content":"Your are a helpful assistant.",
             },
            ]
    #
    messages.append({"role":"user","content":prompt})
    #print(messages)
    #
    max_retry = 5
    retry = 0
    #
    
    while True:
        try:
            chat = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                        messages = messages,
                                        temperature=0,
                                        )
            reply = chat.choices[0].message.content 
            return reply
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "Accessing the Completion service error"
            print('Error communicating with Completion service:', oops)
            sleep(1)


#
#def read_config(parser: ConfigParser, location: str) -> None:
#    assert parser.read(location), f"Could not read config {location}"
#
#
#model_path = "./model_files"
#CONFIG_FILE = os.path.join(model_path, "env.conf")
#read_config(ai_for_world_config, CONFIG_FILE)
#api_key = ai_for_world_config.get("openai", "api_key").strip()
#"""
#  
api_key = st.secrets["API_KEY"]
openai.api_key = api_key
#
st.set_page_config(page_title="Tasks with Any YouTube Videos", layout="centered")
st.image(image, caption='Tasks with Any YouTube Videos')
#
# Create a dropdown menu with options
# page header
st.title(f"Tasks with YouTube Videos")
with st.form("Tasks with YouTube Videos"):
   url = st.text_input("Enter the YouTube Video url")
   #
  
   #
   submit_quiz = st.form_submit_button("Quiz")
   submit_sum = st.form_submit_button("Summary")
   #
   task = st.text_input("Enter the instruction.",value="Enter the instruction only if you want to perform a task.")
   #
   submit_task = st.form_submit_button("Instruct")
   #
   if submit_quiz:    
        prompt ="""Create a 5 question multiple choice quiz based on the video transcript specified below and provide solutions.
TRANSCRIPT:
<<content>>
        """
        #
        loader = YoutubeLoader.from_youtube_channel(url)
        documents = loader.load()
        content = documents[0].page_content
        #
        token_len = tiktoken_len(content)
        if token_len > 3500:
            chunks = split_text(content)
            predictions = ''
            for chunk in chunks:
                prompt = prompt.replace('<<content>>',chunk)
                predictions += gpt3turbo(prompt)
        else:
            prompt = prompt.replace('<<content>>',content)
            predictions = gpt3turbo(prompt)

        # output header
        st.header("Quiz Generated")
        # output results
        st.success(predictions)
   if submit_sum:    
        prompt ="""Create a summary of the video transcript specified below.
TRANSCRIPT:
<<content>>
        """
        #
        loader = YoutubeLoader.from_youtube_channel(url)
        documents = loader.load()
        content = documents[0].page_content
        #
        token_len = tiktoken_len(content)
        if token_len > 3500:
            chunks = split_text(content)
            predictions = ''
            for chunk in chunks:
                prompt = prompt.replace('<<content>>',chunk)
                predictions += gpt3turbo(prompt)
        else:
            prompt = prompt.replace('<<content>>',content)
            predictions = gpt3turbo(prompt)

        # output header
        st.header("Summary Generated")
        # output results
        st.success(predictions)
   if submit_task:    
        prompt = """TASK: <<task>>
Please provide respose for the above task based on the video transcript specified below.
TRANSCRIPT:
<<content>>
        
        """
        #
        loader = YoutubeLoader.from_youtube_channel(url)
        documents = loader.load()
        content = documents[0].page_content
        
        #
        token_len = tiktoken_len(content)
        if token_len > 3500:
            chunks = split_text(content)
            predictions = ''
            for chunk in chunks:
                prompt = prompt.replace('<<content>>',chunk).replace('<<task>>',task)
                predictions += gpt3turbo(prompt)
        else:
            prompt = prompt.replace('<<content>>',content)
            predictions = gpt3turbo(prompt)

        # output header
        st.header("Task Response Generated")
        # output results
        st.success(predictions)