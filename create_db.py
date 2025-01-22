import sqlite3 as sql

#connect to SQLite
con = sql.connect('placevi_oglasi.db')

#Create a Connection
cur = con.cursor()

#Drop users table if already exsist.
# cur.execute("DROP TABLE IF EXISTS facebook")
# cur.execute("DROP TABLE IF EXISTS kupujem_prodajem")

#Create users table  in db_web database
sql ='''CREATE TABLE "facebook_inc" (
  "id" INT NOT NULL AUTO_INCREMENT,
  "ad_link" TEXT,
  "ad_full_title" TEXT,
  "ad_full_price" TEXT,
  "ad_full_description" TEXT,
  "ad_full_image" TEXT,
  "ad_user_page" TEXT,
  "date" TIMESTAMP
)'''
cur.execute(sql)


sql ='''CREATE TABLE "kupujem_prodajem" (
  "id" INT NOT NULL AUTO_INCREMENT,
  "ad_link" TEXT,
  "ad_full_title" TEXT,
  "ad_full_price" TEXT,
  "ad_full_description" TEXT,
  "ad_full_image" TEXT,
  "ad_user_page" TEXT,
  "date" TIMESTAMP
)'''
cur.execute(sql)

#commit changes
con.commit()

#close the connection
con.close()



# {"village": "Vrnchanima", "gps_coordinates": "20.4548, 44.2158", "driving_distance": "150 km"}
"""

DROP TABLE IF EXISTS kupujem_prodajem_inc;

CREATE TABLE kupujem_prodajem_inc (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "ad_link" TEXT,
  "ad_date" TEXT,
  "ad_full_title" TEXT,
  "ad_full_price" TEXT,
  "ad_full_description" TEXT,
  "ad_full_image" TEXT,
  "ad_user_page" TEXT,
  "llm_village": TEXT,
  "llm_gps_coordinates" TEXT,
  "llm_driving_distance" TEXT,
  "favourite" INTEGER DEFAULT 0,
  "date" TIMESTAMP
);

INSERT INTO kupujem_prodajem_inc (ad_link, ad_full_title, ad_full_price, ad_full_description, ad_full_image, ad_user_page, llm_village, llm_gps_coordinates, llm_driving_distance, date
SELECT ad_link, ad_full_title, ad_full_price, ad_full_description, ad_full_image, ad_user_page, llm_village, llm_gps_coordinates, llm_driving_distance, date
FROM kupujem_prodajem;

DROP TABLE kupujem_prodajem;
ALTER TABLE kupujem_prodajem_inc RENAME TO kupujem_prodajem;



DROP TABLE IF EXISTS facebook_inc;

CREATE TABLE facebook_inc (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "ad_link" TEXT,
  "ad_date" TEXT,
  "ad_full_title" TEXT,
  "ad_full_price" TEXT,
  "ad_full_description" TEXT,
  "ad_full_image" TEXT,
  "ad_user_page" TEXT,
  "llm_village" TEXT,
  "llm_gps_coordinates" TEXT,
  "llm_driving_distance" TEXT,
  "favourite" INTEGER DEFAULT 0,
  "date" TIMESTAMP
);

INSERT INTO facebook_inc (ad_link, ad_full_title, ad_full_price, ad_full_description, ad_full_image, ad_user_page, llm_village, llm_gps_coordinates, llm_driving_distance, date)
SELECT ad_link, ad_full_title, ad_full_price, ad_full_description, ad_full_image, ad_user_page, llm_village, llm_gps_coordinates, llm_driving_distance, date
FROM facebook;

DROP TABLE facebook;
ALTER TABLE facebook_inc RENAME TO facebook;




"""