from openai import OpenAI
from flask import Flask, request, jsonify, render_template
import cloudscraper
from bs4 import BeautifulSoup
import requests as req
from dotenv import load_dotenv
import os
import re

load_dotenv()

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def index():
    return render_template("form.html")

@app.route("/recipe_submission", methods=["POST"])
def recipe_submission():
    form_data = request.get_json()

    recipe_url = form_data.get('url', '')
    number_of_people = form_data.get('number_of_people', '')
    dietary_restrictions = form_data.get('dietary_restrictions', [])
    
    website_data = cloudscraper.create_scraper().get(recipe_url).text
    soup = BeautifulSoup(website_data, "html.parser")
    ingredients, instructions = soup.find(
        "div", class_=re.compile(r".*ingredients.*")
    ), soup.find("div", class_=re.compile(r".*instructions.*"))

    cleaned_html = "".join([str(ingredients), str(instructions)])

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"Here is a set of data for a website relating to cooking recipes, I would like you to find the recipe that is involved and update the recipe to match the preferences of the user. There are dietary restricts that must be followed in the updated recipe: {dietary_restrictions}. Additionally, you will need to make the recipe ratios work for the given number of people: {number_of_people}. Thank you! {cleaned_html}",
            },
            {
                "role": "user",
                "content": "Please produce a recipe according to the above guidelines. Please put it in the format of a recipe card.",
            },
        ],
    )
    return jsonify(response.choices[0].message.content)
