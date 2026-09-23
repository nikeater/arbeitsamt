import sqlite3, base64, time, yaml
from collect_positions import get, cfg, BASE

voll = yaml.safe_load(open("config.yaml", encoding="utf-8"))
j_conn = sqlite3.connect(voll['JobDb'])
offen = j_conn.execute("SELECT refnr FROM jobs WHERE details IS NULL ORDER BY seit DESC").fetchall()
print(f"Details fuer {len(offen)} Stellen")
for i, refnr in enumerate(offen, 1):
    refnr = refnr[0]
    d = get(f"{BASE}/pc/v4/jobdetails/{base64.b64encode(refnr.encode()).decode()}")
    if d is not None:
        j_conn.execute("UPDATE jobs SET details=? WHERE refnr=?",
                   (d.get("stellenangebotsBeschreibung"), refnr))
    else:
        print("no details found")
        j_conn.execute(f'UPDATE jobs SET details="empty" WHERE refnr=?', (refnr,))
    if i % 5 == 0: j_conn.commit(); print(f"  {i}/{len(offen)}")
    time.sleep(cfg["sleep"])
j_conn.commit()

print("details in j_conn:", j_conn.execute("SELECT count(*) FROM jobs WHERE details IS NOT NULL").fetchone()[0])
j_conn.close()
