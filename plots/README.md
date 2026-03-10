# Plots Directory

This directory contains all plotting and visualization scripts organized by purpose.

## 📁 Directory Structure

### `/paper/` - IEEE ICCE 2026 Paper Figures
**Visualization scripts for the 6-page IEEE paper.**

- **`generate_paper_plots.py`** - Main plotting script for 3 paper figures
  - **Fig. 2 (Gap 1):** Accuracy degradation vs malicious ratio
    - Panel (a): Accuracy per attack (5 groups × 10 defense bars)
    - Panel (b): Detection Rate per attack
  - **Fig. 3 (Gap 2):** False Positive Rate at 50% malicious
    - Heatmap format: rows=defenses, cols=attacks
    - Shows DT-Guard maintains low FPR while baselines fail
  - **Fig. 4 (Gap 3):** Weight distribution per client
    - 4 subplots: DT-PW / Trust-Score / Uniform / FedAvg
    - Shows how only DT-PW suppresses free-rider weights

- **`generate_plots_v2.py`** - Enhanced version with additional features
  - Improved styling for IEEE format
  - Better color schemes and layouts
  - Support for multiple output formats (PDF, PNG, SVG)

- **`plot_dtpw_dynamics.py`** - DT-PW dynamics visualization
  - Shows how DT-PW weights evolve across rounds
  - Illustrates committee selection process
  - Displays Shapley value convergence

- **`generate_overhead_plot.py`** - Computational overhead visualization
  - Plots latency comparison across defenses
  - Memory usage charts
  - Trade-off analysis

**Usage:**
```bash
# Generate all 3 paper figures
python plots/paper/generate_paper_plots.py

# Generate specific figure
python plots/paper/generate_paper_plots.py --only fig2  # Accuracy + Detection Rate
python plots/paper/generate_paper_plots.py --only fig3  # FPR heatmap
python plots/paper/generate_paper_plots.py --only fig4  # Weight distribution

# Change format/DPI
python plots/paper/generate_paper_plots.py --fmt png --dpi 600

# Print inline numbers for paper prose
python plots/paper/generate_paper_plots.py --inline

# Generate overhead plot
python plots/paper/generate_overhead_plot.py

# DT-PW dynamics
python plots/paper/plot_dtpw_dynamics.py
```

### `/thesis/` - Thesis Plots
**Legacy plotting scripts from the thesis work.**

- **`generate_plots.py`** - Original plotting script
  - Basic visualizations for thesis experiments
  - May use different styling conventions
  - Kept for reproducibility of thesis figures

**Note:** These scripts use older plotting styles and may not match IEEE format requirements.

## 📊 Output Structure

Generated figures are saved to:
```
results/paper_experiments/figures/
├── fig2_degradation.pdf       # Gap 1: Accuracy degradation
├── fig3_fpr.pdf               # Gap 2: FPR heatmap
├── fig4_weights.pdf           # Gap 3: Weight distribution
├── overhead_comparison.pdf    # Overhead analysis
└── dtpw_dynamics.pdf          # DT-PW dynamics
```

## 🎨 Styling

Paper plots follow IEEE conference format:
- **Single-column width:** 3.5 inches
- **Double-column width:** 7.16 inches
- **Font:** Times New Roman, 8pt
- **DPI:** 300 (default), 600 for final submission
- **Format:** PDF (vector), PNG (raster fallback)

## 🔧 Dependencies

All plotting scripts require:
```bash
pip install matplotlib numpy
```

For paper plots, additional recommended packages:
```bash
pip install seaborn  # For enhanced color palettes
```

## 📝 LaTeX Integration

Figures are designed to work with IEEE template:
```latex
\begin{figure}[htbp]
\centerline{\includegraphics[width=\columnwidth]{figures/fig2_degradation.pdf}}
\caption{Defense robustness at 50\% malicious clients.}
\label{fig:degradation}
\end{figure}
```

Use the `--inline` flag to get numbers for `\DTfill{}` placeholders in the LaTeX template.
