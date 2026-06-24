# BI-RADS Anchored AI Evaluation Framework

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20821730.svg)](https://doi.org/10.5281/zenodo.20821730)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

This repository contains the official code and data simulation methodology for the paper: **"BI-RADS Anchored Evaluation of Artificial Intelligence for Breast Cancer Screening in Digital Mammography: A Clinical Utility Framework Beyond AUC"**.

It provides a reproducible implementation of a BI-RADS-anchored clinical utility framework for evaluating AI models in breast cancer screening, moving beyond standard AUC metrics to assess calibration, workload-anchored performance, decision curve analysis (DCA), and subgroup equity.

## 📋 Features

- **Data Simulation:** Code to generate a dataset matching the statistical properties of the VinDr-Mammo dataset (N=5,000).
- **Evaluation Pipeline:** 
  - Global discrimination (AUC, PR-AUC with stratified bootstrap CIs)
  - Calibration assessment (Brier score, ECE, calibration-in-the-large)
  - Workload-anchored operating points (BI-RADS 3 recall, BI-RADS 4 biopsy)
  - Decision Curve Analysis (DCA) including combined AI+BI-RADS strategies
  - Subgroup equity audits (age, density, lesion type)
- **Publication-Ready Figures:** Automated generation of all 7 manuscript figures.

## 🚀 Quick Start

### 1. Clone and Setup Environment

```bash
git clone https://github.com/[username]/birads-ai-evaluation.git
cd birads-ai-evaluation

# Create conda environment
conda env create -f environment.yml
conda activate birads-ai
```

### 2. Run the Pipeline

```bash
# Generate the simulated dataset
python src/data/simulate_data.py

# Run the full evaluation pipeline
python src/evaluation/run_evaluation.py

# Generate all figures
python src/evaluation/generate_figures.py
```

Results will be saved in `results/` and figures in `figures/`.

## 📁 Repository Structure

```text
birads-ai-evaluation/
├── .github/workflows/      # CI/CD pipelines (Zenodo DOI updates)
├── data/                   # Simulated data (generated locally)
├── docs/                   # Documentation and TRIPOD+AI checklists
│   ├── simulation_methodology.md
│   └── TRIPOD_AI_AUDIT.md
├── figures/                # Output directory for generated figures
├── results/                # Output directory for evaluation metrics
├── scripts/                # Bash scripts for releases
├── src/                    # Source code
│   ├── data/               # Data generation scripts
│   ├── evaluation/         # Analysis, metrics, DCA, and plotting
│   └── utils/              # Helper functions (bootstrapping, etc.)
├── CITATION.cff            # Citation metadata
├── environment.yml         # Conda environment definition
├── LICENSE                 # MIT License
└── README.md               # This file
```

## 📖 Documentation

- [Simulation Methodology (Appendix A)](docs/simulation_methodology.md)
- [TRIPOD+AI Audit Checklist (Appendix B)](docs/TRIPOD_AI_AUDIT.md)

## 📝 Citation

If you use this framework or code in your research, please cite our paper:

```bibtex
@article{author_birads_2026,
  author = {Bandar Saad Alshreef},
  title = {BI-RADS Anchored Evaluation of Artificial Intelligence for Breast Cancer Screening in Digital Mammography: A Clinical Utility Framework Beyond AUC},
  journal = {European Radiology Experimental},
  year = {2026},
  doi = {10.5281/zenodo.20821730},
  url = {https://github.com/[username]/birads-ai-evaluation}
}
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
