import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from content import *
OUT = sys.argv[1]

def hdr_links(sep, fa=True):
    items = [
        (PHONE, r"\faPhone*"), (EMAIL, r"\faEnvelope[regular]"), (WEB, r"\faLink"),
        (SCHOLAR, r"\faGraduationCap"), (LINKEDIN, r"\faLinkedinIn")]
    return sep.join(r"\mbox{\hrefWithoutArrow{%s}{{\small %s}\hspace{0.12cm}%s}}" % (u, ic, t) for (u, t), ic in items)

COMMON = r"""
\usepackage{xcolor}
\usepackage{enumitem}
\usepackage{fontawesome5}
\usepackage{etoolbox}
\usepackage{ifthen}
\usepackage[pdftitle={Sai Saketh Rambhatla - CV}, pdfauthor={Sai Saketh Rambhatla}, colorlinks=true, urlcolor=accent, linkcolor=accent]{hyperref}
\let\hrefWithoutArrow\href
\setlength{\parindent}{0pt}
"""

# ---------------------------------------------------------------- style 1
def style1():
    src = open(os.path.join(OUT, "..", "main.tex")).read()
    rep = [
        (r"\definecolor{primaryColor}{RGB}{0, 79, 144}", r"\definecolor{primaryColor}{RGB}{0, 110, 112}"),
        (r"\definecolor{advisorcolor}{RGB}{187, 139, 116}", r"\definecolor{advisorcolor}{RGB}{95, 110, 115}"),
        (r"\textbf{#1}\hspace{0.15cm}\titlerule[0.8pt]\hspace{-0.1cm}", r"\textbf{#1}\hspace{0.2cm}\titlerule[0.4pt]\hspace{-0.1cm}"),
        ("        \\Large\\color{primaryColor}", "        \\large\\color{primaryColor}"),
        ("        0.2 cm\n    } % section title spacing", "        0.15 cm\n    } % section title spacing"),
        ("parsep=0.10 cm,", "parsep=0.06 cm,"),
        (r"\fontsize{20 pt}{20 pt}", r"\fontsize{24 pt}{24 pt}"),
        (r"\textcolor{gray}{#3}", r"\textcolor{primaryColor!75!black}{\textit{#3}}"),
        (r"\pdfgentounicode", r"\pdfgentounicode"),
    ]
    for a, b in rep:
        assert a in src, a
        src = src.replace(a, b)
    import re
    src = re.sub(r"& \\hfill ((?:[A-Z][a-z]{2} \d{4}) -- (?:Present|[A-Z][a-z]{2} \d{4}))",
                 lambda m: r"& \hfill\textcolor{primaryColor}{%s}" % m.group(1), src)
    src = src.replace(r"\renewcommand{\href}", r"\colorlet{accent}{primaryColor}\renewcommand{\href}")
    # thin accent rule under header
    src = src.replace("    \\end{header}\n", "    \\end{header}\n    {\\color{primaryColor!40}\\rule{\\textwidth}{0.4pt}}\n", 1)
    return src

