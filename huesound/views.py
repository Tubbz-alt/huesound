# -*- coding: utf-8 -*-
import psycopg2;
from psycopg2.extensions import register_adapter
from huesound import config
from huesound.utils import render_template, render_json, expose, validate_url, url_for
from huesound import cube

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

    query = """SELECT album_uri, image_id
                 FROM color_cube cc, country_string_country csc, country_string cs 
                WHERE csc.country_string = cs.id 
                  AND cc.countries = csc.country_string 
                  AND csc.country = (select id from country where code = %s) 
             ORDER BY cube_distance(color, %s) 
                LIMIT %s
               OFFSET %s"""
    data = (country, cube.Cube(red, green, blue), count, offset)
    cur.execute(query, data)

    result = []
    for row in cur:
        result.append({ "album_uri": row[0], "image_id": row[1] })

    return result

@expose('/<color>/<count>/<country>/j')
def images_json(request, color, count, country):
    return render_json(get_images(color, count, country, 0))

@expose('/<color>/<count>/<country>/j/<int:offset>')
def images_json_paged(request, color, count, country, offset):
    return render_json(get_images(color, count, country, offset))

@expose('/<color>/<count>/<country>/h')
def images_html(request, color, count, country):
    return render_template('icons.html', data=get_images(color, count, country, 0))

@expose('/<color>/<count>/<country>/h/<int:offset>')
def images_html_paged(request, color, count, country, offset):
    return render_template('icons.html', data=get_images(color, count, country, offset))
