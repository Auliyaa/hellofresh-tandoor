#!/usr/bin/python3

import requests
import sys
import os
import datetime
import json
import shutil
import zipfile
from lxml import etree
from serpapi import GoogleSearch

url = None
if sys.argv[1].startswith("http"):
    url = sys.argv[1]
else:
    print(".. searching recipe")
    search = GoogleSearch({
        "q": "hellofresh.fr %s" % sys.argv[1],
        "location": "Toulouse,France",
        "hl": "fr",
        "gl": "fr",
        "api_key": "adbbe545426c885d4310b808b6ef526b34b26555c6fecb77358b5294bcfe9c41"
      })

    url = search.get_dict()["organic_results"][0]["link"]

print(".. parsing recipe: %s" % url)

# ========================================
# HTTP GET
# sample page: https://www.hellofresh.fr/recipes/kottbullar-boulettes-a-la-suedoise-and-linguine-64fb2d1371b62ce128342048
# ========================================
print(".. fetching XML document")
rsp = requests.get(url)
data = rsp.text
# data = re.sub("\\&\\w+\\;", lambda x: escape(unescape(x.group(0))), data)
# data = re.sub("\\s\\&\\s", " et ", data)
# data = re.sub("<script[^>]*>.+@context.+<\\/script[^>]*>","",data)
with open("data.xml", "w", encoding='utf-8') as data_xml:
    data_xml.write(data)

parser = etree.XMLParser(recover=True)
root = etree.fromstring(data, parser)

if rsp.status_code != 200:
    print("failed to fetch url")
    sys.exit(1)

recipe_data = root.find(".//script[@id='schema-org']").text

j = json.loads(recipe_data,strict=False)
print(json.dumps(j,ensure_ascii=False))

print(".. preparing JSON data")
out = dict()
out["steps"] = []
out["description"] = None
out["keywords"] = []
out["waiting_time"] = 0
out["internal"] = True
out["nutrition"] = None
out["servings"] = j["recipeYield"]
out["servings_text"] = ""
out["source_url"] = url

print(".. fetching recipe title")
out["name"] = j["name"]
out["working_time"] = 0 # use j["totalTime"]

print(".. fetching ingredients")
out["steps"].append(dict())

# first step is always for recipe ingredients
out["steps"][0]["name"] = "Préparer les ingrédients"
out["steps"][0]["instruction"] = ""
out["steps"][0]["ingredients"] = []
out["steps"][0]["time"] = 0
out["steps"][0]["order"] = 0
out["steps"][0]["show_as_header"] = False
out["steps"][0]["show_ingredients_table"] = False

order = 0
for ingredient in j["recipeIngredient"]:
    ingredient_data = dict()
    ingredient_data["note"] = ""
    ingredient_data["order"] = order
    ingredient_data["is_header"] = False
    ingredient_data["always_use_plural_unit"] = False
    ingredient_data["always_use_plural_food"] = False

    ingredient_data["food"] = dict()
    ingredient_data["food"]["plural_name"] = None
    ingredient_data["food"]["ignore_shopping"] = False
    ingredient_data["food"]["supermarket_category"] = None
    ingredient_data["unit"]=dict()

    tokens = ingredient.split(" ")
    if ingredient.startswith("selon le goût"):
        ingredient_data["unit"]["name"] = "mémo"
        ingredient_data["amount"] = 1
        ingredient_data["food"]["name"] = " ".join(tokens[3:])
    else:
        ingredient_data["unit"]["name"] = tokens[1]
        ingredient_data["amount"] = float(tokens[0]
                     .replace("⅓", "0.33")
                     .replace("⅔", "0.66")
                     .replace("⅓", "0.33")
                     .replace("¼","0.25")
                     .replace("½", "0.5")
                     .replace("¾", "0.75"))
        ingredient_data["food"]["name"] = " ".join(tokens[2:])

    ingredient_data["unit"]["plural_name"] = ingredient_data["unit"]["name"]
    out["steps"][0]["ingredients"].append(ingredient_data)
    order = order + 1

print(".. fetching steps")

order = 1 # now used for step order
for instruction in j["recipeInstructions"]:
    txt = instruction["text"]
    if txt.startswith("\n"): txt.replace("\n", "", 1)
    step_out = dict()
    step_out["name"] = "Etape %s" % str(order)
    step_out["instruction"] = txt
    step_out["ingredients"] = []
    step_out["time"] = 0
    step_out["order"] = order
    step_out["show_as_header"] = False
    step_out["show_ingredients_table"] = True
    out["steps"].append(step_out)

print(".. fetching image")
img_rsp = requests.get(j["image"], stream=True)

print(".. generating output file")
print(json.dumps(out, ensure_ascii=False))
with open("recipe.json", "w", encoding="utf-8") as fd_recipe_json:
    fd_recipe_json.write(json.dumps(out, ensure_ascii=False))

with open("image.jpg", "wb") as fd_image_jpg:
    shutil.copyfileobj(img_rsp.raw, fd_image_jpg)

with zipfile.ZipFile("42.zip", mode="w") as archive:
    archive.write("recipe.json")
    archive.write("image.jpg")

today = datetime.datetime.now()
with zipfile.ZipFile("export_%s-%02d-%02d.zip" % (str(today.year), today.month, today.day), mode="w") as archive:
    archive.write("42.zip")

print(".. cleaning-up")
os.remove("recipe.json")
os.remove("image.jpg")
os.remove("42.zip")
os.remove("data.xml")
