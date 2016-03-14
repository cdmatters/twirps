from __future__ import unicode_literals
import json
import logging
import os


from flask import Blueprint, Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, Response

from twirps import app, data_collection

from twirps.classes import TDBHandler, NeoDBHandler, PgDBHandler
from decorators import requires_auth

LOGGER = logging.getLogger(__name__)

def initialise_databases():
    pass

def destroy_databases():
    pass

def start_streamer():
    pass

def stop_streamer():
    pass

def start_bulk_historical_collection():
    pass

def stop_bulk_historical_collection():
    pass

def load_passive_twirps_to_database_by_handle():
    pass

def load_active_twirps_to_database_by_handle():
    pass

def load_mp_twirps_to_database():
    pass

def start_bulk_recent_collection():
    pass

def storp_bulk_recent_collection():
    pass

def delete_data():
    pass

def initialise_postgres_db():
    pass

def drop_postgres_db():
    pass

def initialise_neo_db():
    pass

def drop_neo_db():
    pass

def sync_subscribers_from_twitter():
    pass

def sync_subcribers_to_twitter():
    pass



