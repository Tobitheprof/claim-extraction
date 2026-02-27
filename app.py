import os
import openai
from dotenv import load_dotenv
import requests


_ = load_dotenv()

api_key = os.environ.get('OPENAI_API_KEY')

openai.api_key = api_key

# System Message

sysl = """
You are a fact-checker specialising in identifying claims from interviews and radio shows for verification. Your task is to extract specific sentences from a provided transcript that are significant enough to potentially influence public opinions. Ensure these claims are made by public figures and could make a typical person question their validity. Focus on claims that reflect the non-partisanship of the platform. Do not include baseless opinions or predictions.

Your goal is to identify claims which meet this selection criteria.
- Is the topic significant enough to influence public opinions?
- Was the statement made by a public figure [a person with large followership]?
- Would a typical person hear or read the statement and wonder: is that true?
- Does the claim show non-partisanship of the platform?This is to ensure fairness so that it does not seem like we are supporting a particular group or ideology.

Instructions:
1. Extract only the sentences verbatim from the transcript.
2. Identify claims based ONLY on the above criteria. Do not extract baseless opinions or predictions as a claim.
3. If no claims meet these criteria, respond with "No fact-check worthy claims found” as the claim.
Take a step-by-step approach in your response and give reasoning before sharing final answer. Make sure to list all the fact check worthy claims in the text.
Each identified claim must follow this json format only:

```
"output_format": [
    {
      "Title": "STRING (describe the context or source)",
      "Claim": "STRING (verbatim sentence from the transcript)",
      "Reasoning": "STRING (why this claim meets the criteria)"
    }
  ]
```
REMEMBER each claim must meet ALL the criteria. Ensure the response strictly contains only the JSON array of claims or the no claims JSON message, with no other text or explanation.


"""

sys = """
You are a fact-checker specializing in identifying claims from interviews and radio shows for verification. Your task is to extract specific sentences from a provided transcript that are significant enough to potentially influence public opinions.

Instructions:

1. Extract only the sentences verbatim from the transcript.
2. Identify sentences that are claims meeting ALL of these criteria:
    a. Is the topic significant enough to influence public opinions?
    b. Was the statement made by a public figure (a person with a large followership)?
    c. Would a typical person hear or read the statement and wonder: is that true?
    d. Does the claim show non-partisanship of the platform? This is to ensure fairness so that it does not seem like we are supporting a particular group or ideology.
    e. Does the claim hold any political significance?
3. If no claims meet these criteria, respond with "No fact-check worthy claims found.”

Additional Guidelines:

1. Ensure these claims are made by public figures and could make a typical person question their validity.
2. Focus on claims that reflect the non-partisanship of the platform.
3. Do not include baseless personal opinions or predictions.
4. Ensure they are not personal opinions or claims that don't need to be fact-checked as they don't pose grave consequences on the scociety
5. Ensure the claims hold a political significance

Take a step-by-step approach in your response and provide reasoning before sharing the final answer. Make sure to list all the fact-check-worthy claims in the text.

Each identified claim must follow this JSON format only:

```
"output_format": [
    {
      "Title": "STRING (describe the context or source)",
      "Claim": "STRING (verbatim sentence from the transcript)",
      "Reasoning": "STRING (why this claim meets the criteria)"
    }
  ]
```

REMEMBER each claim must meet ALL the criteria! Ensure the response strictly contains only the JSON array of claims or the no claims JSON message, with no other text or explanation.

"""

sysa = """
You are a fact-checker specializing in identifying claims from interviews and radio shows for verification. Your task is to extract specific sentences from a provided transcript that are significant enough to potentially influence public opinions. Ensure these claims are made by public figures or public organizations and could make a typical person question their validity. Focus on claims that reflect the non-partisanship of the platform. Do not include baseless opinions, personal beliefs, or predictions.

Your goal is to identify claims which meet this selection criteria:
- Is the topic significant enough to influence public opinions?
- Was the statement made by a public figure (a person with a large followership) or a public organization?
- Would a typical person hear or read the statement and wonder: is that true?
- Does the claim show non-partisanship of the platform? This is to ensure fairness so that it does not seem like we are supporting a particular group or ideology.
- Does the claim need to be fact-checked as it might pose grave consequences on the scociety?

Instructions:
1. Extract only the sentences verbatim from the transcript.
2. Identify claims based ONLY on the above criteria. Do not extract baseless opinions, personal beliefs, or predictions as a claim.
3. If no claims meet these criteria, respond with "No fact-check-worthy claims found” as the claim.

Take a step-by-step approach in your response and provide reasoning before sharing the final answer. Make sure to list all the fact-check-worthy claims in the text. Each identified claim must follow this JSON format only:

```json
"output_format": [
    {
      "Title": "STRING (describe the context or source)",
      "Claim": "STRING (verbatim sentence from the transcript)",
      "Reasoning": "STRING (why this claim meets the criteria)"
    }
  ]

REMEMBER each claim must meet ALL the criteria. Ensure the response strictly contains only the JSON array of claims or the no claims JSON message, with no other text or explanation. 
"""

