from groq import Groq
import os 
import sqlalchemy
import pandas as pd
import json
import time
import sqlite3 

from dotenv import load_dotenv
import os

# Replace with your OpenAI API key

load_dotenv('../.env')


client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)


def digits_only(input_string):
    return ''.join(filter(str.isdigit, input_string))


def groq_query(ad_text):
    output = ''
    completion = client.chat.completions.create(
    # model="llama3-groq-70b-8192-tool-use-preview",
    model="llama-3.1-70b-versatile",
    messages=[
        {
            "role": "system",
            "content": """Find me name of the village or closest location in the text, it's GPS coordinates and driving distance from Belgrade. 
                          Return answer only in JSON format { \"village\": \"VILLAGE\", \"gps_coordinates\": \"LONGITUDE, LATITUDE\", \"driving_distance\": \"DISTANCE\" }
                          Without any explanations before or after JSON. If you can not find some value return empty string ''.  
            """
        },
        {
            "role": "user",
            "content": f"{ad_text}"
        }
    ],
    temperature=0.5,
    max_tokens=1024,
    top_p=0.65,
    stream=True,
    stop=None,
    )


    for chunk in completion:
        output = output + (chunk.choices[0].delta.content or "")
        # print(chunk.choices[0].delta.content or "", end="")   
    
    return output


def groq_format_response(response):
    """
    response = groq_query(f"{row['ad_full_title']} {row['ad_full_description']}")
    
    """

    try:
        response = json.loads(response)
        print(response)
        if ('village' not in response):
            response['village'] = ''
        if ('gps_coordinates' not in response):
            response['gps_coordinates'] = ''
        else:
            lat, lon =  response['gps_coordinates'].split(',')
            if float(lat) < float(lon):
                response['gps_coordinates'] = f"{lon}, {lat}"

        if ('driving_distance' not in response):
            response['driving_distance'] = ''
    except:
        print(response)
        response = { 
                    'village' : '', 
                    'gps_coordinates' : '', 
                    'driving_distance' : ''
                    } 
        
    return response


def example():
    completion = client.chat.completions.create(
        model="llama3-groq-70b-8192-tool-use-preview",
        messages=[
            {
                "role": "system",
                "content": "Find me name of the village in the text, it's GPS coordinates and driving distance from Belgrade. Return answer only in JSON format { \"village\": \"VILLAGE\", \"gps_coordinates\": \"LATITUDE, LONGITUDE \", \"driving_distance_from_Belgrade\": \"DISTANCE\" }"
            },
            {
                "role": "user",
                "content": "Na prodaju gradjevinsko zemljiste (domacinstvo) u podnozju Kosmaja selo Rogača na površini oko 1.3 ha na veoma atraktivnoj lokaciji u blizini restorana La montanja, bazena Verona i kompleksa Kosmaj Residenca , dve kuće i sve pomoćne zgrade , kucevni plac , livada i suma sve spojeno , na drugoj slici tri parcele su obeležene crveno zaokruženo , struja , gas , gradska voda, optika internet , cena 1250 eura po aru za kupovinu celog placa , veoma pogodno za dalje investicije , po zelji i dogovoru cene moze i manji deo parcele jer ima mogucnost da se uradi i put u duzini svi parcela u tom slucaju cena je veca , za više info poziv . ID Oglasa: #131589831Prijavi"
            }
        ],
        temperature=0.5,
        max_tokens=1024,
        top_p=0.65,
        stream=True,
        stop=None,
    )
    i = 0
    output = ""
    for chunk in completion:
        print(f"i: ")
        i = i + 1
        output = output + (chunk.choices[0].delta.content or "")
        print(output)
        # print(chunk.choices[0].delta.content or "", end="")

    print(output)






if __name__ == '__main__':

    # cnx = sqlalchemy.create_engine("sqlite:////home/homoludens/PycharmProjects/selenium/flask_app/placevi_oglasi.sqlite")  
    # conn = cnx.connect()

    # oglasi_all = pd.read_sql('select * from kupujem_prodajem limit 10', con=cnx)

    # for i, oglas in oglasi_all.iterrows():
    #     response = groq_query(f"{oglas.ad_full_title} {oglas.ad_full_description}")
    #     print(response)


    connection = sqlite3.connect("./data/placevi_oglasi.sqlite")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()


    rows = cursor.execute("SELECT * from facebook WHERE llm_village IS NULL").fetchall()
    rows_dict = [dict(row) for row in rows]

    for row in rows_dict:
        time.sleep(4)
        response = groq_query(f"{row['ad_full_title']} {row['ad_full_description']}")
        try:
            response = json.loads(response)
            print(response)
            if ('village' not in response):
                response['village'] = ''
            if ('gps_coordinates' not in response):
                response['gps_coordinates'] = ''
            if ('driving_distance' not in response):
                response['driving_distance'] = ''
        except:
            print(response)
            response = { 
                        'village' : '', 
                        'gps_coordinates' : '', 
                        'driving_distance' : ''
                        }
        

        # row["llm_village"] = response["village"]
        # row["llm_gps_coordinates"] = response["gps_coordinates"]
        # row["llm_driving_distance"] = response["driving_distance"]


        cursor.execute(f"""UPDATE facebook 
                        SET llm_village = '{response["village"]}', llm_gps_coordinates = '{response["gps_coordinates"]}', llm_driving_distance = '{response["driving_distance"]}'
                        WHERE id={row['id']}  """)
    
        connection.commit()



    rows = cursor.execute("SELECT * from kupujem_prodajem WHERE llm_village IS NULL").fetchall()
    rows_dict = [dict(row) for row in rows]

    for row in rows_dict:
        time.sleep(4)
        response = groq_query(f"{row['ad_full_title']} {row['ad_full_description']}")
        try:
            response = json.loads(response)

            if ('village' not in response):
                response['village'] = ''
            if ('gps_coordinates' not in response):
                response['gps_coordinates'] = ''
            if ('driving_distance' not in response):
                response['driving_distance'] = ''
        except:
            print(response)
            response = { "village" : '', 
                        "gps_coordinates" : '', 
                        'driving_distance' : ''
                        }
        print(response)

        cursor.execute(f"""UPDATE kupujem_prodajem 
                        SET llm_village = '{response["village"]}', llm_gps_coordinates = '{response["gps_coordinates"]}', llm_driving_distance = '{response["driving_distance"]}'
                        WHERE id={row['id']}  """)
    
        connection.commit()    
    
    
    


    # df_todb.to_sql(name = 'newTable',con= dbEngine, index=False, if_exists='replace') 
 
