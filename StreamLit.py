import cv2
import csv
import numpy as np
import tkinter as tk
from tkinter import filedialog
from tkinter import *
import pandas as pd
import urllib.request
import json
import requests
import webbrowser
import ssl
from PIL import Image, ImageFont, ImageDraw, ImageTk, ImageOps, ImageColor
import streamlit as st

#Title of the app
st.title("Deft Tool")
st.sidebar.title("Shape Settings")

template = cv2.imread('TEMP.png')

df = pd.read_csv('products_export.csv')
collums = df[["Title","Variant Price","Image Src","Variant Compare At Price"]]
saved = collums.to_csv("newdata1.csv")
Prices = df["Variant Price"]
Compare_at = df["Variant Compare At Price"]

#creates New csv just for link downloading
links = df["Image Src"]
links_saved  = links.to_csv("links.csv")

#dowloads images
ssl._create_default_https_context = ssl._create_unverified_context
def url_to_jpg(i, url, file_path):
    filename = '{}.jpg'.format(i)
    full_path = '{}{}'.format(file_path, filename)
    urllib.request.urlretrieve(url, full_path)
    print('{} saved.'.format(filename))
    return None

FILENAME = 'links.csv'
FILE_PATH = ''
urls = pd.read_csv(FILENAME)
for i, url in enumerate(urls.values):
    url_to_jpg(i, url[1], FILE_PATH)

img = template
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

sensitivity = 15
lower_white = np.array([0,0,255-sensitivity])
upper_white = np.array([255,sensitivity,255])
mask = cv2.inRange(hsv, lower_white, upper_white)

contours,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

largestshape = []
largestarea = 0
for cnt in contours:
    epsilon = 0.01*cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, epsilon, True)
    #img = cv2.drawContours(img, [approx], 0, (0, 255, 0), 3)
    area = cv2.contourArea(cnt)
    if largestarea < area:
        largestarea = area
        largestshape = approx
        #img = cv2.drawContours(img, [approx], 0, (0, 255, 0), 3)

top_left = largestshape[0][0]
bot_left = largestshape[1][0]
bot_right = largestshape[2][0]
top_right = largestshape[3][0]
width = top_right[0]-top_left[0]
height = bot_left[1]-top_left[1]

for i in range(len(links)):
    puma = cv2.imread(str(i) + ".jpg")
    if (max(width, height)%min(width, height)) < 7 or width == height:
        pumaresized = cv2.resize(puma,(width, height))
        img[top_left[1]:bot_right[1], top_left[0]:bot_right[0]] = pumaresized

    else:
        product_width = puma.shape[1]
        product_height = puma.shape[0]
        ratio = width/product_width
        product_width = product_width*ratio
        product_height = product_height*ratio
        puma = cv2.resize(puma, (int(product_width), int(product_height)))
        total_height_crop = product_height-height
        half_height_crop = total_height_crop/2
        bot_minus_half_crop = int(product_height - half_height_crop)
        puma = puma[int(half_height_crop):int(bot_minus_half_crop), 0:int(product_width)]
        img[top_left[1]:bot_left[1], top_left[0]:bot_right[0]] = puma

    cv2.imwrite(str(i) + ".jpg", img)

height_template = template.shape[0]
width_template = template.shape[1]

shape = st.sidebar.selectbox("Price Text Shape:", ["Circle", "Rectangle"])
shape_color = st.sidebar.color_picker("Pick Shape Colour")
shape_color = ImageColor.getrgb(shape_color)
x_axis = st.sidebar.slider("x co-ordinate: ", 0, int(width_template))
y_axis = st.sidebar.slider("y co-ordinate: ", 0, int(height_template))

radius=0
if shape == "Circle":
    radius = st.sidebar.slider("Radius :", 0, 1000)
    template = cv2.circle(template, (x_axis, height_template-y_axis), radius, (shape_color), cv2.FILLED)

