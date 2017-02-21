import requests
import pyquery as pq

res = requests.get("http://r.qidian.com/recom")
if res.status_code == 200:
    temp_html = res.text
    obj = pq.PyQuery(temp_html)
    print(obj.text())