import sqlite3, json, yaml
from pathlib import Path
from openai import OpenAI

job_db = Path("jobs.db").resolve()
l_conn = sqlite3.connect("levels.db")

# jobs aus jobs getten, wo in einstufung für refnr 
l_conn.execute("ATTACH DATABASE ? AS jobdb", (str(job_db),))
jobs = l_conn.execute("""
    SELECT 
        j.job_title
    FROM jobdb.jobs AS j
    JOIN einstufung AS e
      ON j.refnr = e.refnr
    WHERE e.level = "Gar nicht"
    ORDER BY e.check_id ASC
               """).fetchall()

l_conn.close()
for job in jobs:
    print(job)

print(len(jobs))