# ---------------------------------------------------------------- style 2: sidebar
def style2():
    jobs = "\n".join(r"""\job{%s}{%s, %s}{%s}{%s}""" % j for j in JOBS)
    pubs = "\n".join(r"\pub{%s}{%s}{%s}" % (t, a, s) for t, a, f, s in PUBS)
    edu = "\n".join(r"\sdegree{%s}{%s}{%s}{%s}" % (d, sc, dt, r"\\ ".join(x)) for d, sc, dt, x in EDU)
    interns = "\n".join(r"\intern{%s}{%s (%s)}{%s}{%s}" % i for i in INTERN)
    awards = "\n".join(r"\item %s" % a for a in AWARDS)
    links = [(PHONE, r"\faPhone*"), (EMAIL, r"\faEnvelope[regular]"), (WEB, r"\faLink"), (SCHOLAR, r"\faGraduationCap"), (LINKEDIN, r"\faLinkedinIn")]
    contact = "\n".join(r"\contact{%s}{%s}{%s}" % (ic, u, t) for (u, t), ic in links)
    return r"""\documentclass[10pt, letterpaper]{article}
\usepackage[left=1.1cm, right=1.3cm, top=1.3cm, bottom=1.4cm]{geometry}
\definecolor{accent}{RGB}{44, 62, 92}
\definecolor{tint}{RGB}{238, 242, 247}
\definecolor{muted}{RGB}{105, 115, 130}
""" .replace(r"\definecolor", r"\RequirePackage{xcolor}\definecolor", 1) + COMMON + r"""
\usepackage[default]{sourcesanspro}
\usepackage{paracol}
\usepackage{eso-pic}
\usepackage[explicit]{titlesec}
\usepackage{lastpage}
\pagestyle{empty}
\setcounter{secnumdepth}{0}
\renewcommand{\href}[2]{\hrefWithoutArrow{#1}{#2}}
% tinted sidebar on every page
\AddToShipoutPictureBG{\AtPageLowerLeft{\color{tint}\rule{6.85cm}{\paperheight}}}
\columnratio{0.29}
\setlength{\columnsep}{0.9cm}
\titleformat{\section}{\color{accent}\bfseries\large}{}{0pt}{#1}[\vspace{-0.55em}{\color{accent!35}\rule{\linewidth}{0.6pt}}]
\titlespacing{\section}{0pt}{0.55cm}{0.25cm}
\newcommand{\sidesec}[1]{\par\vspace{0.5cm}{\color{accent}\bfseries\small\MakeUppercase{#1}}\par\vspace{-0.3em}{\color{accent!40}\rule{\linewidth}{0.6pt}}\par\vspace{0.15cm}}
\newcommand{\contact}[3]{\mbox{\makebox[0.5cm][l]{\color{accent}\small #1}\hrefWithoutArrow{#2}{\small\color{black}#3}}\par\vspace{0.12cm}}
\newcommand{\sdegree}[4]{{\bfseries #1}\par{\small #2}\par{\small\color{accent} #3}\par\vspace{0.05cm}{\footnotesize\color{muted} #4\par}\vspace{0.3cm}}
\newcommand{\job}[4]{{\bfseries #1}\hfill{\small\color{accent}\bfseries #3}\par{\color{muted}#2}\par\vspace{0.08cm}\begin{itemize}[leftmargin=0.4cm, topsep=0pt, itemsep=0pt]\item #4\end{itemize}\vspace{0.25cm}}
\newcommand{\pub}[3]{\item\begin{minipage}[t]{\linewidth}\raggedright{\bfseries #1}\\{\small #2}\\{\small\color{accent}\itshape #3}\end{minipage}}
\newcommand{\intern}[4]{{\bfseries #1}, #2\par{\small\color{muted} #3}\par\vspace{0.05cm}#4\par\vspace{0.25cm}}
\newcommand{\me}{\textbf{Sai Saketh Rambhatla}}
\begin{document}
\begin{paracol}{2}
\raggedright
{\fontsize{22pt}{24pt}\selectfont\bfseries\color{accent} Sai Saketh\\Rambhatla\par}
\vspace{0.2cm}
{\small\color{muted} Member of Technical Staff\\Skild AI Research\par}
\sidesec{Contact}
""" + contact + r"""
\sidesec{Education}
""" + edu + r"""
\sidesec{Reviewing}
{\small """ + REVIEW_CONF + r""".\par\vspace{0.1cm}""" + REVIEW_JOUR + r""".\par}
\sidesec{Awards}
\begin{itemize}[leftmargin=0.3cm, topsep=0pt, itemsep=3pt, parsep=0pt, label={\color{accent}\textbullet}]\small
""" + awards + r"""
\end{itemize}
\switchcolumn
\raggedright
\vspace*{-0.55cm}
\section{Experience}
""" + jobs + r"""
\section{Selected Publications}
\begin{itemize}[leftmargin=0.35cm, topsep=0pt, itemsep=4pt, label={\color{accent}\small\textbullet}]
""" + pubs + r"""
\end{itemize}
\section{Research Internships}
""" + interns + r"""
\end{paracol}
\end{document}
"""

