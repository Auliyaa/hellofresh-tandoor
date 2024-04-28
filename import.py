import requests
import sys
import xml.etree.ElementTree as ET
import re
from html import escape, unescape
import json
import zipfile
import shutil
import os
import datetime

# ========================================
# HTTP GET
# sample page: https://www.hellofresh.fr/recipes/kottbullar-boulettes-a-la-suedoise-and-linguine-64fb2d1371b62ce128342048
# ========================================
rsp = requests.get(sys.argv[1])
data = rsp.text
data = re.sub("\\&\\w+\\;", lambda x: escape(unescape(x.group(0))), data)
data = re.sub("\\s\\&\\s", " et ", data)
root = ET.fromstring(data)

if rsp.status_code != 200:
    print("failed to fetch url")
    sys.exit(1)

# ========================================
# output json data: import format for TandoorRecipes
# ========================================
out = dict()
out["steps"] = []
out["description"] = None
out["keywords"] = []
out["waiting_time"] = 0
out["internal"] = True
out["nutrition"] = None
out["servings"] = 1
out["servings_text"] = ""
out["source_url"] = None

# ========================================
# find recipe title
# ========================================
recipe_title = root.find(".//h1").text
out["name"] = recipe_title

# ========================================
# find recipe time
# ========================================
# TODO
out["working_time"] = 35

# ========================================
# parse ingredients
# ========================================
out["steps"].append(dict())

# first step is always for recipe ingredients
out["steps"][0]["name"] = "Préparer les ingrédients"
out["steps"][0]["instruction"] = ""
out["steps"][0]["ingredients"] = []
out["steps"][0]["time"] = 0
out["steps"][0]["order"] = 0
out["steps"][0]["show_as_header"] = False
out["steps"][0]["show_ingredients_table"] = False

ingredients_shipped = root.findall(".//*[@data-test-id='ingredient-item-shipped']")
ingredients_not_shipped = root.findall(".//*[@data-test-id='ingredient-item-not-shipped']")
order=0
for i in ingredients_shipped + ingredients_not_shipped:
    i_out = dict()

    q_txt = i.find(".//p[@class='sc-9394dad-0 cJeggo']").text
    q_num = 0
    q_type = ''
    if q_txt == 'selon le goût':
        q_num = 1
        q_type = "mémo"
    else:
        q_num = float(q_txt.split(' ')[0]
                 .replace("⅓", "0.33")
                 .replace("⅔", "0.66")
                 .replace("⅓", "0.33")
                 .replace("¼","0.25")
                 .replace("½", "0.5")
                 .replace("¾", "0.75"))
        q_type = ' '.join(q_txt.split(' ')[1:])

    i_out["unit"] = dict()
    i_out["unit"]["name"] = q_type
    i_out["unit"]["plural_name"] = q_type
    i_out["unit"]["description"] = None

    i_out["amount"] = q_num
    i_out["note"] = ""
    i_out["order"] = order
    order = order+1
    i_out["is_header"] = False
    i_out["always_use_plural_unit"] = False
    i_out["always_use_plural_food"] = False

    name = i.find(".//p[@class='sc-9394dad-0 eERBYk']").text
    i_out["food"] = dict()
    i_out["food"]["name"] = name
    i_out["food"]["plural_name"] = None
    i_out["food"]["ignore_shopping"] = False
    i_out["food"]["supermarket_category"] = None

    out["steps"][0]["ingredients"].append(i_out)

# ========================================
# parse steps/instructions
# ========================================


def render_txt(xml):
    res = ""
    for sub in xml.iter():
        if sub.tag == 'p':
            res += "\n%s\n" % sub.text
            continue
        if sub.tag == 'li':
            if sub.text is None:
                res += "- %s\n" % sub.find('.//span').text
            else:
                res += "- %s\n" % sub.text
            continue
    return res


instructions_root = root.find(".//*[@data-test-id='instructions']")
steps = instructions_root.findall(".//span[@type='body-xl-regular'].........")
for step in steps:
    step_num = int(step.find(".//span[@type='body-xl-regular']").text)
    txt_root = step.find(".//span[@type='body-md-regular']")
    # need to render contents of txt_root here, may contains <ul> as well as raw text
    step_txt = render_txt(txt_root)

    step_out = dict()
    step_out["name"] = "Etape %s" % str(step_num)
    step_out["instruction"] = step_txt
    step_out["ingredients"] = []
    step_out["time"] = 0
    step_out["order"] = step_num
    step_out["show_as_header"] = False
    step_out["show_ingredients_table"] = True

    out["steps"].append(step_out)


# ========================================
# fetch image
# ========================================
img_root = instructions_root = root.find(".//*[@data-test-id='recipe-hero-image']")
img_src = img_root.find(".//img").attrib["src"]

img_rsp = requests.get(img_src, stream=True)

# ========================================
# create files
# ========================================
with open("recipe.json", "w") as fd_recipe_json:
    fd_recipe_json.write(json.dumps(out, ensure_ascii=False))

with open("image.jpg", "wb") as fd_image_jpg:
    shutil.copyfileobj(img_rsp.raw, fd_image_jpg)

with zipfile.ZipFile("42.zip", mode="w") as archive:
    archive.write("recipe.json")
    archive.write("image.jpg")

today = datetime.datetime.now()
with zipfile.ZipFile("export_%s-%02d-%02d.zip" % (str(today.year), today.month, today.day), mode="w") as archive:
    archive.write("42.zip")

os.remove("recipe.json")
os.remove("image.jpg")
os.remove("42.zip")
