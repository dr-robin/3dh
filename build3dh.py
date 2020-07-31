#!/usr/bin/env python
# coding: utf-8

# # 3D House code

# Imports

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import rasterio as rio
from rasterio.plot import show
import re
import requests
import json
import math
from shapely.geometry import *
from rasterio import mask
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
from rasterio.enums import Resampling
import sys
import boto3
import shutil
import plotly.graph_objects as go

# MAIN VARIABLES

client_type = 's3'
bucket_name = 'geotiffs3dhouse'

aws_client = boto3.client(client_type)
bucket_content = aws_client.list_objects(Bucket=bucket_name)


# file_searcher() takes an S3 Bucket, and a filetype (ex: .tif)


def file_searcher(bucket_content, file_type):
    file_names = []
    ext_list = []
    for item in bucket_content['Contents']:
        file_names.append(item['Key'])
    for file in file_names:
        if file[-4:] == file_type:
            ext_list.append(str(client_type + '://' + bucket_name + '/' +
                                file))
    return ext_list


# Address error and lookup
# address_lookup takes a string and requests it as a parameter from loc.geopunt.be
# which returns a dict containing the correct address notation

class AddressError(Exception):
    pass


def address_lookup(addr: str, debug=False):
    req = requests.get(
        f"http://loc.geopunt.be/geolocation/location?q={addr}&c=1", )
    ret_dict = {}
    if req.json()["LocationResult"] == []:
        raise AddressError(
            "That address couldn't be recognized, please try again with a different string."
        )
    for k, v in req.json()["LocationResult"][0].items():
        if debug:
            print(f"{k}: {v}")
        ret_dict[k] = [v]
    return ret_dict


# given an address dict, returns the polygon associated with the building on that location

## Hedia's polygon API
def hedi_api(address: dict, debug=False):
    street = address['Thoroughfarename'][0]
    nb = address['Housenumber'][0]
    pc = address['Zipcode'][0]
    city = address['Municipality'][0]
    if debug:
        print(street, nb, city, pc)
    req = requests.get(
        f"https://api.basisregisters.dev-vlaanderen.be/v1/adresmatch?gemeentenaam={city}&straatnaam={street}&huisnummer={nb}&postcode={pc}"
    ).json()
    objectId = req["adresMatches"][0]["adresseerbareObjecten"][0]["objectId"]

    req = requests.get(
        f"https://api.basisregisters.dev-vlaanderen.be/v1/gebouweenheden/{objectId}"
    ).json()
    objectId = req["gebouw"]["objectId"]

    req = requests.get(
        f"https://api.basisregisters.dev-vlaanderen.be/v1/gebouwen/{objectId}"
    ).json()
    poly_dict = [req["geometriePolygoon"]["polygon"]]
    polygon = Polygon(poly_dict[0]['coordinates'][0])
    if debug:
        print(polygon)
    return polygon


# Robin's fast_overlap() takes a list of paths to .tif files, and a polygon
# and finds the file in which this polygon is situated with minimal data reading


def fast_overlap(filelist, polygon):

    for filepath in filelist:
        # Open raster and check overlap
        with rio.open(filepath) as src:
            # src is raster, polygon is user address
            if not rio.coords.disjoint_bounds(src.bounds, polygon.bounds):
                if "DSM" in src.name:
                    dsmfile = src.name
                elif "DTM" in src.name:
                    dtmfile = src.name
    return [dsmfile, dtmfile]


# calculate_dem() makes a dem image from a masked dsm and dtm, where only the data needed is read out

def calculate_dem(tifs, polygon, address, upscale_factor=10):
    dsmpath = tifs[0]
    dtmpath = tifs[1]

    # Open DSM raster with mask of building shape
    with rio.open(dsmpath) as src:
        mask, out_transform, win = rio.mask.raster_geometry_mask(
            dataset=src, shapes=[polygon], invert=False, crop=True, pad=False)
        # Read only pixels within the window/bounds of the building shape
        dsm = src.read(1, window=win)

    # Open DTM raster with mask of building shape
    with rio.open(dtmpath) as src:
        mask, out_transform, win = rio.mask.raster_geometry_mask(
            dataset=src, shapes=[polygon], invert=False, crop=True, pad=False)
        # Read only pixels within the window/bounds of the building shape
        dtm = src.read(1, window=win)

    # Calculates raw digital elevation model
    dem = dsm - dtm

    # solves an issue where the buildings were mirrored for some reason,
    # not quite sure why, but this fixes it
    dem = dem.transpose()

    return plot_interactive(dem, address)


# plot_interactive() generates a .html file that gives the user an interactive 3d plot of the building


def plot_interactive(dem, address_dict, debug=False):
    address_str = address_dict['FormattedAddress'][0]

    # Plot xyz of building
    fig = go.Figure(data=[go.Surface(z=dem)])

    fig.update_layout(title=address_str,
                      autosize=False,
                      width=1000,
                      height=1000,
                      margin=dict(l=65, r=50, b=65, t=90))

    output_file = f"{address_str}.html"
    fig.write_html(os.path.join("templates/", output_file))
    return output_file


# searchf() is a high-level function to walk through a directory and return all files
# of a certain filetype

def searchf(fpath: str, file_type: str):
    total_files = []
    # Walk through the folder containing the data, and check if the files match the file type
    # If so; open that file, and print how many there were found
    for root, dirs, files in os.walk(fpath):
        for name in files:
            if name.endswith(file_type):
                total_files.append(name)
    return total_files

# clears the /templates/ folder, and makes it again, because otherwise the program complains

def reset_templates():
    shutil.rmtree('templates/')
    os.mkdir('templates/')

# house_plot() calls all of the above functions in the correct order 
# and returns the path where the .html file is stored

def house_plot(address_dict, debug=False):
    bucket_files = file_searcher(bucket_content, '.tif')
    poly = hedi_api(address_dict, debug)
    tiflist = fast_overlap(bucket_files, poly)
    output = calculate_dem(tiflist, poly, address_dict)
    return output

# main determines what action should be taken based on the user's input in the flask app
# if a certain address has been computed before, it'll open that .html instead of remaking it

def main(inp):
    address_dict = address_lookup(inp)
    address_name = address_dict['FormattedAddress'][0]
    template_list = searchf('templates/','.html')
    for temp in template_list:
        if address_name in temp:
            return temp
    return house_plot(address_dict)