# ---------------------------------------------------------------- style 3: editorial serif
def style3():
    jobs = "\n".join(r"\job{%s}{%s}{%s}{%s}{%s}" % j for j in JOBS)
    pubs = "\n".join(r"\pub{%s}{%s}{%s}" % (t, a, f) for t, a, f, s in PUBS)
    edu = "\n".join(r"\degree{%s}{%s}{%s}{%s}" % (d, sc, dt, "; ".join(x)) for d, sc, dt, x in EDU)
    interns = "\n".join(r"\intern{%s}{%s}{%s}{%s}{%s}" % i for i in INTERN)
    awards = "\n".join(r"\item %s" % a for a in AWARDS)
    return r"""\documentclass[10pt, letterpaper]{article}
\usepackage[left=2.3cm, right=2.3cm, top=1.9cm, bottom=1.9cm]{geometry}
\RequirePackage{xcolor}
\definecolor{accent}{RGB}{122, 31, 43}
\definecolor{muted}{RGB}{95, 95, 95}
""" + COMMON + r"""
\usepackage{ebgaramond}
\usepackage[explicit]{titlesec}
\pagestyle{empty}
\setcounter{secnumdepth}{0}
\renewcommand{\href}[2]{\hrefWithoutArrow{#1}{#2}}
\titleformat{\section}{\normalsize\color{accent}}{}{0pt}{\addfontfeatures{LetterSpace=14}\scshape\MakeLowercase{#1}}[\vspace{-0.45em}{\color{accent!60}\rule{\linewidth}{0.3pt}}]
\titlespacing{\section}{0pt}{0.6cm}{0.3cm}
\newcommand{\job}[5]{\textbf{#1}, #2, #3\hfill{\itshape\color{muted} #4}\par\vspace{0.05cm}{\leftskip=0.4cm #5\par}\vspace{0.22cm}}
\newcommand{\degree}[4]{\textbf{#1}, #2\hfill{\itshape\color{muted} #3}\par{\leftskip=0.4cm\color{muted} #4\par}\vspace{0.18cm}}
\newcommand{\pub}[3]{\item\begin{minipage}[t]{\linewidth}#1\\{\small #2}\\{\small\itshape\color{muted} #3}\end{minipage}}
\newcommand{\intern}[5]{\textbf{#1}, #2 (#3)\hfill{\itshape\color{muted} #4}\par{\leftskip=0.4cm #5\par}\vspace{0.18cm}}
\newcommand{\me}{\textbf{Sai Saketh Rambhatla}}
\begin{document}
\begin{center}
{\fontsize{26pt}{28pt}\selectfont\color{accent} Sai Saketh Rambhatla\par}
\vspace{0.25cm}
{\small """ + r"\hspace{0.3cm}{\color{accent!50}\textperiodcentered}\hspace{0.3cm}".join(r"\hrefWithoutArrow{%s}{%s}" % x for x in [PHONE, EMAIL, WEB, SCHOLAR, LINKEDIN]) + r"""\par}
\end{center}
\vspace{0.1cm}
\section{Employment}
""" + jobs + r"""
\section{Education}
""" + edu + r"""
\section{Selected Publications}
\begin{enumerate}[leftmargin=0.7cm, topsep=0pt, itemsep=4pt, label={\small\color{accent}\arabic*.}]
""" + pubs + r"""
\end{enumerate}
\section{Research Internships}
""" + interns + r"""
\section{Awards}
\begin{itemize}[leftmargin=0.5cm, topsep=0pt, itemsep=1pt, parsep=0pt, label={\color{accent}\textperiodcentered}]
""" + awards + r"""
\end{itemize}
\section{Academic Service}
\textbf{Reviewing.} """ + REVIEW_CONF + r"""; """ + REVIEW_JOUR + r""".
\end{document}
"""

