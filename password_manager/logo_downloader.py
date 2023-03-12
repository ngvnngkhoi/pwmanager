import requests
import os
query = "dog"

url = "https://www.google.com/search?q=" + query + "&source=lnms&tbm=isch"

response = requests.get(url)

#get current directory
path = os.path.dirname(os.path.realpath(__file__))

#make a directory named query
path = os.mkdir(path + "/" + query)

with open(path,"wbg ") as f:
    f.write(response.text)







# Path: logo_downloader.py
# Compare this snippet from test.py:


