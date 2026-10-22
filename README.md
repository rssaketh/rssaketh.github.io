# CV source

LaTeX source for Sai Saketh Rambhatla's CV. The website uses
`styles/style3_editorial.pdf` (copied to `data/rssaketh.pdf` on `master`).

| File | What it is |
|---|---|
| `main.tex` | Base CV (rendercv-style template) |
| `styles/style1_classic.tex` | Classic layout, teal accent |
| `styles/style2_sidebar.tex` | Two columns with a tinted sidebar |
| `styles/style3_editorial.tex` | EB Garamond, small-caps labels — **used on the website** |
| `styles/style4_band.tex` | Full-width coloured header band |
| `tools/content.py` | Shared content for the four styles |
| `tools/gen.py` | Regenerates `styles/*.tex` from `content.py` (style 1 is derived from `main.tex`) |

## Build

Requires [tectonic](https://tectonic-typesetting.github.io/).

```sh
tectonic main.tex                          # base CV
python3 tools/gen.py styles                # regenerate the four styles after editing tools/content.py
(cd styles && for f in style*.tex; do tectonic "$f"; done)
```

To update the website CV, copy `styles/style3_editorial.pdf` to `data/rssaketh.pdf` on `master`.
