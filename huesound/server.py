#!/usr/bin/env python
# -*- coding: utf-8 -*-
import psycopg2;
from psycopg2.extensions import register_adapter
from flask import Flask, request, session, render_template
import json
import config
import cube

STATIC_PATH = "/static"
STATIC_FOLDER = "../static"
TEMPLATE_FOLDER = "../template"

app = Flask(__name__,
            static_url_path = STATIC_PATH,
            static_folder = STATIC_FOLDER,
            template_folder = TEMPLATE_FOLDER)

register_adapter(cube.Cube, cube.adapt_cube)

def get_images(color, count, country, offset):

    try:
        conn = psycopg2.connect(config.PG_CONNECT)
        cur = conn.cursor()
    except psycopg2.OperationalError as err:
        print "Cannot connect to database: %s" % err
        exit()

    red = int(color[0:2], 16) 
    green = int(color[2:4], 16) 
    blue = int(color[4:6], 16) 

    # TODO: Add country support
    query = """SELECT album_uri, image_id
                 FROM album
             ORDER BY cube_distance(color, %s) 
                LIMIT %s
               OFFSET %s"""
    data = (cube.Cube(red, green, blue), count, offset)
    cur.execute(query, data)

    result = []
    for row in cur:
        result.append({ "album_uri": row[0], "image_id": row[1] })

    return result

@app.route('/<color>/<int:count>/<country>/j')
def images_json(color, count, country):
    return json.dumps(get_images(color, count, country, 0))

@app.route('/<color>/<int:count>/<country>/j/<int:offset>')
def images_json_paged(color, count, country, offset):
    return json.dumps(get_images(color, count, country, offset))

@app.route('/<color>/<int:count>/<country>/h')
def images_html(color, count, country):
    return render_template('icons', data=get_images(color, count, country, 0))

@app.route('/<color>/<int:count>/<country>/h/<int:offset>')
def images_html_paged(color, count, country, offset):
    return render_template('icons', data=get_images(color, count, country, offset))

@app.route('/')
def index():
    return render_template('index')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
