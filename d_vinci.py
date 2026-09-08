import json, sqlite3, time
import requests, yaml
from datetime import datetime
from pathlib import Path

job_db = Path("jobs.db").resolve()
j_conn = sqlite3.connect(job_db)

firma = "generali-gruppe"
url = f"https://{firma}.dvinci-hr.com/jobPublication/list.json"
generali_glob_id = "048574e2-40c8-4f96-9a98-6cd13f8d705e"
r = requests.get(
        url,
        params={
            "language": "de", 
            "widget-version": "v2",
            "stellenliste": "true",
            "stellenlisteGlobalId": generali_glob_id
            }, timeout=30
                 )
if r.status_code != 200:
    print(f"{firma}: HTTP {r.status_code}")

stellen = r.json()
now = datetime.now().isoformat(timespec="seconds")
source = "generali"
print(len(stellen))

for stelle in stellen:
    #soup = BeautifulSoup(stelle, "html.parser")
    refnr = firma + stelle["id"]
    job_title = stelle["position"])
                  refnr,
                  now,
                  source,
                  job_title,
                  firma,
                  plz,
                  seit,
                  json.dumps(it, ensure_ascii=False))).rowcount
    print(stelle["position"])
    for info in stelle:
        print(info)


j_conn.close()