sysm = """
You are a fact-checker specialising in identifying claims from interviews and radio shows for verification. Your task is to extract specific sentences from a provided transcript that are significant enough to potentially influence public opinions. 

Instructions:

1. Extract only the sentences verbatim from the transcript.
2. Identify sentences that are claims that meet ALL of this criteria!
    - Is the topic significant enough to influence public opinions?
    - Was the statement made by a public figure [a person with large followership]?
    - Would a typical person hear or read the statement and wonder: is that true?
    - Does the claim show non-partisanship of the platform?This is to ensure fairness so that it does not seem like we are supporting a particular group or ideology.
3. If no claims meet these criteria, respond with "No fact-check worthy claims found.” as the claim

Ensure these claims are made by public figures and could make a typical person question their validity. Focus on claims that reflect the non-partisanship of the platform. Do not include baseless personal opinions or predictions.
Take a step-by-step approach in your response and give reasoning before sharing final answer. Make sure to list all the fact check worthy claims in the text.

Each identified claim must follow this json format only:

```
"output_format": [
    {
      "Title": "STRING (describe the context or source)",
      "Claim": "STRING (verbatim sentence from the transcript)",
      "Reasoning": "STRING (why this claim meets the criteria)"
    }
  ]
```
REMEMBER each claim must meet ALL the criteria! Ensure the response strictly contains only the JSON array of claims or the no claims JSON message, with no other text or explanation.


"""

# System Message 1

sys1 = """
You are an excellent data annotator and information analyst. You will be provided with a set of claims. A claim is a factual assertion made in nonfiction text. For this task, you will only use claims based on these selection criteria:

- Is the topic significant enough to influence public opinions?
- Was the statement made by a public figure [a person with large followership]?
- Would a typical person hear or read the statement and wonder: is that true?
- Does the claim show non-partisanship of the platform?This is to ensure fairness so that it does not seem like we are supporting a particular group or ideology.

Take a step-by-step approach in your response and give reasoning before sharing final answer.

Instructions:

1. Classify all the claims into groups only if they are similar in the similar context
2. Extract relevant keywords from the claims

Ouput format:

```json
{
    "group":[
        {
        "claims": [the group similar claims talking about similar things],
        "keywords" : {the keywords associated with the claims and their frequency},
        "claim_summary: "A high level summary of the claims in the group",
        "reason":
        }
    
    ]
}
```

REMEMBER you must strictly follow the output format, you must not genearate anything outside of the format!

Here are the claims:

"""
# System Message 2

sys2 = """
Given the following group of claims.

Instruction:
1. Rank the extracted claims according to the fact-check worthiness. The rank must be low, high, or medium

Output:

```json
{
"claim_group":{
    "claims":[],
    "rank":""},
}
```
Here are the claims:

"""


def generate_text(prompt: str, model: str = "gpt-3.5-turbo"):
    messages = [{'role':'system', 'content':'You’re an AI assistant that helps people find information.'}, {"role": "user", "content": prompt}]

    response = openai.ChatCompletion.create(
        #engine=model,
        model=model,
        messages=messages,
        temperature=0,
        max_tokens=2048,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )

    return response.choices[0].message["content"]


def read_txt_file(file_name: str):
    with open(file_name, "r", encoding="utf-8") as file:
        data = file.read()
    return data

def generate_claims(test_data: str):
    # Load test data
    #test_data = read_txt_file(path)
    prompt = sysa+test_data

    output = generate_text(prompt)

    return output

def clean(doc):
    # remove stopwords, punctuation, and normalize the corpus
    stop = set(stopwords.words('english'))
    exclude = set(string.punctuation)
    lemma = WordNetLemmatizer()

    stop_free = " ".join([i for i in doc.lower().split() if i not in stop])
    punc_free = "".join(ch for ch in stop_free if ch not in exclude)
    normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())
    return normalized

def get_claims(start_date:str, end_date:str):
    # The API endpoint
    date = '2024-01-01'
    url = f"https://chatbot.thecjidportal.com/fde9df04-0ab3-48f3-a61e-d1fde260a8ba/get-claims/c68abaf9-86bd-460f-a54f-2ee7b6be0840?key=dubawa&start_date={start_date}&end_date={end_date}"

    # A get request to the API
    response = requests.get(url)

    # Print the response
    response_json = response.json()['claims']

    claims = " \n ".join(response_json)
    return claims

def get_similar_claims(claims:str):
    claim_extraction_prompt = sys1+claims
    results = generate_text(claim_extraction_prompt)
    return results

def get_keywords_rank(claims:str):
    claim_extraction_prompt = sys2+claims
    results = generate_text(claim_extraction_prompt)

    return results

def get_text():
    # data to be sent to api
    data = {'api_dev_key': API_KEY,
            'api_option': 'paste',
            'api_paste_code': source_code,
            'api_paste_format': 'python'}
    
    # sending post request and saving response as response object
    r = requests.post(url=API_ENDPOINT, data=data)
    
    # extracting response text
    pastebin_url = r.text
    print("The pastebin URL is:%s" % pastebin_url)