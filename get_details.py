import sqlite3, base64, time
from collect_positions import get, cfg, BASE
j_conn = sqlite3.connect("jobs.db")
offen = j_conn.execute("SELECT refnr FROM jobs WHERE details IS NULL ORDER BY seit DESC").fetchall()
print(f"Details fuer {len(offen)} Stellen")
for i, refnr in enumerate(offen, 1):
    refnr = refnr[0]
    refnr = base64.b64encode(refnr.encode()).decode()
    d = get(f"{BASE}/pc/v4/jobdetails/{refnr}")
    if d is not None:
        j_conn.execute("UPDATE jobs SET details=? WHERE refnr=?",
                   (d.get("stellenangebotsBeschreibung"), refnr))
    if i % 10 == 0: j_conn.commit(); print(f"  {i}/{len(offen)}")
    time.sleep(cfg["sleep"])
j_conn.commit()

print("details in j_conn:", j_conn.execute("SELECT count(*) FROM jobs WHERE details IS NOT NULL").fetchone()[0])
j_conn.close()
