# from groq import Groq
# import os 
# import sqlalchemy
# import pandas as pd
# import json
# import time
import sqlite3 


def digits_only(input_string):
    return ''.join(filter(str.isdigit, input_string))



connection = sqlite3.connect("./data/placevi_oglasi.sqlite")
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

# rows = cursor.execute("SELECT id, ad_full_price from facebook").fetchall()
rows = cursor.execute("SELECT id, ad_full_price from kupujem_prodajem").fetchall()
rows_dict = [dict(row) for row in rows]

for row in rows_dict:
    cursor.execute(f"""UPDATE facebook 
                    SET ad_full_price = '{digits_only(row["ad_full_price"])}'
                    WHERE id={row['id']}  """)

    connection.commit()