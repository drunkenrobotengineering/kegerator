#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import boto
import time

from boto.dynamodb2.items import Item
from boto.dynamodb2.table import Table
from boto.s3.key import Key
from datetime import datetime
from quik import FileLoader

drinkers_table = Table('drinkers')
s3 = boto.connect_s3()

def scrape_data_to_csv():
    all_drinkers = drinkers_table.scan()
    with open("booze.csv", "w") as f:
        f.write("{0},{1},{2},{3}".format("CODE","NAME","NUMBER_OF_DRINKS","VOLUME_CONSUMED"))
        for drinker in all_drinkers:
            if (drinker['drinker_id'] == None):
                drinker['drinker_id'] = "UNKNOWN"
            if (drinker['name'] == None):
                drinker['name'] = "UNKNOWN"
            if (drinker['volume_consumed'] == None):
                drinker['volume_consumed'] = 0
            if (drinker['number_of_drinks'] == None):
                drinker['number_of_drinks'] = 0
            f.write("{0},{1},{2},{3}\n".format(drinker['drinker_id'], drinker['name'], drinker['number_of_drinks'], drinker['volume_consumed']))

def scrape_data_to_html():
    timestamp = datetime.fromtimestamp(time.time()).strftime("%H:%M:%S on %A, %d %B, %Y")
    all_drinkers = drinkers_table.scan()
    drinkers = []
    for drinker in all_drinkers:
        if (drinker['drinker_id'] == None):
            drinker['drinker_id'] = "UNKNOWN"
        if (drinker['name'] == None):
            drinker['name'] = "UNKNOWN"
        if (drinker['volume_consumed'] == None):
            drinker['volume_consumed'] = 0
        if (drinker['number_of_drinks'] == None):
            drinker['number_of_drinks'] = 0
        d = {}
        d['drinker_id'] = drinker['drinker_id']
        d['name'] = drinker['name']
        d['volume_consumed'] = drinker['volume_consumed']
        d['number_of_drinks'] = drinker['number_of_drinks']
        drinkers.append(d)
    loader = FileLoader('templates')
    template = loader.load_template('drinks.html.template')
    webpage = template.render(locals())
    bucket = s3.get_bucket('kegerator')
    key = Key(bucket)
    key.key = 'drinks.html'
    key.content_type = 'text/html'
    key.set_contents_from_string(webpage)
    key.make_public()

if __name__ == "__main__":
    scrape_data_to_html()
