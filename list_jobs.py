import sqlite3, json, yaml
from pathlib import Path

job_db = Path("jobs.db").resolve()
try:
    with open(Path("applicable_jobs.yaml"), "r") as f:
        applicable_jobs = yaml.safe_load(f)
    j_conn = sqlite3.connect(job_db)

    for a_job in applicable_jobs:
        if a_job["bewerbung"] is None:
            continue
        else:
            print(f'updating bewerbungstatus to {a_job["bewerbung"]}')
        j_conn.execute("UPDATE jobs SET bewerbung=? WHERE refnr=?",
               (a_job["bewerbung"], a_job["refnr"])
                       )
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
        e.check_id,
        e.level,
        j.bewerbung,
        j.job_title,
        j.plz,
        j.refnr,
        j.details
    FROM jobdb.jobs AS j
    JOIN einstufung AS e
      ON j.refnr = e.refnr
    WHERE 
        e.level IN ('Vielleicht', 'Interessant', 'Perfekt') AND
        j.bewerbung IS NULL
    ORDER BY e.check_id ASC
               """).fetchall()
l_conn.close()

row_list = [dict(row) for row in jobs]

with open("applicable_jobs.yaml", "w", encoding="utf-8") as f:
    yaml.safe_dump(row_list, f, allow_unicode=True)
print(len(jobs))
