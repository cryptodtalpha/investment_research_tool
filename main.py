
### IMPORT LIBRARIES ###

from openai import OpenAI
import json
import streamlit as st


### IMPORT API KEYS ###


# read openai token
open_api_key = st.secrets['OPENAI_API_KEY']

if open_api_key:
    print("OpenAI API key loaded")
else:
    print("OpenAI API key not loaded")
    
# read perplexity API token
perp_api_key = st.secrets['PERP_API_KEY']

if perp_api_key:
    print("Perplexity API key loaded")
else:
    print("Perplexity API key not loaded")



### INITIALISE OPENAI CLIENT ###

client_openai = OpenAI()

### INITIALISE PERPLEXITY CLIENT ###

perp_client = OpenAI(api_key = perp_api_key, base_url = "https://api.perplexity.ai")    



### INITIALISE MESSAGE HISTORY ###

st.header("Investment Research Assistant", divider = 'blue')


if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi I am your investment research assistant! Give me a topic to research!"}
]
    

# prompt for user input and save to chat history
if prompt := st.chat_input("Your question"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
# display prior chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# if last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Preparing response..."):
            
            # openai stream
                        
            stream = client_openai.chat.completions.create(
                model = "gpt-4o",
                messages = [
                    {"role": "system", 
                     "content": ("You are an expert investment analyst. Provide me a concise list of no more than 10 key investment research questions for the following topic."
                                 "Ensure each question makes specific reference to the topic provided. Your answer should just contain the list of questions."),
                     },
                    {"role": "user",
                     "content": prompt},
                    ],
                stream = True,
                )

            response = st.write_stream(stream)
            
            # convert openai response into list of questions

            questions_list = [question.strip() for question in response.strip().split('\n')]
            questions_list = [question[3:].strip() for question in questions_list]
            
            # perplexity stream
    
            for question in questions_list:
                
                st.subheader(question, divider = 'green')
    
                perp_stream = perp_client.chat.completions.create(
                    model = "llama-3-sonar-large-32k-online",
                    messages = [
                            {
                                  "role": "system",
                                  "content": (
                                      "You are an expert investment analyst that will assist the user "
                                      "in providing accurate, concise research."
                                  ),
                            },
                            {
                                  "role": "user",
                                  "content": (
                                      question
                                  ),
                            },
                        ]
                        ,
                    )      
            
                perp_json_response = perp_stream.json()               
                perp_response_dict = json.loads(perp_json_response)                
                perp_response_text = perp_response_dict['choices'][0]['message']['content']            
                perp_response = st.write(perp_response_text)            
                      
            
        st.session_state.messages.append({"role": "assistant", "content": perp_response})
            







    

    
    
    

    