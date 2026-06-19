import torch
import re
import nltk
import os
import platform
from transformers import T5Tokenizer, T5ForConditionalGeneration
from transformers import BartTokenizer, BartForConditionalGeneration
import requests
from bs4 import BeautifulSoup, Comment
import warnings
import streamlit as st
import time


def time_function(func, *args, **kwargs):
    """Function to time the run time"""
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    elapsed_time = end_time - start_time
    st.write(f"The process {func.__name__} took {elapsed_time:.2f} seconds to run.")
    return result


def find_config_file(model_dir, model_name):
    """Function to find the config file inside the existing model cache folders"""
    print("From the config file function",os.path.join(model_dir, model_name))
    for dirpath, dirnames, filenames in os.walk(os.path.join(model_dir,"models--" + model_name)):
        if 'config.json' in filenames:
            print("Config file found")
            return os.path.join(dirpath, 'config.json')
    return None

def generate_summary():
    """Function to generate text summary using T5 are BART"""
    try:
        st.set_page_config(layout="wide")
        
        # Create a placeholder before running the T5 inference
        placeholder = st.empty()
        # Update the placeholder with a "Please wait" message
        placeholder.text("Please wait. Page loading..")

        st.markdown("""
            <style>
                .stMarkdown p {
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }
            </style>
                """, unsafe_allow_html=True)
        
        placeholder.text("Please wait. Page loading...")

        text = "Confidential ACI Demo for Text Summarization"
        words = text.split()
        t = st.empty()
        for i in range(len(words) + 1):
            t.markdown("### %s" % ' '.join(words[:i]))
            time.sleep(0.05)
        st.write("")
        placeholder.text("Please wait. Page loading....")
        text = "This demo summarizes the text from a public page but the intent is \
                 to showcase a 2 party multi party scenario implemented using \
                 Azure Confidential Computing based ACI"
        words = text.split()
        t = st.empty()
        for i in range(len(words) + 1):
            t.markdown("%s" % ' '.join(words[:i]))
            time.sleep(0.05)

        placeholder.text("Please wait. Page loading.....")
        if platform.system() == 'Windows':
            with open('./ConfidentialFullText.txt', 'r') as f:
                page_text = f.read()
        else:
            with open('/mnt/remote/share/ConfidentialFullText.txt', 'r') as f:
                page_text = f.read()
        
        ## Code to ensure that the model is not downloaded every time the function is called
        model_name = 't5-small'
        if platform.system() == 'Windows':
            model_dir = os.path.join("C:\\", "Users", os.getlogin(), ".cache", "huggingface", "hub")
        else:
            print("Home",os.environ['HOME'])
            model_dir = os.path.join(os.environ['HOME'], ".cache", "huggingface", "hub")
        
        #model_dir = os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "transformers")
        
        print("Model Dir",model_dir)

        placeholder.text("Please wait. Page loading......")
        
        config_file = find_config_file(model_dir, model_name)
        
        print("Config file",config_file)
        
        if not os.path.exists(os.path.join(model_dir, "models--" + model_name)):
            print(f"Downloading {model_name} model...")
            model = T5ForConditionalGeneration.from_pretrained(model_name)
        else:
            print(f"{model_name} model already exists. Loading from cache...")
            model = T5ForConditionalGeneration.from_pretrained(os.path.dirname(config_file))

        if not os.path.exists(os.path.join(model_dir, "models--" + model_name)) or config_file == None:
            print(f"Downloading {model_name} tokenizer...")
            tokenizer = T5Tokenizer.from_pretrained(model_name)
        else:
            print(f"{model_name} tokenizer already exists. Loading from cache...")
            tokenizer = T5Tokenizer.from_pretrained(os.path.dirname(config_file))
        ## End optimization code
        placeholder.text("Please wait. Page loading......")
        device = torch.device('cpu')

        text = page_text

        ## Max length since this is T5
        max_length = 500
        
        preprocess_text = text.strip().replace("\n","")
        
        tokens = tokenizer.tokenize(preprocess_text)
        
            
        token_chunks = []
        current_chunk = []
        for token in tokens:
            current_chunk.append(token)
            if len(current_chunk) >= max_length and token == '.':
                # Check the number of tokens in the current chunk
                num_tokens = len(tokenizer.convert_tokens_to_ids(current_chunk))
                if num_tokens > max_length:
                    # Split the current chunk into smaller chunks
                    sub_chunks = [current_chunk[i:i+max_length] for i in range(0, len(current_chunk), max_length)]
                    token_chunks.extend(sub_chunks)
                else:
                    token_chunks.append(current_chunk)
                current_chunk = []
        if current_chunk:
            # Check the number of tokens in the last chunk
            num_tokens = len(tokenizer.convert_tokens_to_ids(current_chunk))
            if num_tokens > max_length:
                # Split the last chunk into smaller chunks
                sub_chunks = [current_chunk[i:i+max_length] for i in range(0, len(current_chunk), max_length)]
                token_chunks.extend(sub_chunks)
            else:
                token_chunks.append(current_chunk)
            
        t5_summaries = []
        
        for chunk in token_chunks:
            chunk_text = tokenizer.convert_tokens_to_string(chunk)
            tokenized_text = tokenizer.encode("summarize: " + chunk_text, return_tensors="pt").to(device)
            summary_ids = model.generate(tokenized_text,
                                            num_beams=8,
                                            no_repeat_ngram_size=2,
                                            min_length=30,
                                            max_length=60,
                                            early_stopping=True)
            summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            t5_summaries.append(summary)
        
        t5_summary = ' '.join(t5_summaries)
        
        st.write("#### Summary Generated by T5\n")

        text = t5_summary
        words = text.split()
        t = st.empty()
        for i in range(len(words) + 1):
            t.markdown("###### %s" % ' '.join(words[:i]))
            time.sleep(0.05)

        reference_summary = """Confidential containers run in a hardware backed Trusted Execution Environment (TEE)  
                    that provide intrinsic capabilities like data integrity, data confidentiality and code integrity.  
                    both deployment models help achieve high-isolation and memory encryption through hardware-based assurances. 
                    confidential computing can help you with your zero trust deployment security posture in Azure 
                    cloud by protecting your memory space through encryption."""

        reference = reference_summary.split()
        hypothesis = t5_summary.split()

        print()

        # Calculate BLEU-4 score
        weights = (0.25, 0.25, 0.25, 0.25)
        BLEUscore = nltk.translate.bleu_score.sentence_bleu([reference], hypothesis, weights=weights)
        st.write(f"T5 Summary BLEU-4 score: {BLEUscore}")
        placeholder.text("Loaded models & T5 Inference completed.")
        print()

        ## Code to ensure that the model is not downloaded every time the function is called
        model_name = 'facebook/bart-large'
        if platform.system() == 'Windows':
            model_dir = os.path.join("C:\\", "Users", os.getlogin(), ".cache", "huggingface", "hub")
        else:
            print("Home",os.environ['HOME'])
            model_dir = os.path.join(os.environ['HOME'], ".cache", "huggingface", "hub")
        #model_dir = os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "transformers")

        print("Model Dir", model_dir)

        config_file = find_config_file(model_dir, model_name.replace('/',"--"))
        print("Config file",config_file)
        if not os.path.exists(os.path.join(model_dir, "models--" + model_name.replace('/',"--"))):
            print(f"Downloading {model_name} model...")
            model = BartForConditionalGeneration.from_pretrained(model_name)
        else:
            print(f"{model_name} model already exists. Loading from cache & inferencing...")
            model = BartForConditionalGeneration.from_pretrained(os.path.dirname(config_file))

        if not os.path.exists(os.path.join(model_dir, "models--" + model_name.replace('/',"--"))) or config_file == None:
            print(f"Downloading {model_name} tokenizer...")
            tokenizer = BartTokenizer.from_pretrained(model_name)
        else:
            print(f"{model_name} tokenizer already exists. Loading from cache & tokenizing...")
            tokenizer = BartTokenizer.from_pretrained(os.path.dirname(config_file))
        # End code

        # Tokenize the text
        input_ids = tokenizer.encode(text, return_tensors='pt')

        # Generate the summary
        summary_ids = model.generate(input_ids ,max_length=230, min_length=50)
        BART_summary_text = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

        st.write("#### Summary Generated by BART\n")
        
        text = BART_summary_text
        words = text.split()
        t = st.empty()
        for i in range(len(words) + 1):
            t.markdown("###### %s" % ' '.join(words[:i]))
            time.sleep(0.05)

        reference = reference_summary.split()
        hypothesis = BART_summary_text.split()
        print()
        # Calculate BLEU-4 score
        weights = (0.25, 0.25, 0.25, 0.25)
        BLEUscore = nltk.translate.bleu_score.sentence_bleu([reference], hypothesis, weights=weights)
        st.write(f"BART summary BLEU-4 score: {BLEUscore}")
        placeholder.text("All Inferences completed.")
    except Exception as e:
    # Code to handle the exception
        placeholder.text((str(e)))

    
if __name__ == "__main__":
    # Suppress all warnings
    warnings.filterwarnings("ignore")
    #url = "https://learn.microsoft.com/en-us/azure/confidential-computing/confidential-containers#vm-isolated-confidential-containers-on-azure-container-instances-aci---public-preview"
    time_function(generate_summary)