width = 0
height = 0
if shape == "Rectangle":
    width = st.sidebar.slider("Width :", 0, 1000)
    height = st.sidebar.slider("Height :", 0, 1000)
    template = cv2.rectangle(template, (x_axis, height_template-y_axis), ((x_axis+width),((height_template-y_axis)+height)), (shape_color, cv2.FILLED)

st.sidebar.title("Font Settings")

font_select = st.sidebar.selectbox("Select Font :", ['Bold', 'Regular'])
font_color = st.sidebar.color_picker("Pick Font Colour")

st.sidebar.header("Font without Compare")
font_size = st.sidebar.slider("Font Size: ", 0, 500)
x_axis_font = st.sidebar.slider("x co-ordinate font: ", 0, int(width_template))
y_axis_font = st.sidebar.slider("y co-ordinate font: ", 0, int(height_template))
font = ImageFont.truetype(font_select.upper() + '.ttf', size=font_size)

st.sidebar.header("Font with Compare")
font_size_compare = st.sidebar.slider("Font Compare Size: ", 0, 500)
x_axis_font_compare = st.sidebar.slider("x co-ordinate compare font: ", 0, int(width_template))
y_axis_font_compare = st.sidebar.slider("y co-ordinate compare font: ", 0, int(height_template))
line_color = st.sidebar.color_picker("Pick Line Colour")
line_width = st.sidebar.slider("Compare Price Line Width", 0, width_template)
line_thickness = st.sidebar.slider("Compare Price Line Thickness", 0, 50)
line_x = st.sidebar.slider("Line x:", 0, width_template)
line_y = st.sidebar.slider("Line y:", 0, height_template)

font_compare = ImageFont.truetype(font_select.upper() + '.ttf', size=font_size_compare)

cv2.imwrite("Design.jpg", template)
im = Image.open("Design.jpg").convert("RGB")
d = ImageDraw.Draw(im)

d.multiline_text((x_axis_font, height_template-y_axis_font), "£99.99", font=font, fill=font_color, spacing=10, align='center')
d.multiline_text((x_axis_font_compare, height_template-y_axis_font_compare), """£89.99\n£99.99""", font=font_compare, fill=font_color, spacing=10, align='center')
d.line(((line_x, height_template-line_y), (line_x+line_width, height_template-line_y)), fill=line_color, width=line_thickness)

im.save("NewDesign.jpg")
st.image(im, use_column_width=True, clamp=True)

finished_edit = st.sidebar.button("PRESS TO EDIT PHOTOS")

if finished_edit:
    for i in range(len(links)):
        if radius > 0:
            image_circle = cv2.imread(str(i)+".jpg")
            image_circle = cv2.circle(image_circle, (x_axis, height_template - y_axis), radius, (shape_color), cv2.FILLED)
            cv2.imwrite(str(i) + ".jpg", image_circle)
        if width > 0 or height > 0:
            image_rectangle = cv2.imread(str(i) + ".jpg")
            image_rectangle = cv2.rectangle(image_rectangle, (x_axis, height_template - y_axis),((x_axis + width), ((height_template - y_axis) + height)), (shape_color),cv2.FILLED)
            cv2.imwrite(str(i) + ".jpg", image_rectangle)

        im = Image.open(str(i) + ".jpg")
        d = ImageDraw.Draw(im)

        if (len(str(Prices[i]))) == 4:
            priceimage = "£" + str(Prices[i]) + "0"
        else:
            priceimage = "£" + str(Prices[i])

        if "." in str(Compare_at[i]):
            if (len(str(Compare_at[i]))) == 4:
                Compare_at_Price = ("£" + str(Compare_at[i]) + "0")
            both_price = priceimage + "\n" + Compare_at_Price
            d.multiline_text((x_axis_font_compare, height_template - y_axis_font_compare), both_price,font=font_compare, fill=font_color, spacing=10, align='center')
            d.line(((line_x, height_template - line_y), (line_x + line_width, height_template - line_y)),fill=line_color, width=line_thickness)
            im.save(str(i) + ".jpg")
        else:
            d.multiline_text((x_axis_font, height_template-y_axis_font), priceimage, font=font, fill=font_color, spacing=10, align='center')
            im.save(str(i) + ".jpg")

        img = Image.open(str(i) + ".jpg")
        location = Image.open(str(i) + ".jpg")
        d = ImageDraw.Draw(im)