# ---------------------------------------------------------------- style 4: header band
def style4():
    jobs = "\n".join(r"\job{%s}{%s}{%s}{%s}{%s}" % j for j in JOBS)
    pubs = "\n".join(r"\pub{%s}{%s}{%s}" % (t, a, s) for t, a, f, s in PUBS)
    edu = "\n".join(r"\degree{%s}{%s}{%s}{%s}" % (d, sc, dt, " \\textperiodcentered{} ".join(x)) for d, sc, dt, x in EDU)
    interns = "\n".join(r"\intern{%s}{%s}{%s}{%s}{%s}" % i for i in INTERN)
    awards = "\n".join(r"\item %s" % a for a in AWARDS)
    return r"""\documentclass[10pt, letterpaper]{article}
\usepackage[left=1.7cm, right=1.7cm, top=1.6cm, bottom=1.5cm]{geometry}
\RequirePackage{xcolor}
\definecolor{accent}{RGB}{29, 78, 137}
\definecolor{muted}{RGB}{100, 108, 120}
""" + COMMON + r"""
\usepackage[default]{sourcesanspro}
\usepackage{tikz}
\usepackage{amssymb}
\usepackage[explicit]{titlesec}
\usepackage{eso-pic}
\pagestyle{empty}
\setcounter{secnumdepth}{0}
\renewcommand{\href}[2]{\hrefWithoutArrow{#1}{#2}}
\titleformat{\section}{\color{accent}\bfseries\large}{}{0pt}{{\color{accent}\rule[-0.15em]{4pt}{1.05em}}\hspace{0.25cm}\MakeUppercase{#1}}
\titlespacing{\section}{0pt}{0.45cm}{0.2cm}
\newcommand{\datepill}[1]{{\setlength{\fboxsep}{2pt}\colorbox{accent!10}{\small\color{accent}\bfseries #1}}}
\newcommand{\job}[5]{\textbf{#1} \textperiodcentered{} #2, #3\hfill\datepill{#4}\par\vspace{0.03cm}{\leftskip=0.5cm #5\par}\vspace{0.18cm}}
\newcommand{\degree}[4]{\textbf{#1} \textperiodcentered{} #2\hfill\datepill{#3}\par{\leftskip=0.5cm\color{muted}\small #4\par}\vspace{0.15cm}}
\newcommand{\pub}[3]{\item\begin{minipage}[t]{\linewidth}\textbf{#1}\hfill{\small\color{accent}\bfseries #3}\\{\small #2}\end{minipage}}
\newcommand{\intern}[5]{\textbf{#1} \textperiodcentered{} #2\hfill\datepill{#3}\par{\leftskip=0.5cm #5 {\color{muted}\small(#4)}\par}\vspace{0.15cm}}
\newcommand{\me}{\textbf{Sai Saketh Rambhatla}}
\AddToShipoutPictureBG*{\begin{tikzpicture}[remember picture, overlay]
\fill[accent] (current page.north west) rectangle ([yshift=-3.9cm]current page.north east);
\end{tikzpicture}}
\begin{document}
\vspace*{-0.55cm}
{\color{white}
{\fontsize{26pt}{28pt}\selectfont\bfseries Sai Saketh Rambhatla\par}
\vspace{0.12cm}
{\large Member of Technical Staff, Skild AI Research\par}
\vspace{0.22cm}
\hypersetup{urlcolor=white}
{\small """ + hdr_links(r"\hspace{0.45cm}") + r"""\par}
\hypersetup{urlcolor=accent}
}
\vspace{0.75cm}
\section{Employment}
""" + jobs + r"""
\section{Education}
""" + edu + r"""
\section{Selected Publications}
\begin{itemize}[leftmargin=0.4cm, topsep=0pt, itemsep=3pt, label={\color{accent}\small$\blacktriangleright$}]
""" + pubs.replace(r"\item", r"\item") + r"""
\end{itemize}
\section{Research Internships}
""" + interns + r"""
\section{Awards}
\begin{itemize}[leftmargin=0.4cm, topsep=0pt, itemsep=0pt, parsep=0pt, label={\color{accent}\small$\blacktriangleright$}]
""" + awards + r"""
\end{itemize}
\section{Academic Service}
\textbf{Reviewing:} """ + REVIEW_CONF + r""". \textbf{Journals:} """ + REVIEW_JOUR + r""".
\end{document}
"""

for name, fn in [("style1_classic", style1), ("style2_sidebar", style2), ("style3_editorial", style3), ("style4_band", style4)]:
    open(os.path.join(OUT, name + ".tex"), "w").write(fn())
print("written")
