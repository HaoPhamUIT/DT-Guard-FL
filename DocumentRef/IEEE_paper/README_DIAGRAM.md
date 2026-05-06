# DT-Guard Architecture Diagram

## Compile Instructions

### Option 1: Local LaTeX (if installed)
```bash
cd DocumentRef/IEEE_paper/
pdflatex dtguard-architecture.tex
```

### Option 2: Overleaf (Recommended)
1. Go to https://www.overleaf.com/
2. Create new project → Upload `dtguard-architecture.tex`
3. Compile (Ctrl+S or click Recompile)
4. Download PDF
5. Place `dtguard-architecture.pdf` in `IEEE_paper/` folder

### Option 3: Online LaTeX Compiler
- https://latexbase.com/
- https://www.latex4technics.com/
- Paste code → Compile → Download PDF

## Usage in Paper

Once you have `dtguard-architecture.pdf`, add to your paper:

```latex
\begin{figure*}[htbp]
\centerline{\includegraphics[width=0.95\textwidth]{dtguard-architecture.pdf}}
\caption{Architecture of DT-Guard. Client updates are routed through the Digital Twin for behavioral testing before aggregation. The four-layer pipeline and DT-PW scoring run in parallel inside the DT.}
\label{fig:framework}
\end{figure*}
```

## Install LaTeX (if needed)

### macOS
```bash
brew install --cask mactex
```

### Ubuntu/Debian
```bash
sudo apt-get install texlive-full
```

### Windows
Download MiKTeX: https://miktex.org/download
