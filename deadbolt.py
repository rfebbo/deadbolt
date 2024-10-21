import numpy as np
from bs4 import BeautifulSoup
import requests
import regex as re
import json

from dli_heros import load_local_heros, download_hero_info
from dli_items import download_item_info
from hero import hero


heros = load_local_heros()
# download_hero_info()
download_item_info()

for h in heros:
    Abrams = hero(heros[h])
    print(f'{h} DPS:{Abrams.get_dps()}')



