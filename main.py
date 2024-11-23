from openai import OpenAI
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests as req
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@app.route('/recipe_submission', methods=['POST'])
def recipe_submission():
    data = request.get_json()
    req.get(data['url'])
    dietary_restrictions, number_of_people = data['dietary_restrictions'], data['number_of_people']
    website_data = BeautifulSoup(data['url'], 'html.parser')
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",        
        messages=[
                    {   
                        "role": "system", 
                        "content": 
                        f"Here is a set of data for a website relating to cooking recipes, 
                        I would like you to find the recipe that is involved and update the recipe to match the preferences of the user. 
                        There are dietary restricts that must be followed in the updated recipe: {dietary_restrictions}.
                        Additionally, you will need to make the recipe ratios work for the given number of people: {number_of_people}.
                        Thank you!
                        {website_data}",
                    }, 
                    {
                        "role": "user",
                        "content": 
                        "Please produce a recipe according to the above guidelines. Please put it in the format of a recipe card.",
                    }
                ]
            )
    return jsonify(response)






