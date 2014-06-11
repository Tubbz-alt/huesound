#!/usr/bin/env python
# -*- coding: utf-8 -*-
import psycopg2;
from psycopg2.extensions import register_adapter
from flask import Flask, request, session, render_template
import json
import config
import cube
import memcache

STATIC_PATH = "/static"
STATIC_FOLDER = "../static"
TEMPLATE_FOLDER = "../template"

CACHE_TIME = 60 * 60 * 12

app = Flask(__name__,
            static_url_path = STATIC_PATH,
            static_folder = STATIC_FOLDER,
            template_folder = TEMPLATE_FOLDER)

register_adapter(cube.Cube, cube.adapt_cube)

def get_images(color, count, country, year, type, offset):

    try:
        conn = psycopg2.connect(config.PG_CONNECT)
        cur = conn.cursor()
    except psycopg2.OperationalError as err:
        print "Cannot connect to database: %s" % err
        exit()

    red = int(color[0:2], 16) 
    green = int(color[2:4], 16) 
    blue = int(color[4:6], 16) 
    query = """SELECT album_uri, image_id
                 FROM album a, album_country ac, country c
                WHERE ac.album = a.id 
                  AND ac.country = c.id
                  AND c.code = %s """
    data = [country]

    if year != "all":
        begin, end = year.split("-")

        query += """AND year >= %s
                    AND year <= %s """
        data.append(begin)
        data.append(end)

    if type != "all":
        query += """AND type = %s """
        data.append(type)

    query += """ORDER BY cube_distance(color, %s) 
                   LIMIT %s
                  OFFSET %s"""
    data.extend([cube.Cube(red, green, blue), count, offset])
    cur.execute(query, tuple(data))

    result = []
    for row in cur:
        result.append({ "album_uri": row[0], "image_id": row[1] })

    return result

@app.route('/<color>/<int:count>/<country>/<year>/<type>/j/<int:offset>')
def images_json_paged(color, count, country, year, type, offset):

    mc = memcache.Client(['127.0.0.1:11211'], debug=0)
    result = mc.get(str("%s-%d-%s-%s-%s-%d" % (color, count, country, year, type, offset)))
    if result:
	return result

    result = "mbalbums(" + json.dumps(get_images(color, count, country, year, type, offset)) + ")"
    mc.set(str("%s-%d-%s-%s-%s-%d" % (color, count, country, year, type, offset)), result, time=CACHE_TIME)

    return result

@app.route('/<color>/<int:count>/<country>/<year>/<type>/h/<int:offset>')
def images_html_paged(color, count, country, year, type, offset):
    return render_template('icons', data=get_images(color, count, country, year, type, offset))

@app.route('/')
def index():
    return render_template('index')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
