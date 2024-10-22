#!/usr/bin/python3

import requests
import sys
import json
from lxml import etree
from serpapi import GoogleSearch

url = None
# if sys.argv[1].startswith("http"):
#     url = sys.argv[1]
# else:
#     print(".. searching recipe")
#     search = GoogleSearch({
#         "q": "hellofresh.fr %s" % sys.argv[1],
#         "location": "Toulouse,France",
#         "hl": "fr",
#         "gl": "fr",
#         "api_key": "adbbe545426c885d4310b808b6ef526b34b26555c6fecb77358b5294bcfe9c41"
#       })
#
#     url = search.get_dict()["organic_results"][0]["link"]
#
# print(".. parsing recipe: %s" % url)
#
# # ========================================
# # HTTP GET
# # sample page: https://www.hellofresh.fr/recipes/kottbullar-boulettes-a-la-suedoise-and-linguine-64fb2d1371b62ce128342048
# # ========================================
# print(".. fetching XML document")
# rsp = requests.get(url)
# data = rsp.text
# # data = re.sub("\\&\\w+\\;", lambda x: escape(unescape(x.group(0))), data)
# # data = re.sub("\\s\\&\\s", " et ", data)
# # data = re.sub("<script[^>]*>.+@context.+<\\/script[^>]*>","",data)
# with open("data.xml", "w", encoding='utf-8') as data_xml:
#     data_xml.write(data)
#
# parser = etree.XMLParser(recover=True)
# root = etree.fromstring(data, parser)
#
# if rsp.status_code != 200:
#     print("failed to fetch url")
#     sys.exit(1)
#
# recipe_data = root.find(".//script[@id='schema-org']").text

recipe_data='{"@context":"http://schema.org/","@type":"Recipe","name":"La Végé : salade chèvre chaud  lardons veggie avec une farandole de crudités  de la pomme","author":"HelloFresh","image":"https://img.hellofresh.com/f_auto,fl_lossy,h_640,q_auto,w_1200/hellofresh_s3/image/HF_Y24_R212_W42_FR_QFR23455-1_Main_high-2a49b778.jpg","thumbnailUrl":"https://img.hellofresh.com/f_auto,fl_lossy,h_300,q_auto,w_450/hellofresh_s3/image/HF_Y24_R212_W42_FR_QFR23455-1_Main_high-2a49b778.jpg","description":"Déguster un classique, la salade au chèvre chaud, en version végétarienne tout en conservant le fumé et le croustillant caractéristique des lardons, c\'est possible ! Servez-la accompagnée de petits pains aux noix, de carottes, de pommes et de sucrine. Et aucun compromis sur le goût.","datePublished":"2024-03-04T15:18:42+00:00","totalTime":"PT20M","nutrition":{"@type":"NutritionInformation","calories":"739 kcal","fatContent":"50.8 g","saturatedFatContent":"14 g","carbohydrateContent":"46.2 g","sugarContent":"14.4 g","proteinContent":"23.2 g","fiberContent":null,"cholesterolContent":null,"sodiumContent":"2.87 g","servingSize":"400"},"recipeInstructions":[{"@type":"HowToStep","text":"\nVeillez à bien respecter les quantités indiquées à gauche pour préparer votre recette !\nPréchauffez le four à 210°C sur grill.\nCoupez les petits pains en deux dans l\'épaisseur.\nCoupez le chèvre en rondelles.\n"},{"@type":"HowToStep","text":"\nDisposez les pains sur une plaque recouverte de papier sulfurisé. Placez une rondelle de chèvre et une petite pincée de thym séché (selon votre goût) sur chaque moitié. \nEnfournez-les 8-10 min, ou jusqu\'à ce que le chèvre soit fondant.\nPendant ce temps, faites chauffer un filet d\'huile d\'olive dans une poêle à feu moyen-vif. Faites-y revenir ⅓ sachet de lardons végétaux par personne 4-6 min, ou jusqu\'à ce qu\'ils soient bien dorés.\n"},{"@type":"HowToStep","text":"\nFaites une vinaigrette en mélangeant, par personne : 1 cc de moutarde, 1 pincée de thym séché (selon votre goût), 1½ cs d\'huile d\'olive et 1 cs de vinaigre balsamique dans un saladier. Salez et poivrez.\nCoupez la sucrine en fines lanières.\nCoupez la pomme en quartiers et ôtez-en le trognon. Coupez les quartiers en dés.\nÉpluchez et râpez la carotte.\n\n L’ASTUCE DU CHEF : Il se peut que les premières feuilles de votre sucrine soient légèrement déshydratées ; pensez à les retirer avant de les consommer."},{"@type":"HowToStep","text":"\nJuste avant de servir, ajoutez la sucrine, la carotte et la pomme au saladier. Mélangez.\nDisposez la salade dans des assiettes creuses. Placez les lardons végétaux par-dessus (selon votre goût), puis les tartines de chèvre chaud.\nArrosez d’un filet d’huile d’olive et de vinaigre balsamique si vous le souhaitez (voir L\'ASTUCE). Pour un meilleur équilibre des saveurs, piochez un peu de chaque élément du plat à chaque bouchée.\n\nL\'ASTUCE DU CHEF : Si vous appréciez le mélange sucré-salé, vous pouvez aussi arroser le tout d’un filet de miel."}],"recipeIngredient":["2 pièce(s) Petit pain aux noix","1 pièce(s) Fromage de chèvre frais","½ sachet(s) Thym séché","2 pièce(s) Sucrine","1 pièce(s) Pomme","½ pièce(s) Carotte","⅔ paquet(s) Lardons végétaux","4 cs Huile d\'olive","2 cc Moutarde","2 cs Vinaigre balsamique noir","selon le goût Poivre et sel"],"recipeYield":2,"keywords":["Moins de CO2","Végétarien","SEO"],"recipeCategory":"Plat principal","recipeCuisine":"Française"}'
j = json.loads(recipe_data,strict=False)

print(".. preparing JSON data")
out = dict()

out["steps"] = []
out["description"] = None
out["keywords"] = []
out["waiting_time"] = 0
out["internal"] = True
out["nutrition"] = None
out["servings"] = 1
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

