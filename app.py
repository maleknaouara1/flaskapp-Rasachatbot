from flask import Flask, render_template, url_for, request

import json
from flask import session
from flask import redirect
import requests
app = Flask(__name__, template_folder='templates', static_folder='static')



@app.route('/get_chatbot')
def get_chatbot():
    return render_template('TTBOT.html')

import matplotlib.pyplot as plt


db_config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'database': 'database',
    'port': '3306'
}

def calculate_average_efficiency_per_department():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    query = """
    SELECT Departement, AVG(efficiency_per_day) as avg_efficiency
    FROM productivity
    WHERE efficiency_per_day IS NOT NULL
    GROUP BY Departement
    """
    cursor.execute(query)
    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return results


@app.route('/top_efficiencies')
def efficiency():
    conn =  mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    query = '''
        SELECT *
        FROM productivity
        ORDER BY efficiency_per_day DESC
        LIMIT 10;
    '''
    cursor.execute(query)
    top_efficiencies = cursor.fetchall()
    conn.close()

    return render_template('efficiency.html', top_efficiencies=top_efficiencies)


@app.route('/')
def home():
    # Your code to calculate average efficiencies and generate the chart
    results = calculate_average_efficiency_per_department()
    departments = [result['Departement'] for result in results]
    avg_efficiencies = [result['avg_efficiency'] for result in results]
    

    
    

    rgb_color = (63/255, 133/255, 63/255)
    plt.figure(figsize=(7, 4))

    bars = plt.bar(departments, avg_efficiencies, width=0.8, color=['darkgrey', rgb_color, 'lightgray'])
    plt.xlabel('Departments')
    plt.ylabel('Average Efficiency')

    # Annotate the bars with percentage values
    for bar, efficiency in zip(bars, avg_efficiencies):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height, f'{efficiency:.1f}%', ha='center', va='bottom', fontsize=10, color='black')

    plt.xticks(rotation=0)
    plt.tight_layout()
    
    # Save the chart as an image
    chart_path = 'static/efficiency_chart23.png'
    plt.savefig(chart_path)
    plt.close()  # Close the current plot to avoid conflicts

    chatbot_app_image = url_for('static', filename='chatbot_app.png')
    # Get the URL for the logo image
    logo_image = url_for('static', filename='Kashcke (1).jpg')
    return render_template('home.html', chatbot_app_image=chatbot_app_image, logo_image=logo_image,chart_path=chart_path)

@app.route("/TTBOT")
def ttbot():
    # Get the URL for the chatbot icon image
    chatbot_icone = url_for('static', filename='chaticon.png')

    return render_template("TTBOT.html", chatbot_icone=chatbot_icone)


import mysql.connector
def get_database():
    return render_template('database.html')

# MySQL database configuration
db_config = {
    'user':'root',
    'password':'root',
    'host':'localhost',
    'database':'database',
    'port':'3306'
}
def get_error_items():
    error_items = []

    # Replace with your MySQL database connection details
    db_config = {
        'user':'root',
        'password':'root',
        'host':'localhost',
        'database':'database',
        'port':'3306'
    }

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM productivity"
    cursor.execute(query)
    items = cursor.fetchall()

    
    for item in items:
        # Check if any column value is None (NULL)
        if any(value is None for value in item.values()) or item['pointing'] > 24 or item['Produced_Hours'] > 24 or item['Produced_Hours'] > item['pointing'] :
            error_items.append(item)

    cursor.close()
    connection.close()

    return error_items

@app.route('/errors')
def errors():
    error_items = get_error_items()
    return render_template('errors.html', error_items=error_items)


# Create a MySQL connection
db_connection = mysql.connector.connect(**db_config)
@app.route('/database')
def database():
    cursor = db_connection.cursor(dictionary=True)

    # Execute an SQL query
    query = "SELECT * FROM productivity"
    cursor.execute(query)

    # Fetch all rows from the query result
    data = cursor.fetchall()

    cursor.close()
    logo_image = url_for('static', filename='Kashcke (1).jpg')
    return render_template('database.html', data=data,logo_image=logo_image)



# Cette fonction crée une route pour l'API Flask à l'URL "/get"
@app.route("/get")
# Cette fonction récupère la réponse du bot
def get_bot_response():
    
    userText = str(request.args.get('msg'))
    
    if not userText:
        data = json.dumps({"sender": "Rasa", "message": "/greet"})
    else:
        data = json.dumps({"sender": "Rasa", "message": userText})

    # Ajoute des en-têtes de requête
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    # Envoie une requête POST à l'URL spécifiée pour obtenir la réponse du bot
    response = requests.post('http://localhost:5005/webhooks/rest/webhook', data=data, headers=headers)
    # Convertit la réponse JSON en dictionnaire Python
    response = response.json()
    # Initialise une liste pour stocker les messages du bot
    messages = []
    # Initialise une chaîne vide pour stocker le code HTML des boutons
    button_html = ""
    # Boucle à travers chaque réponse du bot
    for r in response:
        # Récupère le texte de la réponse
        text = r['text']
        # Récupère les entités (s'il y en a) de la réponse
        entities = r.get('entities', {})
        # Si des entités sont présentes, les remplace par leur valeur dans le texte de la réponse
        if entities:
            for entity, value in entities.items():
                text = text.replace(f"[{entity}]", value)
        # Récupère les boutons (s'il y en a) de la réponse
        buttons = r.get('buttons', [])
        # Boucle à travers chaque bouton
        for button in buttons:
            # Récupère le titre du bouton
            buttonTitle = button['title']
            # Récupère le payload du bouton et le remplace par des valeurs spécifiques
            buttonPayload = button['payload'].replace('{{"forfait":"50Mo"}}', '{"forfait":"50Mo"}')
            buttonPayload = buttonPayload.replace('{{"forfait_ehdia":"200Mo"}}', '{"forfait_ehdia":"200Mo"}')
            buttonPayload = buttonPayload.replace('{{"type_request":"statut"}}', '{"type_request":"statut"}')
            # Ajoute le bouton au code HTML
            button_html += f'<button class="btn btn-primary" data-payload=\'{buttonPayload}\'>{buttonTitle}</button>'
        # Si des boutons sont présents, les ajoute au code HTML
        if button_html:
            button_html = f'<div id="button-container">{button_html}</div>'
        # Ajoute le texte de la réponse à la liste de messages
        messages.append(text)
    # Joint tous les messages en une chaîne avec des séparateurs spécifiques et ajoute le code HTML des boutons à la fin
    bot_responses = '|||'.join(messages) + '|||' + button_html
    # Retourne la réponse finale
    return bot_responses

import mysql.connector

db_config = {
    'user':'root',
    'password':'root',
    'host':'localhost',
    'database':'database',
    'port':'3306'
}

def calculate_efficiency():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    query = "SELECT id, produced_hours, pointing FROM productivity"
    cursor.execute(query)
    rows = cursor.fetchall()

    for row in rows:
        if row['pointing'] is not None and row['pointing'] != 0 and row['pointing'] < 100:
          if row['produced_hours'] is not None  and row['produced_hours'] <= row['pointing'] and  row['produced_hours']<100:

                efficiency = (row['produced_hours'] / row['pointing']) * 100
                update_query = "UPDATE productivity SET efficiency_per_day = %(efficiency)s WHERE id = %(id)s"
                cursor.execute(update_query, {'efficiency': efficiency, 'id': row['id']})
                connection.commit()

    cursor.close()
    connection.close()


calculate_efficiency()

if __name__ == "__main__":
	app.run(debug = True)