# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
from typing import Any, Text, Dict, List,Optional
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List, Union
from rasa_sdk.events import SlotSet
import json
import re
import asyncio
from datetime import datetime


import calendar
import mysql.connector
import random
import string
from rasa_sdk.events import SessionStarted, ActionExecuted
from time import sleep
from typing import Dict, Text, Any, List, Union


class GetEfficiencyChoice(Action):
    def name(self) -> Text:
        return "get_efficiency_choice"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Retrieve the user's message
        user_message = tracker.latest_message.get("text")

        # Check for keywords in the user's message to determine the time frame
        time_frame = None
        if "month" in user_message:
            time_frame = "month"
        elif "week" in user_message:
            time_frame = "week"
        elif "day" in user_message:
            time_frame = "day"

        # Set the time_frame slot with the determined value
        return [SlotSet("time_frame", time_frame)]

#########ActionGetErrors########
class ActionGetErrors(Action):
    def name(self) -> Text:
        return "get_errors"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Connect to the database
        cnx = mysql.connector.connect(user='root', password='root', host='localhost', database='database', port='3306')
        cursor = cnx.cursor()

        # Execute query to retrieve data from the table
        query = "select VERKETTEN,Departement,Person,`Name`,Material,`Order`,Activity,Operation_short_text,Quantity,`date`,downtime,Performance_H,Produced_Hours,pointing from productivity "
        cursor.execute(query)

        # Fetch all the results
        results = cursor.fetchall()

        # Check for errors in the data
        errors = []

        for i, row in enumerate(results, start=1):
            # Check if any value in the row is null
            if any(value is None for value in row):
                errors.append("Null value found in column {} of row {}".format(row.index(None) + 1, i))

            pointing_value = row[13]  # Index of the "pointing" column in the row
            produced_hours_value = row[12]  # Index of the "Produced_Hours" column in the row

            # Check if the value in the "pointing" column is not a float or is out of range
            if not isinstance(pointing_value, (float, int)) or pointing_value > 10.0:
                errors.append("Invalid value in 'pointing' column of row {}".format(i))

            # Check if the value in the "Produced_Hours" column is not a float or is out of range
            if not isinstance(produced_hours_value, (float, int))  or produced_hours_value > 10.0:
                errors.append("Invalid value in 'Produced_Hours' column of row {}".format(i))

        # Store the errors in a slot for tracking
        tracker.slots['errors'] = errors
        
        formatted_errors = ["/-" + error for error in errors]

        # Print the errors in the console
        
        
          

        # Display the errors
        if len(errors) == 0:
            dispatcher.utter_message(text="No errors found in the database.")
            return []
        else:
            error_message = "\n".join(formatted_errors)
            dispatcher.utter_message(text="Errors found in the database:\n{}".format(error_message))
        return [SlotSet("errors", formatted_errors)]




##########ActionGetEmployeeID######


def extract_employee_ids(text):
    pattern = r'\b\d{5}\b'
    return re.findall(pattern, text)

def extract_worked_days(text):
    pattern = r'\b\d{1,2}\b'
    return re.findall(pattern, text)

class ActionGetEmployeeID(Action):
    def name(self) -> Text:
        return "action_get_employee_id"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_input = tracker.latest_message['text']
        
        # Extract 5-digit employee IDs from input
        extracted_ids = extract_employee_ids(user_input)
        
        # Extract 2-digit worked days
        extracted_worked_days = extract_worked_days(user_input)
        
        if len(extracted_ids) == 1:
            employee_id = extracted_ids[0]
            if len(employee_id) == 5:
                # Valid employee ID
                # Establish database connection (you need to fill in the actual details)
                cnx = mysql.connector.connect(user='root', password='root', host='localhost', database='database', port='3306')
                cursor = cnx.cursor()
                query = "SELECT * FROM productivity WHERE Person = '{}'".format(employee_id)
                cursor.execute(query)
                result = cursor.fetchone()
                if not result:
                    dispatcher.utter_message(text="Employee ID not found in the database.")
                else:
                    dispatcher.utter_message(text="Could you please provide me with the date?")
                    return [SlotSet("employee_id", employee_id)]
            else:
                dispatcher.utter_message(text="Employee ID should be 5 digits.")
                return []
        elif len(extracted_worked_days) == 1:
            worked_days = extracted_worked_days[0]
            
            return [SlotSet("worked_days", worked_days)]
        else:
            dispatcher.utter_message(text="Invalid input.")
            return []


    
