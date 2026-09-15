import yaml, sys, os
import re
import sqlite3
from pathlib import Path
from dataclasses import dataclass
import render_letter

@dataclass
class RenderConfig:
    color: str = "002F87"
    signature: str = "unterschrift_transparent.png"
    output_dir: Path = Path("output")

rcfg = RenderConfig()

with open(Path.home() / "Documents/Bewerbungen/cv_deutsch.yaml", "r") as f:
    cv = yaml.safe_load(f)
cfg = yaml.safe_load(open("config.yaml", encoding="utf-8"))

job_db = Path("jobs.db").resolve()
j_conn = sqlite3.connect(job_db)

def get_ort(plz):
    if plz is None:
        return ''
    if plz[0:1] == 89:
        return 'München'
    else:
        sys.exit()

def first_word_letters_only(s):
    first = s.split(None, 1)[0] if s.split() else ""
    return re.sub(r'[^a-zA-Z]', '', first).lower()

def main():
    jobs = j_conn.execute('''
    SELECT refnr, plz, ort, firma, job_title, kontakt, anschreiben
    FROM jobs
    WHERE bewerbung = "written" OR bewerbung = "gereadet"
                   ''').fetchall()
    for job in jobs:
        firma_addr = None
        plz = job[1]
        ort = job[2]
        if ort is None:
            ort = get_ort(plz)
        firma = job[3]
        job_title = job[4] 
        kontakt = job[5]
        anschreiben = job[6]
        print(f"\n═══ Render Anschreiben ═══")
        tex = render_letter.render(
                cv,
                rcfg,
                firma_addr,
                firma,
                plz,
                ort,
                job_title,
                kontakt,
                anschreiben
                )
        out = Path("output") / f"anschreiben_{first_word_letters_only(firma)}.tex"
        out.write_text(tex, encoding="utf-8")
        print(f"  → {out}")


if __name__ == "__main__":
    main()
