import sqlite3, json, yaml
from pathlib import Path

job_db = Path("jobs.db").resolve()
try:
    with open(Path("running_applications.yaml"), "r") as f:
        running_applications = yaml.safe_load(f)
    j_conn = sqlite3.connect(job_db)

    for a_job in running_applications:
        if a_job["bewerbung"] == "beworben":
            print(f'updating bewerbungstatus to {a_job["bewerbung"]}')
            j_conn.execute('UPDATE jobs SET bewerbung="beworben" WHERE refnr=?',
                   (a_job["refnr"],))

    j_conn.commit()
    j_conn.close()
except FileNotFoundError:
    pass
l_conn = sqlite3.connect("levels.db")

# jobs aus jobs getten, wo in einstufung für refnr 
l_conn.execute("ATTACH DATABASE ? AS jobdb", (str(job_db),))
l_conn.row_factory = sqlite3.Row
jobs = l_conn.execute("""
    SELECT 
        j.job_title,
        j.bewerbung,
        e.level,
        j.fit,
        j.firma,
        j.plz,
        j.refnr,
        j.anschreiben,
        j.fragen,
        j.lacking,
        j.strengths,
        j.details
    FROM jobdb.jobs AS j
    JOIN einstufung AS e
      ON j.refnr = e.refnr
    WHERE 
        j.bewerbung="gereadet"
    ORDER BY e.check_id ASC
               """).fetchall()
l_conn.close()

row_list = [dict(row) for row in jobs]

with open("running_applications.yaml", "w", encoding="utf-8") as f:
    yaml.safe_dump(row_list, f, allow_unicode=True, sort_keys=False)
print(len(jobs))
