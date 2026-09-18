import sqlite3, json, yaml
import time
from pathlib import Path
from openai import OpenAI

job_db = Path("jobs.db").resolve()
j_conn = sqlite3.connect(job_db)

jobs = j_conn.execute("""
SELECT refnr, job_title, details FROM jobs
WHERE bewerbung = "write"
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
    begin = int(time.time())
    prompt = f"""
    Das ist mein Lebenslauf: 
    {cv}
    ...ich bewerbe mich als {job[1]}:
    {job[2]}
    ich möchte ein kurzes Anschreiben haben. Gib mir nur den Inhalt. 
    KEINE ANREDE.
    KEINE GRUẞFORMEL.
    """
    response = client.chat.completions.create(
        model="local-model",  # name doesn't matter much, server ignores it usually
        messages=[
            {
                "role": "system", 
                "content": f'Du bist {cv["person"]["vorname"]+" "+cv["person"]["nachname"]}'
                },
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=8096,
    )
    print(response)
    anschreiben = response.choices[0].message.content
    end =  int(time.time())
    inference_time = end - begin
    print(job[1])
    print(anschreiben)
    print(inference_time)
    j_conn.execute('''
    UPDATE jobs 
    SET anschreiben=?, bewerbung="written", write_prompt=? 
    WHERE refnr=?
    ''',
               (anschreiben, prompt, job[0]))
    j_conn.commit()
j_conn.close()
