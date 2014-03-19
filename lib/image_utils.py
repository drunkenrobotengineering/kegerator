#!/usr/bin/python

import os, sys
import Tkinter
from Tkinter import *
import Image, ImageTk
import tkFont

def get_dimensions(image, max_width, max_height):
    original_width = image.size[0]
    original_height = image.size[1]
    max_ratio = (1.0*max_width)/(1.0*max_height)
    original_ratio = (1.0*original_width)/(1.0*original_height)
    if (original_ratio > max_ratio):
        # width is the limiting dimension
        # resize so the width is at the max
        scale_down = (1.0*max_width)/(1.0*original_width)
        return original_width * scale_down, original_height*scale_down
    else:
        # height is the limiting dimension (or it's exactly the right ratio)
        # resize so the height is at the max
        scale_down = (1.0*max_height)/(1.0*original_height)
        return original_width * scale_down, original_height*scale_down

def get_resized_image(image, max_width, max_height, enlarge=True):
    width, height = get_dimensions(image, max_width, max_height)
    print "width = " + str(width)
    print "height = " + str(height)
    if (not enlarge and max_width > image.size[0]):
        return image
    width = int(width)
    height = int(height)
    return image.resize((width, height), Image.ANTIALIAS)
