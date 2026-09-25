import yaml, sys, os
import re
import sqlite3
from pathlib import Path
from dataclasses import dataclass
from slugify import slugify
from unidecode import unidecode
import render_letter

@dataclass
class RenderConfig:
    color: str = "002F87"
    signature: str = "unterschrift_transparent.png"
    output_dir: Path = Path("output")

rcfg = RenderConfig()

voll = yaml.safe_load(open("config.yaml", encoding="utf-8"))
with open(voll['CvPath'], "r") as f:
    cv = yaml.safe_load(f)

job_db = Path(voll['JobDb']).resolve()
j_conn = sqlite3.connect(job_db)

def get_ort(plz):
    if plz is None:
        return ''
    if plz[0:1] == 89:
        return 'München'
    else:
        sys.exit()

def main():
    jobs = j_conn.execute('''
    SELECT refnr, plz, ort, firma, job_title, kontakt, anschreiben
    FROM jobs
    WHERE bewerbung = "written" OR bewerbung = "gereadet"
    ORDER BY seit ASC
                   ''').fetchall()
    for job in jobs:
        firma_addr = None
        plz = job[1]
        ort = job[2]
        if ort is None:
            ort = get_ort(plz)
        firma = job[3]
        if firma is None:
            firma = '99999'
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
        firma_s = unidecode(slugify(firma))
        print(firma)
        print(firma_s)
        out = Path("output") / f"anschreiben_{firma_s}.tex"
        i = 1
        # while out.exists():
        #    out = Path("output") / f'anschreiben_{firma_s+"_"+str(i)}.tex'
        #    i += 1
        out.write_text(tex, encoding="utf-8")
        print(f"  → {out}")
        print(job[0])
        j_conn.execute('''
        UPDATE jobs 
        SET bewerbung="rendered"
        WHERE refnr=?
        ''', (job[0],))
        j_conn.commit()

if __name__ == "__main__":
    main()
