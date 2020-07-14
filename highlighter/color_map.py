#! /usr/bin/python
"""
Originally from:
@author: (c) 2017, Jorj X. McKie
License: GNU GPL V3
PyMuPDF demo program to print the the database of stored RGB colors as a PDF
----------------------------------------------------------------------------
"""
from __future__ import print_function
import fitz, sys, os
from fitz.utils import getColor, getColorInfoList
import random

def print_color_map(color_map, output_file="color_map.pdf"):
    black = getColor("black")    # text color
    white = getColor("white")    # text color
    fsize = 8                    # fontsize
    lheight = fsize *1.2         # line height
    idx = 0                      # index in color database
    doc = fitz.open()            # empty PDF
    w = 800                      # page width
    h = 600                      # page height
    rw = 80                      # width of color rect
    rh = 60                      # height of color rect
    n_rows = 10
    n_cols = 10

    sorted_label_names = sorted(list(color_map.keys()))
    color_map = dict(zip(sorted_label_names, mylist))
    num_colors = len(sorted_label_names)

    while idx < num_colors:
        page = doc.newPage(-1, width = w, height = h)  # new empty page
        for i in range(n_rows):                        # row index
            if idx >= num_colors:
                break
            for j in range(n_cols):                    # column index
                rect = fitz.Rect(rw*j, rh*i, rw*j + rw, rh*i + rh)  # color rect
                label = sorted_label_names[idx]# color name
                cname = color_map[label]
                col = getColor(cname)
                page.drawRect(rect, color = col, fill = col)   # draw color rect
                pnt1 = rect.top_left + (0, rh*0.3)   # pos of color name in white
                pnt2 = pnt1 + (0, lheight)           # pos of color name in black
                page.insertText(pnt1, labels[idx], fontsize = fsize, color = white)
                page.insertText(pnt2, labels[idx], fontsize = fsize, color = black)
                idx += 1
                if idx >= num_colors:
                    break

    doc.save(output_file, garbage = 4, deflate = True, clean=True)