from pathlib import Path
from dataclasses import dataclass
from datetime import date

@dataclass
class RenderConfig:
    color: str = "002F87"
    signature: str = ""
    output_dir: Path = Path("output")

def german_date() -> str:
    months = {
        1: "Januar", 2: "Februar", 3: "März", 4: "April",
        5: "Mai", 6: "Juni", 7: "Juli", 8: "August",
        9: "September", 10: "Oktober", 11: "November", 12: "Dezember",
    }
    d = date.today()
    return f"{d.day}.~{months[d.month]} {d.year}"

def esc(s: str) -> str:
    """Escape special LaTeX characters in user-facing strings."""
    return s.replace("&", r"\&").replace("%", r"\%").replace("_", r"\_").replace("#", r"\#")

def render(
        cv: dict,
        cfg: RenderConfig,
        firma_addr : str,
        firma : str,
        plz : int,
        ort : str,
        job_title : str,
        kontakt : str,
        anschreiben : str,
        )  -> str:
    p = cv["person"]
    me_adr = p["adresse"]
    me_kontakt = p["kontakt"]

    # Empfänger
    if plz is None or plz is 99999:
        empfaenger = firma
    else:
        empfaenger = str(plz)+' '+ort
        empfaenger = firma + '\\\\' + empfaenger
    if firma_addr:
        empfaenger = firma_addr + '\\\\' + empfaenger
    if kontakt:
        empfaenger = kontakt + '\\\\' + empfaenger

    # Anrede
    anrede_line = "Sehr geehrte Damen und Herren,"
    if kontakt:
        er = "r" if kontakt.startswith("Herr ") else ""
        anrede_line = f"Sehr geehrte{er} {kontakt}"

    # Betreff
    betreff = f"Bewerbung {esc(job_title)}"
    datum = german_date()

    # Body: escape & in LLM-generated text
    anschreiben = esc(anschreiben)

    tex = rf"""\documentclass[11pt, a4paper, sans]{{moderncv}}

\moderncvstyle{{banking}}
\moderncvcolor{{black}}

\usepackage{{lmodern}}
\usepackage[scale=0.85, top=20mm, bottom=20mm]{{geometry}}
\usepackage[ngerman, provide=*]{{babel}}
\usepackage{{graphicx}}
\usepackage{{eso-pic}}

% ── Config (keep in sync with CV) ────────────────────────────────────
\newcommand{{\maincolor}}{{{cfg.color}}}
\definecolor{{ribbon}}{{HTML}}{{\maincolor}}

% Ribbon
\AddToShipoutPictureFG{{%
  \AtPageUpperLeft{{%
    \put(17pt,-85pt){{\color{{ribbon}}\rule{{7pt}}{{85pt}}}}%
  }}%
}}

% ── Person ───────────────────────────────────────────────────────────
\firstname{{{esc(p['vorname'])}}}
\familyname{{{esc(p['nachname'])}}}
\address{{{p['adresse']['strasse']}}}{{{p['adresse']['plz']}}}{{}}
\phone[mobile]{{{me_kontakt['mobil']}}}
\email{{{me_kontakt['email']}}}
\social[github]{{{me_kontakt['github']}}}

% ── Letter fields ────────────────────────────────────────────────────
\recipient{{{empfaenger}}}{{}}
\date{{{p['adresse']['stadt'].split()[-1]}, den {german_date()}}}
\opening{{~}}

\begin{{document}}

\makelettertitle
\vspace{{-1em}}

\noindent
\textbf{{{betreff}}}

\vspace{{4mm}}

\noindent
{anrede_line}

\vspace{{2mm}}

{anschreiben}

\vspace{{1em}}
\noindent Mit freundlichen Grüßen, \\[0.6em]
\vspace{{1em}}
\parbox[t]{{5cm}}{{%
\IfFileExists{{{cfg.signature}}}{{%
  \includegraphics[height=0.8cm]{{{cfg.signature}}}\\
}}{{}}%

\textbf{{{esc(p['vorname'])} {esc(p['nachname'])}}}
}}

\end{{document}}
"""
    return tex
