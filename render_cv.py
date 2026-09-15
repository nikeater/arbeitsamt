

# ── CV ───────────────────────────────────────────────────────────────

def render_cv(cv: dict, match: dict | None, meta: dict | None, cfg: RenderConfig) -> str:
    p = cv["person"]
    tex = []

    tex.append(rf"""\documentclass[10pt, a4paper, sans]{{moderncv}}

\moderncvstyle{{{cfg.cv_style}}}
\moderncvcolor{{black}}

\usepackage{{lmodern}}
\usepackage[scale=0.85, top=20mm, bottom=16mm]{{geometry}}
\usepackage[ngerman, provide=*]{{babel}}
\usepackage{{tikz}}
\usepackage{{eso-pic}}

""")
    tex.append(rf"""
% ── Config ───────────────────────────────────────────────────────────
\newcommand{{\maincolor}}{{{cfg.color}}}
\definecolor{{ribbon}}{{HTML}}{{\maincolor}}
\definecolor{{barlight}}{{HTML}}{{D6DFE8}}
\definecolor{{barlabel}}{{HTML}}{{555555}}
\definecolor{{barpct}}{{HTML}}{{999999}}

% Ribbon
\AddToShipoutPictureFG{{%
  \AtPageUpperLeft{{%
    \put(17pt,-113pt){{\color{{ribbon}}\rule{{7pt}}{{113pt}}}}%
  }}%
}}
""")
    tex.append(rf"""
\firstname{{{esc(p['vorname'])}}}
\familyname{{{esc(p['nachname'])}}}
\address{{{esc(p['strasse'])}}}{{{esc(p['plz_ort'])}}}{{}}
\phone[mobile]{{{p['telefon']}}}
\email{{{p['email']}}}
\extrainfo{{Geb.\ {p['geburtsdatum']}}}

\begin{{document}}
\makecvtitle""")

    # Match section
    if match and meta:
        titel = esc(meta.get("stellentitel", ""))
        firma = esc(meta.get("unternehmen", ""))
        ref = meta.get("referenznummer", "")

        header = f"Passung: {titel}"
        if firma:
            header += f" --- {firma}"
        if ref:
            ref = ref.replace("_", "-")
            header += rf" (Ref.\ {ref})"

        tex.append(rf"""
\section{{{header}}}
\vspace{{-2pt}}%""")

        bars = []
        for cat in match.get("kategorien", [])[:2]:
            bars.append((esc(cat["name"]), cat["score"]))
        exp = match.get("erfahrung", 0)
        bars.append(("Erfahrung", exp))

        tex.append(r"\noindent\begin{minipage}[c]{0.48\textwidth}")
        tex.append(r"  \begin{tikzpicture}")
        for idx, (label, score) in enumerate(bars):
            y = -idx * 0.42
            tex.append(rf"    \matchbar{{{label}}}{{{score:.2f}}}{{{y:.2f}}}")
        tex.append(r"  \end{tikzpicture}")
        tex.append(r"\end{minipage}\hfill\begin{minipage}[c]{0.46\textwidth}")

        if cfg.disclaimer:
            tex.append(r"  \raggedright")
            tex.append(r"  {\scriptsize\color{black}%")
            tex.append(r"   Die dargestellte Passungsanalyse wurde ")
            tex.append(r"   mittels eigenentwickeltem Matching auf")
            tex.append(r"   Basis von Zero-Shot Natural Language")
            tex.append(r"   Inference (Laurer et al., BGE-M3) automatisiert")
            tex.append(r"   erstellt.}")
 
        tex.append(r"\end{minipage}")
        tex.append(r"\vspace{4pt}")

    # Experience
    tex.append(r"""
\section{Berufserfahrung}""")
    for e in cv["erfahrung"]:
        bullets = e["beschreibung"]
        if isinstance(bullets, list):
            items = bullets
        else:
            items = [s.strip() for s in bullets.replace("\\,\\%", "PCTHOLD").split(". ") if s.strip()]
            items = [s.rstrip(".").replace("PCTHOLD", "\\,\\%") for s in items]

        itemtex = "\n".join(rf"    \item {esc(it)}" for it in items)
        tex.append(rf"""\cventry{{{e['zeitraum']}}}{{{esc(e['titel'])}}}{{{esc(e['firma'])}}}{{{esc(e['ort'])}}}{{}}{{%
  \begin{{itemize}}%
{itemtex}
  \end{{itemize}}
}}""")

    # Skills
    tex.append(r"""
\section{Kenntnisse \& Fähigkeiten}""")
    k = cv["kenntnisse"]
    for i in range(0, len(k), 2):
        a = k[i]
        if i + 1 < len(k):
            b = k[i + 1]
            tex.append(rf"""\cvdoubleitem
  {{\textbf{{{esc(a['label'])}}}}}{{{esc(a['items'])}}}
  {{\textbf{{{esc(b['label'])}}}}}{{{esc(b['items'])}}}""")
        else:
            tex.append(rf"\cvitem{{\textbf{{{esc(a['label'])}}}}}{{{esc(a['items'])}}}")

    # Education
    tex.append(r"""
\section{Bildung}""")
    for b in cv["bildung"]:
        details = b.get("details", [])
        if details:
            itemtex = "\n".join(rf"    \item {esc(d)}" for d in details)
            tex.append(rf"""\cventry{{{b['zeitraum']}}}{{{b['abschluss']}}}{{{esc(b['institution'])}}}{{}}{{\textit{{{b['note']}}}}}{{%
  \begin{{itemize}}%
{itemtex}
  \end{{itemize}}
}}""")
        else:
            tex.append(rf"\cventry{{{b['zeitraum']}}}{{{b['abschluss']}}}{{{esc(b['institution'])}}}{{}}{{\textit{{{b['note']}}}}}{{}}")

    tex.append(r"""
\end{document}""")
    return "\n".join(tex)


# ── Cover letter ─────────────────────────────────────────────────────

