import sqlite3, json, yaml
from pathlib import Path
from openai import OpenAI

job_db = Path("jobs.db").resolve()
l_conn = sqlite3.connect("levels.db")

# jobs aus jobs getten, wo in einstufung für refnr 
l_conn.execute("ATTACH DATABASE ? AS jobdb", (str(job_db),))
l_conn.execute("""
    CREATE TABLE IF NOT EXISTS einstufung (
    check_id INTEGER PRIMARY KEY,
    refnr TEXT,
    level TEXT,
    reason TEXT,
    prompt TEXT,
    model TEXT)
    """)
l_conn.commit()
jobs = l_conn.execute("""
SELECT j.refnr, j.job_title, j.details FROM jobdb.jobs j
WHERE NOT EXISTS (
               SELECT 1 FROM main.einstufung e 
               WHERE e.refnr = j.refnr
               )
ORDER BY j.seit DESC
               """).fetchall()


with open(Path.home() / ".config/io.datasette.llm/keys.json", "r") as f:
    keys = json.load(f)
with open(Path.home() / "Documents/Bewerbungen/cv_deutsch.yaml", "r") as f:
    cv = yaml.safe_load(f)
voll = yaml.safe_load(open("config.yaml", encoding="utf-8"))
client = OpenAI(
        base_url=voll["LlmAdress"],
        api_key=keys["llamaserver"],
        )

for job in jobs:
    frage = f'''Wie gut ist diese Stelle mit folgender Beschreibung:
{job[2]}
...für einen Kandidaten mit folgendem CV geeignet:
{cv}
Der Kandidat ist bereit umzuziehen'''
    anweisung = '''
    Gib die Antwort als Json:
    {
        "reason": ""
        "level": "",
    }
    Überlege, wie gut die Stelle sich für eine Bewerbung durch den Kandidaten eignet. Fülle die kurze Überlegung in reason ein.
    Fülle in level ein, zu welchem Ergebnis du gekommen bist. Nutze ausschließlich folgende Werte: "Gar nicht", "Eher nicht", "Vielleicht", "Interessant" oder "Perfekt".
        '''
    prompt = frage + anweisung
    response = client.chat.completions.create(
        model="local-model",  # name doesn't matter much, server ignores it usually
        messages=[
            {"role": "system", "content": "Du bist ein deutscher Karriereberater"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=3096,
    )
    max_id = l_conn.execute("SELECT MAX(check_id) FROM einstufung").fetchone()[0]
    if max_id is None:
        check_id = 1
    else:
        check_id = max_id + 1
    antwort = json.loads(response.choices[0].message.content)
    level = antwort["level"]
    reason = antwort["reason"]
    model = response.model
    print(f"{job[1]} ({job[0]}): {level}, {reason}")
    l_conn.execute("""
    INSERT OR IGNORE INTO einstufung(
    check_id, refnr, level, reason, prompt, model
    ) VALUES (?,?,?,?,?,?)
               """,
                   (
                       check_id,
                       job[0],
                       level,
                       reason,
                       prompt,
                       model,
                       ))
    l_conn.commit()
l_conn.close()