#######action_get_Specific_Date##### 



class ActionCheckDateInDatabase(Action):
    def name(self) -> Text:
        return "action_get_specific_date"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Extract the date from the user message
        user_message = tracker.latest_message.get("text")
        specific_date = self.extract_date(user_message)
        print(f'specific_date slot:',specific_date)
        employee_id = tracker.get_slot("employee_id")
        print(f"Employee ID1*: {employee_id}")
        if not specific_date:
            dispatcher.utter_message(text="Invalid date format. Please provide the date in the format yyyy-mm-dd.")
            return []

        # Connect to the database and check if the date is in the "Productivity" table
        
        cnx = mysql.connector.connect(
                user='root',
                password='root',
                host='localhost',
                database='database',
                port='3306'
            )
        cursor = cnx.cursor()

            # Replace 'Productivity' with your actual table name in the database
        # Exécution de la requête pour vérifier si l'ID employee (person) est disponible dans la base de données
        query = "SELECT date FROM Productivity WHERE date = '{}'".format(specific_date)
        cursor.execute(query)
        result = cursor.fetchone()
        # Stocker l'ID de l'employé dans une variable de suivi
        tracker.slots['specific_date'] = specific_date
        # Stocker le code de vérification dans une variable de suivi
        print(f'specific_date slot2: {tracker.get_slot("specific_date")}')
        if not result:
            dispatcher.utter_message(text="The date does not exists in the database.")
        

        

        return [SlotSet("specific_date", specific_date),SlotSet("employee_id", employee_id)]

    def extract_date(self, text: str) -> Any:
        # Use regex to extract the date from the user message in the format yyyy-mm-dd or dd-mm-yyyy
        date_pattern = r"(\d{4}-\d{2}-\d{2})|(\d{2}-\d{2}-\d{4})"
        match = re.search(date_pattern, text)

        if match:
            date_str = match.group(0)
            try:
                specific_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                print(f'specific_date extract:',specific_date)
            except ValueError:
                try:
                    specific_date = datetime.strptime(date_str, "%d-%m-%Y").date()
                except ValueError:
                    pass
            else:
                return specific_date.strftime("%Y-%m-%d")  # Convert date to string in 'yyyy-mm-dd' format

        return None
################# date ###########

###########
class ActionDateSlots(Action):
    def name(self) -> Text:
        return "date"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        extracted_slots = []
        begin = None  # Initialize begin and end with default values
        end = None
        employee_id = tracker.get_slot("employee_id")
        worked_days = tracker.get_slot("worked_days")
        print(f"Employee ID*: {employee_id}")
        print(f"worked_days1: {worked_days}")
        # Define regex pattern to match date format
        date_pattern = r'\d{4}-\d{2}-\d{2}'
        
        # Loop through events to find user messages
        for event in tracker.events:
            if event.get('event') == 'user':
                message = event.get('text')
                date_matches = re.findall(date_pattern, message)
                
                if len(date_matches) >= 2:
                    begin, end = date_matches[:2]
                    extracted_slots.append({'begin': begin, 'end': end})
                    # Stocker l'ID de l'employé dans une variable de suivi
        tracker.slots['begin'] = begin
        # Stocker le code de vérification dans une variable de suivi
        print(f'begin slot2: {tracker.get_slot("begin")}')
        tracker.slots['end'] = end
        # Stocker le code de vérification dans une variable de suivi
        print(f'end slot2: {tracker.get_slot("end")}')
        
        return [SlotSet('begin', begin), SlotSet('end', end),SlotSet("employee_id", employee_id),SlotSet("worked_days", worked_days)]
#####################



######################## get_efficiency_day ###################


class CalculateEfficiencyAction(Action):
    def name(self) -> Text:
        return "get_efficiency_day"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        specific_date = tracker.get_slot("specific_date")
        employee_id = tracker.get_slot("employee_id")
        
        # Connect to the MySQL database
        connection = mysql.connector.connect(
                user='root',
                password='root',
                host='localhost',
                database='database',
                port='3306'
        )
        
        cursor = connection.cursor()

        # Initialize efficiency_day with a default value
        efficiency_day = 0.0
        
        # Query the database for productive hours and pointing for the given day and employee
        query = "SELECT Produced_Hours, pointing FROM productivity WHERE Person = %s AND date = %s"
        cursor.execute(query, (employee_id, specific_date))
        result = cursor.fetchone()

        if result:
            productive_hours, pointing = result
            efficiency_day = (productive_hours / pointing) * 100
            
            message = f"Efficiency for employee {employee_id} on {specific_date}: {efficiency_day:.2f}%"
            dispatcher.utter_message(text=message)
            tracker.slots['efficiency_day'] = efficiency_day
            print(f'efficiency_day slot: {tracker.get_slot("efficiency_day")}')
            if efficiency_day >100 : 
                dispatcher.utter_message(text="Produced/Hours or pointing is not correct, verify them.")


        else:
            dispatcher.utter_message(text="No data found for the given employee and day.")
        
        return [SlotSet("efficiency_day", efficiency_day),SlotSet("employee_id", employee_id)]







