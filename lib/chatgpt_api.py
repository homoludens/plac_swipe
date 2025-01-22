import openai
import json
import sqlite3
from dotenv import load_dotenv
import os

# Replace with your OpenAI API key


load_dotenv('../.env')

openai.api_key = os.getenv("OPENAI_API_KEY")

print(openai.api_key)

from openai import OpenAI
client = OpenAI(api_key=openai.api_key)

# completion = client.chat.completions.create(
#   model="gpt-4",
#   messages=[
#     {"role": "system", "content": "You are a helpful assistant."},
#     {"role": "user", "content": "Hello!"}
#   ]
# )

# print(completion.choices[0].message)


# chat_completion = client.chat.completions.create(
#     messages=[
#         {
#             "role": "user",
#             "content": "Say this is a test",
#         }
#     ],
#     model="gpt-4",
# )

# chat_completion.choices[0].message.content


def query_chatgpt(prompt):
    try:
        # Query the GPT-4 model
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {   "role": "system", 
                    "content":  """ Find me name of the village or closest location in the text, it's GPS coordinates and driving distance from Belgrade. 
                                    Return answer only in JSON format { \"village\": \"VILLAGE\", \"gps_coordinates\": \"LONGITUDE, LATITUDE\", \"driving_distance\": \"DISTANCE\" }
                                    Without any explanations before or after JSON. If you can not find some value return empty string ''.  
                                """
                },
                {"role": "user", "content": prompt}
            ],
            # max_tokens=2000,
            # n=1,
            # stop=None,
            # temperature=0.7,
        )

        # Extract the response from the model
        gpt_response = response.choices[0].message.content
        
        # Return the response as a JSON formatted string
        return json.loads(gpt_response)
    
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=4)



def test():
    # Example prompt to send to GPT-4

    test_prompts = [
    """
    Na prodaju vikendica 22 ari placa, vlasnik 1/1. Ima struju, blizu glavnog puta izmedju Omoljice i Bredtovca. 
    Ima veliki vinograd koji doseze do Ponjavice, veliku obradivu povrsinu, kuca sa dve sobe gore i terasom i dole u 
    podrumu jos dve prostorije. Oaza mira i tišine, idealno mesto za miran zivot, odmor, pecanje. . .
    Za ozbiljne kupce dogovor oko cene. 40000 e.   Vredi pogledati. Srecna kupovina
    """,
    """
    Prodaje se plac u naselju Kalakaca pored Beske. Od obale Dunava i restorana Sidro oko 1000 m udaljen. Na placu je montazna kuca od 33 kvm. Ima struja voda do placa. Kuca legalizovana i sve uknjizeno. Vlasnik.
    Do placa ima dva prilaza, iz dve ulice. Asfalt do placa.
    """,
    """
    Vikendica na prodaju (POGODNA ZA ETNO SELO) na 114 ari placa sa cetiri  objekta na placu vikendica se nalazi 500  metara od puta u sumu na 300 metara od puta je kanal DTD na sam ulaz u grebenac u blizini su i zagajacka brda struja je dobiva preko solarnih panela a i moze da se struja dovede do vikendice vode ima preko hidropaka NOVO kupatilo i lepo uredjene sobe  vise informacija pozvati broj 0612761775
    """,
    """
    Na prodaju vikendica pored Dunava, 2 Km uzvodno od Djerdapa 2, opstina Negotin, legalizovana,
    useljiva, korisne povrsine 60 met. kv plus 3 terase 45 met. kv, na bazi dvosobnog stana, plac povrsine 500 met. kv. Moguca je zamena za stan u Sokobanji ili u Negotinu uz dogovor. Za dodatne informacije nazvati na tel. 063452842 ili na Whattsapp 00381 63452842 
    ( posto radim u inostranstvu, ali sam cesto u Srbiji), takodje na e-mail: v. djordjevic@ptt. rs . Vitomir Djordjevic
    """,
    """
    Na prodaju prelepa vikendica u Sićevu. Nalazi se u naseljenom delu, okružena prirodom. Idealna nekretnina za ljubitelje prirode i života van buke. Vikendica je uknjižene kvadrature 63m2, vrlo kvalitetne gradnje sa fasadnom ciglom. Unutrašnost vikendice je potrebno adaptirati. Nekretnina nema struju, ali postoji mogućnost za priključak. Voda je sprovedena. Uknjižena, čisto vlasništvo 1/1. Topla preporuka agencije! Ovo je samo deo naše ponude, za više informacija javite se i posetite naš sajt.

    Agencija Bulevar nekretnine, registarski broj posrednika 1487.  
    Za više informacija, javite se na broj 0184155470.  
    We have agents who speak both Russian and English!
    У нас есть агенты, говорящие как на русском, так и на английском языке!

    """,
    """
    Kuća na prodaju 7,25x8,60 na placu od 6ari. Kuća se nalazi u selu Rešetar br 70A opština Plitvička jezera. Kuća je legalizovana uradjen nov krov, jedan vlasnik. U lepom prirodnom okruženju udaljena od Plitvičkih jezera 15ak kilometara. Za više informacija pozovite tel+381 91 73 05 294. Može i poziv na viber i whatsApp. Jovo.

    """

    ] 

    for prompt in test_prompts:
        # prompt = 
        result = query_chatgpt(prompt)

        # Print the result
        print(result)


def format_response(response):
    """
    response = groq_query(f"{row['ad_full_title']} {row['ad_full_description']}")
    
    """

    try:
        # response = json.loads(response)
        # print(response)
        if ('village' not in response):
            response['village'] = ''

        if ('gps_coordinates' not in response) and ():
            response['gps_coordinates'] = ''
        else:
            if response['gps_coordinates'] != '':
                lat, lon =  response['gps_coordinates'].split(',')
                if float(lat) < float(lon):
                    response['gps_coordinates'] = f"{lon}, {lat}"

        if ('driving_distance' not in response):
            response['driving_distance'] = ''

    except Exception as e:
        print(e)
        response = { 
                    'village' : '', 
                    'gps_coordinates' : '', 
                    'driving_distance' : ''
                    } 
        
    return response


if __name__ == "__main__":

    # print(test())
    # con = sqlite3.connect('placevi_oglasi_FB14.sqlite')
    # con = sqlite3.connect('placevi_oglasi_KPtest8.sqlite')
    con = sqlite3.connect('./data/placevi_oglasi.sqlite')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    # datas = cur.execute(f"SELECT * FROM facebook WHERE favourite=0 AND llm_village=''")
    datas = cur.execute(f"SELECT * FROM kupujem_prodajem WHERE favourite=0")
    datas = [dict(row) for row in datas.fetchall()]
    print(f"len: {len(datas)}")

    for d in datas:
        print(f"id: {d['id']}")
        prompt = d['ad_full_title'] + ' ' + d['ad_full_description'] 
        response = query_chatgpt(prompt)
        # print(f"prompt: {prompt}")
        print(f"query_chatgpt: {response}")

        response = format_response(response)

        # response['village'], response['gps_coordinates'], response['driving_distance']
        d['llm_village'] = response['village']
        d['llm_gps_coordinates'] = response['gps_coordinates']
        d['llm_driving_distance'] = response['driving_distance']
    
        set_clause = ", ".join([f"{key} = ?" for key in d.keys()])
        # update_query = f"UPDATE facebook SET {set_clause} WHERE id = {d['id']}"
        update_query = f"UPDATE kupujem_prodajem SET {set_clause} WHERE id = {d['id']}"
        values = list(d.values())
        
        # cur = con.cursor()
        cur.execute(update_query, values)
    
        con.commit()

    # print(datas)

