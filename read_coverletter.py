import sqlite3, json, yaml
import time
from pathlib import Path
from openai import OpenAI

job_db = Path("jobs.db").resolve()
j_conn = sqlite3.connect(job_db)

# jobs aus jobs getten, wo in einstufung für refnr 
jobs = j_conn.execute("""
SELECT refnr, job_title, details, firma, anschreiben FROM jobs
WHERE bewerbung = "write"
               """).fetchall()

if firma is not None:
    firma = " von " + firma

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
Du suchst einen Kandidaten für die Position {job[1]}.
Du hast dieses Anschreiben erhalten:
    {job[4]}
Dies ist die Stellenausschreibung:
    {job[2]}
Und dies der CV des Kandidaten.
    {cv}
Was hältst du von dem Kandidaten? Ist er für die Stelle geeignet?
Hat er besonderes Potenzial für die Stelle?
Welche Kompetenzen fehlen, was bereitet Dir Sorgen?
Welche Fragen würdest Du stellen?
    """
    anweisung = '''
    Gib die Antwort als Json:
    {
        "fit": "",
        "strengths": "",
        "lacking": "",
        "fragen": ""
    }
    Fülle in "fit" die Eignung des Kandidaten ein. Nutze ausschließlich folgende Werte: "Gar nicht", "Eher nicht", "Vielleicht", "Interessant" oder "Perfekt".
    Fülle in "strengths" ein, welche Stärken Du beim Kandidaten siehst, insbesondere für deine Firma.
    Fülle in "lacking" ein, welche Kompetenzen fehlen und mögliche Gründe, weshalb der Kandidat nicht geeignet ist.
    Fülle in "fragen" ein, welche Fragen Du dem Kandidaten stellen würdest.
        '''
    prompt = frage + anweisung
    response = client.chat.completions.create(
        model="local-model",  # name doesn't matter much, server ignores it usually
        messages=[
            {"role": "system", "content": f"Du bist Personalchef{firma}"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=8096,
    )
    print(response)
    antwort = json.loads(response.choices[0].message.content)
    fit = antwort["fit"]
    strengths = antwort["strengths"]
    lacking = antwort["lacking"]
    fragen = antwort["fragen"]
    end =  int(time.time())
    inference_time = end - begin
    print(job[1])
    print(inference_time)
    j_conn.execute('''
    UPDATE jobs SET (
        fit = ?, 
        strengths = ?, 
        lacking = ?, 
        fragen = ?, 
    )bewerbung="readen" WHERE refnr=?
                   ''',
               (fit, strengths, lacking, fragen, job[0]))
    j_conn.commit()
j_conn.close()
