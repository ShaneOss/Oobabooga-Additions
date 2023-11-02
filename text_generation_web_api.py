import copy
import html
import json
import requests

class LocalGPT:
    def __init__(self):
        self.HOST = 'localhost:5000'
        self.URI = f'http://{self.HOST}/api/v1/chat'
        self.searching = False
        self.query_str = ""
        self.answer = ""

    def run(self, user_input, history):
        self.request = {
            'user_input': user_input,
            'max_new_tokens': 512,
            'auto_max_new_tokens': False,
            'max_tokens_second': 0,
            'history': history,
            'mode': 'chat',
            'regenerate': False,
            '_continue': True,
            'preset': 'None',
            'do_sample': True,
            'temperature': 0.2,
            'top_p': 0.95,
            'typical_p': 1,
            'epsilon_cutoff': 0,
            'eta_cutoff': 0,
            'tfs': 1,
            'top_a': 0,
            'repetition_penalty': 1.1,
            'repetition_penalty_range': 0,
            'top_k': 40,
            'min_length': 0,
            'no_repeat_ngram_size': 0,
            'num_beams': 1,
            'penalty_alpha': 0,
            'length_penalty': 1,
            'early_stopping': False,
            'mirostat_mode': 0,
            'mirostat_tau': 5,
            'mirostat_eta': 0.1,
            'grammar_string': '',
            'guidance_scale': 1,
            'negative_prompt': '',
            'seed': -1,
            'add_bos_token': True,
            'truncation_length': 4096,
            'ban_eos_token': False,
            'custom_token_bans': '',
            'skip_special_tokens': True,
            'stopping_strings': []
        }

    def search_large_text(self, context, large_text):
        max_chunk_length = 1500
        text_chunks = [large_text[i:i + max_chunk_length] for i in range(0, len(large_text), max_chunk_length)]
        
        conversation_history = {'internal': [], 'visible': []}  # Initialize the conversation history
        user_context = ['user_input', context]
        conversation_history['internal'].append(user_context)
        conversation_history['visible'].append(user_context)
    
        generated_output = []  # Initialize a list to store generated responses
    
        for chunk in text_chunks:
            chunk_history = copy.deepcopy(conversation_history)
    
            # Push a new user message to both "internal" and "visible" histories
            user_message = [chunk, '']
            chunk_history['internal'].append(user_message)
            chunk_history['visible'].append(user_message)
    
            self.run(chunk, chunk_history)
    
            response = requests.post(self.URI, json=self.request)
    
            if response.status_code == 200:
                result = response.json()['results'][0]['history']
                print("RESULT: \n", result)
            
                if result and 'visible' in result and result['visible']:
                    last_visible = result['visible'][-1]
                    if len(last_visible) > 1:
                        generated_output.append(last_visible[1])

            combined_output = '\n'.join(generated_output)

        return html.unescape(combined_output)

    def search(self, query: str):
        self.searching = True
        formatted_query = query.replace('\n', '\\n').replace('\t', '\\t')
        self.query_str = formatted_query
        history = [{'role': 'user', 'content': self.query_str}]

        self.run(self.query_str, history)

        response = requests.post(self.URI, json=self.request)

        if response.status_code == 200:
            result = response.json()['results'][0]['history']
            # Extract and append the generated response from the API

            if result and 'visible' in result and result['visible']:
                last_visible = result['visible'][-1]
                if len(last_visible) > 1:
                    self.answer = html.unescape(last_visible[1])
                else:
                    self.answer = ""
            else:
                self.answer = ""

        if self.answer != "":
            formatted_output = self.answer.replace('\\n', '\n').replace('\\t', '\t')
            return formatted_output
        else:
            self.searching = False
            return ""

"""
Example:

from text_generation_web_api import LocalGPT
localgpt = LocalGPT()

# Normal text
result = localgpt.search("What is the meaning of life?")
print(result)

# For large text
result = localgpt.search_large_text('Your a helpful assistant who summarizes in detail YouTube video transcripts. Summarize each chunk and then provide a summary of the whole transcript. End your response with <|end_of_turn|>', cleaned_transcript)
print(result)
"""
