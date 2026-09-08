"""Holt alles und legt das rohe JSON in SQLite. Gefiltert wird in filter.py."""
import base64, json, sqlite3, time
from datetime import datetime
import requests, urllib3, yaml

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service"
HEADERS = {"X-API-Key": "jobboerse-jobsuche",
           "User-Agent": "Jobsuche/2.9.2 (de.arbeitsagentur.jobboerse; build:1077; iOS 15.1.0) Alamofire/5.4.4"}

voll = yaml.safe_load(open("config.yaml", encoding="utf-8"))
cfg = voll["abruf"]
db = sqlite3.connect(voll["db"])
db.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
    refnr TEXT PRIMARY KEY,
    first_seen TEXT,
    source TEXT,
    job_title TEXT,
    seit DATE,
    plz NUMBER,
    raw TEXT,
    details TEXT)
    """)

def get(url, params=None, versuch=1):
    r = requests.get(url, headers=HEADERS, params=params, timeout=30, verify=False)
    if r.status_code == 403 and versuch <= 3:
        print(f"  403, warte {30 * versuch}s")
        time.sleep(30 * versuch)
        return get(url, params, versuch + 1)
    if r.status_code != 200:
        print(f"  HTTP {r.status_code}")
        return None
    return r.json()

def suche(was, wo, umkreis):
    q = {"suchbereich": "jobs", "pav": "false", "as": "true", "facetten": "false",
         "veroeffentlichtseit": cfg["veroeffentlichtseit"], "size": cfg["size"]}
    if was: q["was"] = was
    if wo:  q["wo"], q["umkreis"] = wo, umkreis
    for page in range(1, cfg["max_pages"] + 1):
        items = (get(f"{BASE}/pc/v6/jobs", {**q, "page": page}) or {}).get("ergebnisliste") or []
        yield from items
        if len(items) < cfg["size"]: return
        time.sleep(cfg["sleep"])

now = datetime.now().isoformat(timespec="seconds")
source = "agentur fuer arbeit"
orte = list((cfg["staedte"] or {}).items()) or [(None, None)]

for was in cfg["suchbegriffe"] or [None]:
    for wo, km in orte:
        n = neu = 0
        for it in suche(was, wo, km):
            refnr = it.get("referenznummer")
            job_title = it.get("stellenangebotsTitel")
            seit = it.get("datumErsteVeroeffentlichung")
            if not refnr: continue
            if job_title is None: continue
            if any(b in job_title.lower() for b in cfg["nichtBeruf"]):
                print(f"{job_title} skipped!")
                continue
            print(seit)
            plz = it.get("plz")
            n += 1
            neu += db.execute("INSERT OR IGNORE INTO jobs (refnr, first_seen, source, job_title, seit, plz, raw) VALUES (?,?,?,?,?,?,?)",
                              (
                                  refnr,
                                  now,
                                  source,
                                  job_title,
                                  seit,
                                  plz,
                                  json.dumps(it, ensure_ascii=False))).rowcount
        db.commit()
        print(f"{was or '*'} @ {wo or '*'}: {n} Treffer, {neu} neu")
        time.sleep(cfg["sleep"])

if cfg["details"]:
    offen = [r[0] for r in db.execute(
        "SELECT refnr FROM jobs WHERE details IS NULL LIMIT ?", (cfg["details_limit"],))]
    print(f"Details fuer {len(offen)} Stellen")
    for i, refnr in enumerate(offen, 1):
        d = get(f"{BASE}/pc/v4/jobdetails/{base64.b64encode(refnr.encode()).decode()}")
        db.execute("UPDATE jobs SET details=? WHERE refnr=?",
                   (d.get("stellenangebotsBeschreibung"), refnr))
        if i % 25 == 0: db.commit(); print(f"  {i}/{len(offen)}")
        time.sleep(cfg["sleep"])
    db.commit()

print("gesamt in db:", db.execute("SELECT count(*) FROM jobs").fetchone()[0])
db.close()
