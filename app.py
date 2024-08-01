from flask import Flask, render_template,request,jsonify
from flask import jsonify
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import re


app = Flask(__name__)

STUDENTS = [

    {"id": 1,
     "name": "Olaronke Afolabi",
     "team" : "Front-End"
     },
     {"id": 2,
      "name": "Jasmine Emeruwa",
      "team" : "Front-End"
      },
      { "id": 3, 
       "name": "Natanel Solomonov",
       "team" : "Front- End & Back- End"
      },
      { "id": 4,
       "name": "Rahul Nair",
       "team": "Back-End"
      },
      {"id": 5,
       "name" : "Morolasaiye Aina",
       "team" : "Front-End"
      }
]
def extract_nutrient_value(text):
    match = re.search(r'(\d+(\.\d+)?)', text)
    return match.group(1) if match else None



    
def parse_food_item_fat(url,serving_size=1):
    food_item_html=requests.get(url).text
    soup=BeautifulSoup(food_item_html, 'lxml')
    food_fact=soup.find_all('span',class_='nutfactstopnutrient')
    for fact in food_fact:
        if 'Total Fat' in fact.text:
            total_fat=fact.find('b').next_sibling.strip()
            total_fat = float(total_fat.rstrip('g')) * serving_size
            print("Total Fat:",total_fat)
            return total_fat
        return None
    

def parse_food_item_carb(url, serving_size=1):
    food_item_html = requests.get(url).text
    soup = BeautifulSoup(food_item_html, 'lxml')
    food_fact_carb = soup.find_all('span', class_='nutfactstopnutrient')
    for fact in food_fact_carb:
        if 'Total Carbohydrate' in fact.text:
              total_carb=fact.find('b').next_sibling.strip()
              total_carb=float(total_carb.rstrip('g'))*serving_size
              print("Total Carbohydrates:", total_carb)
              return total_carb
    return None    
 
            

   
def parse_food_item_cholest(url,serving_size=1):
    food_item_html=requests.get(url).text
    soup=BeautifulSoup(food_item_html, 'lxml')
    food_fact_cholest=soup.find_all('span',class_='nutfactstopnutrient')
    for fact in food_fact_cholest:
        if 'Cholesterol' in fact.text:
            total_cholest= fact.find('b').next_sibling.strip()
            total_cholest=float(total_cholest.rstrip('mg'))*serving_size
            print("Total Cholesterol:", total_cholest)
            return total_cholest
    return None    
       
            

def parse_food_item_sodium(url,serving_size=1):
    food_item_html = requests.get(url).text
    soup = BeautifulSoup(food_item_html, 'lxml')
    food_fact_sodium = soup.find_all('span', class_='nutfactstopnutrient')
    
    sodium_found = False
    for fact in food_fact_sodium:
        if 'Sodium' in fact.text and not sodium_found:
            total_sodium = extract_nutrient_value(fact.text)
            if total_sodium:
                total_sodium=float(total_sodium.rstrip('mg'))*serving_size
                print("Total Sodium:", total_sodium, "mg")
                sodium_found = True
                return total_sodium
                
    if not sodium_found:
        print("No Sodium Found")
        return None


def parse_food_item_protein(url,serving_size=1):
    food_item_html = requests.get(url).text
    soup = BeautifulSoup(food_item_html, 'lxml')
    food_fact_protein = soup.find_all('span', class_='nutfactstopnutrient')
    protein_found= False
    for fact in food_fact_protein:
        if "Protein" in fact.text and not protein_found:
            total_protein = extract_nutrient_value(fact.text)
            if total_protein:
                total_protein=float(total_protein.rstrip('mg'))*serving_size
                print(" Total Protein:", total_protein, "g")
                protein_found= True
                return total_protein
    if not protein_found:
        print("No Protein Found")
        return None
    
def parse_food_item_calories(url,serving_size=1):
    food_item_html = requests.get(url).text
    soup = BeautifulSoup(food_item_html, 'lxml')
    food_fact = soup.find_all('p')

    for fact in food_fact:
        if 'Calories per serving' in fact.text:
            calories_per_serving = fact.find_next('p').text.strip()
            calories_per_serving=int(calories_per_serving)*serving_size
            print("Calories per serving:", calories_per_serving)
            return calories_per_serving


@app.route('/food_search', methods=['POST'])
def food_search():
    if request.method == 'POST':
        food_name_input = request.form['food_name_input']
        dining_hall = request.form['dining_hall']
        date_input = request.form['date_input']
        serving_size = int(request.form['serving_size'])

        # Convert the date to the required format for the URL
        formatted_date = datetime.strptime(date_input, "%Y-%m-%d").strftime("%m/%d/%Y")

        html_text = requests.get(f'https://nutrition.umd.edu/?locationNum={dining_hall}&dtdate={formatted_date}')
        soup = BeautifulSoup(html_text.content, 'lxml')
        food_cards = soup.find_all('div', class_='card')
        food_found = False
        food_info = None

        for food_card in food_cards:
            food_name = [item.text for item in food_card.find_all('a', 'menu-item-name')]
            food_links = [item['href'].split("=")[-1] for item in food_card.find_all('a', 'menu-item-name')]

            for i in range(len(food_name)):
                if food_name[i] == food_name_input and not food_found:
                    food_item_url = f'https://nutrition.umd.edu/label.aspx?RecNumAndPort={food_links[i]}'
                    # Call nutrient parsing functions and store the results in food_info dictionary
                    food_info = {
                        'Total Fat': parse_food_item_fat(food_item_url,serving_size),
                        'Total Carbohydrates': parse_food_item_carb(food_item_url,serving_size),
                        'Total Cholesterol': parse_food_item_cholest(food_item_url,serving_size),
                        'Total Sodium': parse_food_item_sodium(food_item_url,serving_size),
                        'Total Protein': parse_food_item_protein(food_item_url,serving_size),
                        'Total Calories': parse_food_item_calories(food_item_url,serving_size)
                    }
                    food_found = True
                    break
        return jsonify(food_info)
    return render_template('index.html', students=STUDENTS)
@app.route('/')
def careerLaunch():
    return render_template('index.html', students = STUDENTS  )
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)