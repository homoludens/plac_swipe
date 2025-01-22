from flask import Flask, jsonify, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy


from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5

from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length
import secrets
from sqlalchemy.sql.expression import cast

import sqlite3
from shapely import wkt
import geopandas as gpd
from lib.ko_imena import ko_imena

app = Flask(__name__) 


foo = secrets.token_urlsafe(16)
app.secret_key = foo
# app.secret_key = 'tO$&!|0wkamvVia0?n$NqIRVWOG'
# Bootstrap-Flask requires this line
bootstrap = Bootstrap5(app)
# Flask-WTF requires this line
csrf = CSRFProtect(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///.data/placevi_oglasi.sqlite"  # KONFIGURASI DATABASE
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////home/homoludens/PycharmProjects/selenium/oglasi_flask/placevi_oglasi_FB12.sqlite"  # KONFIGURASI DATABASE
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////home/homoludens/PycharmProjects/selenium/placevi_oglasi_FB14.sqlite"  # KONFIGURASI DATABASE
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////home/homoludens/PycharmProjects/selenium/placevi_oglasi_KPtest8.sqlite" 

db = SQLAlchemy(app) # Membuat Object SQLAlchmy


def convert_epsg(geometry_wkt):
    gdf = gpd.GeoDataFrame(geometry=[wkt.loads(geometry_wkt)])
    # gdf['geometry'] = [wkt.loads(geometry_wkt)]
    gdf = gpd.GeoDataFrame(gdf).set_geometry('geometry').set_crs('EPSG:32634').to_crs('EPSG:4326') # EPSG:3857
    a = gdf.geometry.iloc[0]
    a = list(a.geoms)[0]
    b = [[i[1], i[0] ] for i in list(a.exterior.coords)]

    return (a.centroid.x, a.centroid.y), b


class SerchForm(FlaskForm):


    maximum_price = StringField('Maximum price?')
    distance = StringField('Distace?')
    favourite = BooleanField('Fav?')
    submit = SubmitField('Submit')

    ko_ime = StringField('ko_ime') 


class ParcelSerchForm(FlaskForm):

    opstine = ['LJIG', 'MIONICA', 'VALJEVO', 'GORNJI MILANOVAC', 'ARANĐELOVAC', 'TOPOLA', 'SOPOT', 'GROCKA', 'MLADENOVAC', 
        'SMEDEREVO', 'SMEDEREVSKA PALANKA', 'VELIKA PLANA', 'RAČA', 'LAPOVO', 'ŽABARI', 'PETROVAC NA MLAVI', 'SVILAJNAC', 
        'ZAJEČAR']
    
    # ko_ime = ko_imena
    ko_ime = SelectField('ko_ime', choices=ko_imena )  
    parcela_id = StringField('parcela_id')
    submit = SubmitField('Search')


  
# Membuat model product
class facebook(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    ad_link = db.Column(db.Text)
    ad_full_title = db.Column(db.Text, nullable=False)
    ad_full_price = db.Column(db.Text, nullable=False)
    ad_full_description = db.Column(db.Text, nullable=False)
    ad_full_image = db.Column(db.Text, nullable=False)
    ad_user_page = db.Column(db.Text, nullable=False)
    llm_village = db.Column(db.Text, nullable=False)
    llm_gps_coordinates = db.Column(db.Text, nullable=False)
    llm_driving_distance = db.Column(db.Text, nullable=False)
    favourite = db.Column(db.Integer)
    date = db.Column(db.DateTime , nullable=False)


class kupujem_prodajem(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    ad_link = db.Column(db.Text, nullable=False)
    ad_full_title = db.Column(db.Text, nullable=False)
    ad_full_price = db.Column(db.Text, nullable=False)
    ad_full_description = db.Column(db.Text, nullable=False)
    ad_full_image = db.Column(db.Text, nullable=False)
    ad_user_page = db.Column(db.Text, nullable=False)
    llm_village = db.Column(db.Text, nullable=False)
    llm_gps_coordinates = db.Column(db.Text, nullable=False)
    llm_driving_distance = db.Column(db.Text, nullable=False)
    favourite = db.Column(db.Integer)
    date = db.Column(db.DateTime , nullable=False)    
# Membuat route untuk menangani GET & POST

# @app.route("/add", methods = ["GET", "POST"])
# def handle_request():
#     if request.method == "POST":
#         name = request.form["name"]
#         price = request.form["price"]
#         new_product = facebook(name=name, price=price)
#         db.session.add(new_product)
#         db.session.commit()
#         return redirect("/")
#     else:
#         products = facebook.query.all()
#         return render_template('index.html', products=products)

# # Route edit product
# @app.route("/edit/<int:id>", methods=["GET", "POST"])
# def edit_product(id):
#     product = facebook.query.get(id)
#     if request.method == "POST":
#         product.name = request.form["name"]
#         product.price = request.form["price"]
#         db.session.commit()
#         return redirect("/") 
#         return render_template("edit.html", product=product)

# # Route delete product
# @app.route("/delete/<int:id>", methods=["POST"])
# def delete_product(id):
#     product = Product.query.get(id)
#     db.session.delete(product)
#     db.session.commit()
#     return redirect("/")

# #Menampilkan semua product

@app.route('/', methods=['GET', 'POST'])
def show_all_products():
    maximum_price = 1000
    fav = 0 

    form = SerchForm()
    message = ""

    if form.validate_on_submit():
        maximum_price = form.maximum_price.data
        fav = 1 if form.favourite.data else -1
        # if isinstance(maximum_price, int):
        #     # # empty the form field
        #     # form.name.data = ""
        #     # id = get_id(ACTORS, name)
        #     # # redirect the browser to another route and template
        #     # return redirect( url_for('actor', id=id) )
        # else:
        #     message = "error."


    with app.app_context():
        datas = db.paginate( db.select(facebook).where(cast(facebook.ad_full_price, db.Integer) < maximum_price).where(facebook.favourite == fav)) 
        # datas = db.paginate( db.select(kupujem_prodajem).where(cast(kupujem_prodajem.ad_full_price, db.Integer) < maximum_price)) 
        return render_template("index2.html", datas=datas, form=form, message=message)
    


@app.route('/tinder', methods=['GET', 'POST'])
def tinder():
    maximum_price = 500000

    # form = SerchForm(request.args)
    form = SerchForm()
    message = "test message"

    if form.validate_on_submit():
        maximum_price = form.maximum_price.data
        form.maximum_price.data = maximum_price


    if request.method == 'GET':
        try:
            maximum_price = request.args['maximum_price']
        except:
            pass

    with app.app_context():
        datas = db.paginate( db.select(facebook).where(cast(facebook.ad_full_price, db.Integer) < maximum_price)
                                                .where(facebook.favourite>=0).order_by(facebook.date.desc())
                            , per_page=1)
        # datas = db.paginate( db.select(kupujem_prodajem).where(cast(kupujem_prodajem.ad_full_price, db.Integer) < maximum_price).where(kupujem_prodajem.favourite>=0)
        #                     , per_page=1)
        return render_template("tinder.html", datas=datas, form=form, message=message, maximum_price=maximum_price) 
    


@app.route('/parcela_search', methods=['GET', 'POST'])
def parcela_search():
    geosrbija_con = sqlite3.connect("./data/geosrbija.sqlite")
    geosrbija_con.row_factory = sqlite3.Row

    form = ParcelSerchForm()
    message = "test message"
    ko_ime = 'VALJEVO'
    parcela_id = '111'



    # index	ko_id	ko_ime	opstina_id	opstina_ime	parcela_id	in_date	geometry_wkt
    
    if form.validate_on_submit():
        ko_ime = form.ko_ime.data
        parcela_id = form.parcela_id.data
        # if isinstance(maximum_price, int):
        #     # # empty the form field
        #     # form.name.data = ""
        #     # id = get_id(ACTORS, name)
        #     # # redirect the browser to another route and template
        #     # return redirect( url_for('actor', id=id) )
        # else:
        #     message = "error."


    with app.app_context():

        cur = geosrbija_con.cursor()

        datas = cur.execute(f"SELECT ko_id, ko_ime,	opstina_id,	opstina_ime, parcela_id, geometry_wkt FROM parcele_opstine WHERE ko_ime='{ko_ime}' AND parcela_id LIKE'{parcela_id}%'")

        datas = [dict(row) for row in datas.fetchall()]
        # geometry_wkt = convert_epsg(datas[0]['geometry_wkt'])
        
        datas2 = []
        for data in datas:

            data['geometry'] = wkt.loads(data['geometry_wkt'])
            #  = (datas[0]['geometry'].centroid.x , datas[0]['geometry'].centroid.y)
            data['centroid'], data['geometry_list'] = convert_epsg(data['geometry_wkt'])
               
            datas2.append(data)
        
        print(len(datas2))
        # datas = db.paginate( db.select(facebook).where(cast(facebook.ad_full_price, db.Integer) < maximum_price), per_page=1)
        return render_template("parcela_search.html", datas=datas2, centroid = data['centroid'], form=form, message=message) 
    

@app.route("/kp")
def show_all_products_kp():
    with app.app_context():
        datas = db.paginate(db.select(kupujem_prodajem))
        return render_template("index_kp.html", datas=datas)    


@app.route("/geosearch", methods=['GET'])
def geo_search():
    data = [ {"loc":[41.575330,13.102411], "title":"aquamarine"},
        {"loc":[41.575730,13.002411], "title":"black"},
        {"loc":[41.807149,13.162994], "title":"blue"},
        {"loc":[41.507149,13.172994], "title":"chocolate"},
        {"loc":[41.847149,14.132994], "title":"coral"},
        {"loc":[41.219190,13.062145], "title":"cyan"},
        {"loc":[41.344190,13.242145], "title":"darkblue"},	
        {"loc":[41.679190,13.122145], "title":"Darkred"},
        {"loc":[41.329190,13.192145], "title":"Darkgray"},
        {"loc":[41.379290,13.122545], "title":"dodgerblue"},
        {"loc":[41.409190,13.362145], "title":"gray"},
        {"loc":[41.794008,12.583884], "title":"green"},	
        {"loc":[41.805008,12.982884], "title":"greenyellow"},
        {"loc":[41.536175,13.273590], "title":"red"},
        {"loc":[41.516175,13.373590], "title":"rosybrown"},
        {"loc":[41.506175,13.273590], "title":"royalblue"},
        {"loc":[41.836175,13.673590], "title":"salmon"},
        {"loc":[41.796175,13.570590], "title":"seagreen"},
        {"loc":[41.436175,13.573590], "title":"seashell"},
        {"loc":[41.336175,13.973590], "title":"silver"},
        {"loc":[41.236175,13.273590], "title":"skyblue"},
        {"loc":[41.546175,13.473590], "title":"yellow"},
        {"loc":[41.239190,13.032145], "title":"white"}]

    return jsonify(data)


@app.route("/post/favourite", methods=['POST'])
# def favorite(post_id, set_on_off):
def favorite():

    post = ''
    post_id = int(request.json['post_id'])
    set_on_off = int(request.json['set_on_off'])

    assert isinstance(post_id, int)
    assert isinstance(set_on_off, int)

    if request.method == 'POST':
        try:
            post = facebook.query.get(post_id)
            # post = kupujem_prodajem.query.get(post_id)
            
            post.favourite = set_on_off
        except Exception as e:
            print(f'error {e}')

        
        db.session.commit()
        
    print(post.favourite)
    data = {'success': True, 'id': post_id, 'fav':  set_on_off}
    return jsonify(data)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)