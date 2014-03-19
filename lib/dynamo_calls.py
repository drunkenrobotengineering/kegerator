#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

from datetime import datetime
from decimal import Decimal
import os
import sys
import time

from boto.dynamodb2.items import Item
from boto.dynamodb2.table import Table

drinkers = Table('drinkers')
drinks = Table('drinks')
fobs = Table('fobs')
kegs = Table('kegs')
payers = Table('payers')

def set_if_none(dict, key, value):
    if dict[key] is None:
        dict[key] = str(value)

def price(number):
    floor = number.quantize(Decimal("0.01"))
    if number - floor >= .005:
        flor = floor + Decimal('.01')
    return floor

def get_fob(fob_id):
    fob = fobs.get_item(fob_id=str(fob_id))
    return fob

def get_drinker(drinker_id):
    drinker = drinkers.get_item(drinker_id=drinker_id)
    if not drinker:
        drinker = Item(drinkers, data={
                'drinker_id': str(drinker_id),
                'volume_consumed': str(0),
                'number_of_drinks' : str(0)
                })
    set_if_none(drinker, 'drinker_id', drinker_id)
    set_if_none(drinker, 'payer_id', drinker_id)
    set_if_none(drinker, 'name', 'unknown')
    set_if_none(drinker, 'email', 'unknown')
    set_if_none(drinker, 'volume_consumed', 0)
    set_if_none(drinker, 'alcohol_consumed', 0)
    set_if_none(drinker, 'number_of_drinks', 0)
    set_if_none(drinker, 'total_cost', 0)
    return drinker

def get_drinker_from_fob(fob_id):
    fob = get_fob(fob_id)
    if fob is None or fob['drinker_id'] is None:
        return None
    drinker = get_drinker(fob['drinker_id'])
    if drinker is None:
        return None
    return drinker

def get_payer(payer_id):
    payer = payers.get_item(payer_id=payer_id)
    if not payer:
        payer = Item(payers, data={
                'payer_id': str(payer_id),
                'credit': str(0)
                })
    set_if_none(payer, 'payer_id', payer_id)
    set_if_none(payer, 'credit', 0)
    return payer

def get_current_keg(tap):
    keg_result_set = kegs.query(
        tap__eq=str(tap),
        finish_timestamp__lt=str(0)
    )
    for keg in keg_result_set:
        return keg
    return None

def record_drink(fob_id, tap, volume, timestamp):
    if volume <= 0:
        return
    fob = get_fob(fob_id)
    if fob is None or fob['drinker_id'] is None:
        print "An unknown fob ({0}) managed to get {1} ml of beer from tap {2}.".format(fob_id, volume, tap)
        return
    drinker_id = fob['drinker_id']
    drinker = get_drinker(drinker_id)
    if drinker is None:
        print "An unknown drinker ({0}) managed to get {1} ml of beer from tap {2}.".format(drinker_id, volume, tap)
        return
    keg = get_current_keg(tap)
    cost = price(Decimal(volume) * Decimal(keg['cost']) / Decimal(keg['volume']))
    alcohol = Decimal(volume) * Decimal(keg['abv'])
    drink = Item(drinks, data={
            'drinker_id': str(drinker_id),
            'timestamp': str(timestamp),
            'volume': str(volume),
            'tap': str(tap),
            'cost': str(cost),
            'alcohol': str(alcohol),
            'payer_id': str(drinker['payer_id']),
            'beer_name': str(keg['beer_name'])
            })
    drink.save()
    payer = get_payer(drinker['payer_id'])
    payer['credit'] = str(Decimal(payer['credit']) - Decimal(cost))
    payer.save()
    drinker['number_of_drinks'] = str(Decimal(drinker['number_of_drinks']) + 1)
    drinker['volume_consumed'] = str(Decimal(drinker['volume_consumed']) + Decimal(volume))
    drinker['alcohol_consumed'] = str(Decimal(drinker['alcohol_consumed']) + Decimal(alcohol))
    drinker['total_cost'] = str(Decimal(drinker['total_cost']) + Decimal(cost))
    drinker.save()
    keg['volume_remaining'] = str(Decimal(keg['volume_remaining']) - Decimal(volume))
    keg.save()

def record_drinks(fob_id, tap_one_amount, tap_two_amount):
    timestamp = long(time.time())
    record_drink(fob_id, 1, tap_one_amount, timestamp)
    record_drink(fob_id, 2, tap_two_amount, timestamp+1)

def get_amount_allowed(fob_id):
    drinker = get_drinker_from_fob(fob_id)
    if not drinker:
        return 0
    return get_amount_allowed_for_drinker(drinker['drinker_id'])

def get_amount_allowed_for_fob(fob_id):
    return get_amount_allowed(fob_id)

def get_amount_allowed_for_drinker(drinker_id):
    drinker = get_drinker(drinker_id)
    if not drinker:
        return 0
    payer = get_payer(drinker['payer_id'])
    if Decimal(payer['credit']) > 0:
        return 500 # A bit more than a pint
        # it's possible that this'll send them over the amount they've paid for, but if so, they'll just be locked out from their next drink, and it's easier than calculating exactly how much they could afford as the two taps might cost different amounts.
    return 0

def register_drinker(drinker_id):
    drinker = drinkers.get_item(drinker_id=drinker_id)
    drinker = get_drinker(drinker_id)
    drinker.save()
    return True

def register_fob(fob_id, drinker_id):
    drinker = get_drinker(drinker_id)
    if not drinker:
        return False
    fob = get_fob(fob_id)
    if not fob:
        fob = Item(fobs, data={
                'fob_id': str(fob_id),
                'drinker_id': str(drinker_id)
                })
    fob['drinker_id'] = (drinker_id)
    fob['fob_id'] = str(fob_id)
    fob.save()
    return True

def add_credit_to_payer(payer_id, amount):
    payer = get_payer(payer_id)
    payer['credit'] = price(Decimal(payer['credit']) + Decimal(amount))
    payer.save()

def add_credit_to_drinker(drinker_id, amount):
    drinker = get_drinker(drinker_id)
    add_credit_to_payer(drinker['payer_id'], amount)
    drinker.save()
    
def remove_current_keg(tap):
    current_keg = get_current_keg(tap)
    if current_keg:
        current_keg.delete()
        current_keg['finish_timestamp'] = str(long(time.time()))
        current_keg.save(overwrite=True)

def add_new_keg(tap, cost, volume, abv, beer_name):
    remove_current_keg(tap)
    new_keg = Item(kegs, data={
                'tap': str(tap),
                'start_timestamp': str(long(time.time())),
                'finish_timestamp': str(-1),
                'cost': str(cost),
                'volume': str(volume),
                'abv': str(abv),
                'beer_name': str(beer_name),
                'volume_remaining': str(volume)
                })
    new_keg.save()