################get efficiency #############

class CalculateEfficiencyAction(Action):
    def name(self) -> Text:
        return "get_efficiency"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        efficiency = 0.0  
        begin = tracker.get_slot("begin")
        end = tracker.get_slot("end")
        employee_id = tracker.get_slot("employee_id")
        worked_days = tracker.get_slot("worked_days")
        print(f"Begin*: {begin}, End*: {end}, Employee ID*: {employee_id},worked_days:{worked_days}")
        if worked_days is None:
            dispatcher.utter_message(text="Please provide the number of worked days.")
            return []

        worked_days = int(worked_days) 
        # Check if begin and end slots have valid date values
        if begin and end:
            # Connect to the MySQL database
            connection = mysql.connector.connect(
                user='root',
                password='root',
                host='localhost',
                database='database',
                port='3306'
            )
            
            
            cursor = connection.cursor()
            
            # Query the database for productive hours and pointing for the given period and employee
            query = "SELECT SUM(Produced_Hours), SUM(pointing) FROM productivity WHERE Person = %s AND date BETWEEN STR_TO_DATE(%s, %s) AND STR_TO_DATE(%s, %s)"
            cursor.execute(query, (employee_id, begin, '%Y-%m-%d', end, '%Y-%m-%d'))
            result = cursor.fetchone()
            try:
                  cursor.execute(query, (employee_id, begin, '%Y-%m-%d', end, '%Y-%m-%d'))
                  result = cursor.fetchone()

                  print(f"Query executed: {query}")  # Print the executed query for verification

                  if result and result[0] is not None and result[1] is not None:
                    total_productive_hours, total_pointing = result
                    num_days = (datetime.strptime(end, '%Y-%m-%d') - datetime.strptime(begin, '%Y-%m-%d')).days + 1
                    if num_days==30 or num_days==31 or num_days== 29 or num_days==28 and worked_days<=num_days : 
                      
                      efficiency = (total_productive_hours / (total_pointing * worked_days))*100
                      message = f"Efficiency for employee {employee_id} between {begin} and {end}: {efficiency:.2f}%"
                      dispatcher.utter_message(text=message)
                    elif num_days==7 and worked_days<=num_days:
                      
                      efficiency = (total_productive_hours / (total_pointing * worked_days))*100
                      message = f"Efficiency for employee {employee_id} between {begin} and {end}: {efficiency:.2f}%"
                      dispatcher.utter_message(text=message)
                    else :
                        dispatcher.utter_message(text="However, I'm currently unable to perform this calculation for the given period.Try to correct the period")

                    
                    
                    tracker.slots['efficiency'] = efficiency
                    print(f'efficiency slot: {tracker.get_slot("efficiency")}')
                    if efficiency >100 : 
                         dispatcher.utter_message(text="Produced/Hours or pointing is not correct, verify them.")
                  else:
                      dispatcher.utter_message(text="No data found for the given employee and period.")
            except Exception as e:
                print(f"Error occurred: {e}")
                dispatcher.utter_message(text="An error occurred while fetching data from the database.")
            finally:
                cursor.close()
                connection.close()

            

        return [SlotSet("efficiency", efficiency),SlotSet('begin', begin), SlotSet('end', end),SlotSet("employee_id", employee_id),SlotSet("worked_days",worked_days)]



#La classe ActionDefault a pour fonction de gérer les actions par défaut lorsqu'aucune autre action n'est appropriée. (elle active le fallback classifier qui se trouve dans la configuration de rasa)


 

#####
from rasa_sdk.events import UserUttered, UserUtteranceReverted
class ActionGreet(Action):
    def name(self) -> Text:
        return "action_greet"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text = "Hello and welcome to kaschke! I am your virtual assistant.") 
        message2 = "utter_info"
        # envoyer le deuxième message
        dispatcher.utter_message(response = message2)

        return [UserUtteranceReverted()]
#########



