from serpapi import GoogleSearch
import sys

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

search = GoogleSearch({
    "q": "hellofresh.fr %s" % sys.argv[1],
    "location": "Toulouse,France",
    "hl": "fr",
    "gl": "fr",
    "api_key": "adbbe545426c885d4310b808b6ef526b34b26555c6fecb77358b5294bcfe9c41"
  })

print(search.get_dict())