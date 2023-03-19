from django.forms.models import model_to_dict

from datetime import datetime

from random import choice
import requests

from json import loads

import environ
env = environ.Env()
environ.Env.read_env()

categories = ["age", "amazing", "anger", "architecture", "art", "attitude", "beauty", "best", "birthday", "change", "communications", "computers", "cool", "courage","design", "dreams", "education", "environmental", "equality", "experience", "failure", "faith", "family", "fear", "fitness", "food", "forgiveness", "freedom", "friendship", "funny", "future", "good", "government", "graduation", "great", "happiness", "health", "history", "home", "hope", "humor", "imagination", "inspirational", "intelligence", "jealousy", "knowledge", "leadership", "learning", "life", "love", "medical", "mom", "morning", "movies", "success"];

def getFormattedData(modelObjects, headers):
    """getFormattedData function

    Args:
        modelObjects (Model Object): Immutable list of model objects
        headers (list[str]): string list of headers
    """
    data = []
    for modelObject in modelObjects:
        row = model_to_dict(modelObject)
        data.append([
            (header, row[header]) for header in headers
        ])
        
    return data

def getDateObjectFromTime(datetime):
    date, time = datetime.split()
    re = [int(x) for x in date.split('-')]
    re.extend([int(x) for x in time.split(':')])
    
    
    return datetime(*re)

def getRandomQuote():
    """Random Quote Generator

    Returns:
        dict: dictionary containing quote
    """
    api_url = 'https://api.api-ninjas.com/v1/quotes?category={}'.format(choice(categories))
    response = requests.get(
                    api_url, 
                    headers = {
                        'X-Api-Key': env('QUOTE_API_KEY')
                    }
                )
    
    response = loads(response.text[1:-1])
    
    return response