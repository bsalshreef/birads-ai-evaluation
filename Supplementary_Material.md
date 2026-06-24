# Supplementary Material

**Article Title:** BI-RADS Anchored Evaluation of Artificial Intelligence for Breast Cancer Screening in Digital Mammography: A Clinical Utility Framework Beyond AUC
**Author:** Bandar Saad Alshreef
**Journal:** *European Radiology Experimental*

---

## Appendix A: Data Simulation Methodology

This document outlines the statistical assumptions and methodology used to generate the simulated dataset for the BI-RADS anchored AI evaluation framework.

### 1. Objective

Because publicly available datasets (such as VinDr-Mammo) do not provide both radiologist-assigned BI-RADS assessments and calibrated continuous AI risk scores suitable for deployment, we simulated a dataset of $N=5,000$ screening mammography examinations. The goal was to exactly reproduce the published statistical properties of the VinDr-Mammo dataset while introducing a realistic, slightly miscalibrated AI risk score to test the evaluation framework.

### 2. Demographic and Clinical Variables

The simulation matched the following published distributions:

**2.1 BI-RADS Categories**
- BI-RADS 1: ~65%
- BI-RADS 2: ~23%
- BI-RADS 3: ~7%
- BI-RADS 4: ~4%
- BI-RADS 5: ~1%

**2.2 Breast Density**
- Density A: ~10%
- Density B: ~40%
- Density C: ~40%
- Density D: ~10%

**2.3 Age**
- Mean: 50 years
- Standard Deviation: 10 years
- Range clipped to: [25, 80] years

**2.4 Lesion Types**
Assigned probabilistically based on BI-RADS category:
- BI-RADS 1: No Finding (100%)
- BI-RADS 2: No Finding (70%), Mass (20%), Calcification (10%)
- BI-RADS 3: Mass (45%), Focal Asymmetry (30%), Calcification (15%), No Finding (10%)
- BI-RADS 4: Mass (50%), Calcification (25%), Architectural Distortion (15%), Focal Asymmetry (10%)
- BI-RADS 5: Mass (60%), Calcification (25%), Architectural Distortion (15%)

### 3. Cancer Outcomes

Cancer prevalence was anchored to realistic positive predictive values (PPV) per BI-RADS category to achieve an overall prevalence of ~3.2%:
- BI-RADS 1: 0.5%
- BI-RADS 2: 1.0%
- BI-RADS 3: 5.0%
- BI-RADS 4: 35.0%
- BI-RADS 5: 90.0%

*Note: In the simulation, outcome status and predictor values were generated concurrently; blinding was inherently maintained during model evaluation as the evaluation scripts had no access to the data generation parameters.*

### 4. AI Risk Score Generation

The continuous AI score was generated using a logistic model with added Gaussian noise to achieve a target global AUC of ~0.89.

1. **Base Log-Odds:** Derived from BI-RADS category, density, and age.
2. **Noise:** $\mathcal{N}(0, 1.1)$ added to simulate model uncertainty.
3. **Miscalibration:** The log-odds were systematically shifted (`log_odds * 0.82 + 0.35`) before applying the sigmoid function. This creates an overconfident model at low probabilities (intercept shift), deliberately introducing calibration errors (especially in BI-RADS 3 and 4) to demonstrate the framework's ability to detect them.

### 5. Reproducibility

The complete generation script is available in the public repository. Random seeds are fixed (`np.random.seed(42)`) to ensure the exact same dataset is generated across different environments.

---

## Appendix B: TRIPOD+AI Audit Checklist

This checklist audits the study against the TRIPOD+AI (Transparent Reporting of a multivariable prediction model for Individual Prognosis Or Diagnosis + Artificial Intelligence) guidelines. 

**Overall Compliance: 100%** (47/47 items compliant)

| Section | Item | Status | Addressed in |
| :--- | :--- | :---: | :--- |
| **Title/Abstract** | 1a-1c: Identify study, AI mention, population/outcome | ✅ | Title page, Abstract |
| **Introduction** | 2a-2b: Clinical context, rationale, objectives | ✅ | Introduction |
| **Methods (Data)** | 3a-3e: Study design, dates, criteria, data sources | ✅ | Methods 4.1, 4.2, Appendix A |
| **Methods (Participants)** | 4a-4c: Characteristics, sample size, missing data | ✅ | Methods 4.2, Results (Table 1) |
| **Methods (Outcome)** | 5a-5c: Define outcome, measurement, blinding | ✅ | Methods 4.3, Appendix A |
| **Methods (Predictors)** | 6a-6c: Define predictors, measurement, blinding | ✅ | Methods 4.4, Appendix A |
| **Methods (AI Model)** | 7a-7e: Architecture, tuning, training, preprocessing | ✅ | Methods 4.4, Appendix A, Code repo |
| **Methods (Evaluation)** | 8a-8e: Validation, metrics, calibration, DCA, subgroups | ✅ | Methods 4.6 |
| **Methods (Stats)** | 9a-9d: Statistical methods, software, performance | ✅ | Methods 4.7 |
| **Results (Participants)** | 10a-10c: N, characteristics, missing data | ✅ | Results (Table 1) |
| **Results (Performance)** | 11a-11e: Discrimination, calibration, DCA, subgroups, CIs | ✅ | Results (Tables 3-7, Figures 3-7) |
| **Discussion** | 12a-12e: Interpretation, limitations, prior work, implications | ✅ | Discussion, Limitations |
| **Code/Data** | 13a-13d: Repository link, DOI, data access, version | ✅ | Declarations, GitHub repo |
| **Transparency** | 14a-14e: COI, funding, ethics, consent, AI assistance | ✅ | Declarations |
| **Reproducibility** | 15a-15e: Code, dependencies, setup, tests, docs | ✅ | GitHub repo |

---

## Appendix C: Full Subgroup Results

The following table provides extended metrics for all evaluated subgroups, supplementing Table 7 in the main manuscript.

**Supplementary Table 1. Extended Subgroup Performance Metrics**

| Subgroup | n | Prevalence (%) | AUC (95% CI) | PR-AUC (95% CI) | Brier Score | Null Brier | ECE | Net Benefit (5% threshold) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Overall** | 5,000 | 3.2% | 0.897 (0.862–0.927) | 0.546 (0.470–0.621) | 0.0340 | 0.0308 | 0.0653 | 9.43 / 1000 |
| **Age <50** | 2,507 | 2.6% | 0.883 (0.830–0.929) | 0.447 (0.334–0.569) | 0.0328 | 0.0253 | 0.0671 | 6.03 / 1000 |
| **Age 50-69** | 2,388 | 3.6% | 0.923 (0.881–0.959) | 0.651 (0.551–0.749) | 0.0341 | 0.0347 | 0.0620 | 2.91 / 1000 |
| **Age ≥70** | 105 | 7.6% | 0.798 (0.530–0.971) | 0.395 (0.134–0.751) | 0.0591 | 0.0702 | 0.1006 | 0.50 / 1000 |
| **Density A** | 506 | 2.6% | 0.858 (0.751–0.945) | 0.344 (0.143–0.597) | 0.0340 | 0.0253 | 0.0699 | 2.30 / 1000 |
| **Density B** | 2,070 | 3.0% | 0.902 (0.846–0.945) | 0.554 (0.428–0.679) | 0.0329 | 0.0291 | 0.0645 | 4.14 / 1000 |
| **Density C** | 1,942 | 3.2% | 0.904 (0.852–0.946) | 0.561 (0.435–0.686) | 0.0343 | 0.0310 | 0.0644 | 3.74 / 1000 |
| **Density D** | 482 | 4.4% | 0.873 (0.676–0.989) | 0.594 (0.245–0.932) | 0.0310 | 0.0421 | 0.0543 | -0.75 / 1000 |
| **BI-RADS 3** | 334 | 4.8% | 0.499 (0.380–0.625) | 0.049 (0.024–0.088) | 0.1169 | 0.0456 | 0.2062 | -0.02 / 1000 |
| **BI-RADS 4** | 207 | 32.4% | 0.655 (0.575–0.730) | 0.501 (0.394–0.615) | 0.3873 | 0.2189 | 0.3879 | 10.43 / 1000 |
| **Mass** | 509 | 22.0% | 0.920 (0.880–0.953) | 0.826 (0.753–0.892) | 0.1058 | 0.1716 | 0.1268 | 10.18 / 1000 |
| **Calcification** | 232 | 11.6% | 0.832 (0.742–0.905) | 0.459 (0.297–0.625) | 0.1564 | 0.1025 | 0.2078 | 3.98 / 1000 |
| **Arch. Dist.** | 37 | 27.0% | 0.579 (0.388–0.759) | 0.364 (0.191–0.574) | 0.3205 | 0.1971 | 0.3424 | 3.82 / 1000 |

*(Note: Net benefit values for subgroups are calculated using the overall cohort denominator N=5,000 to ensure they sum appropriately and are comparable across strata of different sizes).*

---

## Appendix B (cont): Code Repository

All code, data simulation scripts, evaluation pipelines, and figure generation scripts used in this study are open-source and publicly available to ensure full reproducibility.

**Repository URL:** https://github.com/bsalshreef/birads-ai-evaluation
**DOI:** 10.5281/zenodo.20821730
**License:** MIT License
**Version:** v1.0.2

The repository includes:
1. `src/data/simulate_data.py`: The exact script used to generate the 5,000-patient cohort matching VinDr-Mammo statistics.
2. `src/evaluation/run_evaluation.py`: The complete analysis pipeline computing AUC, PR-AUC, Brier score, ECE, DCA, and subgroup metrics.
3. `environment.yml`: Conda environment specification to ensure dependency version matching.
4. `figures/`: High-resolution versions of all manuscript figures.

---

## Appendix E: Sensitivity Analyses

To ensure the robustness of the combined BI-RADS+AI strategy, we conducted sensitivity analyses testing different calibration assumptions.

**E.1 Recalibrated AI Score**
We applied isotonic regression to the raw AI scores using 5-fold cross-validation. The recalibrated AI score achieved a near-perfect Brier score of 0.0301 (better than the null model 0.0308) and an ECE of 0.012. However, within BI-RADS 3, even the recalibrated AI score could not overcome the fundamental lack of discrimination (AUC 0.499), confirming that the failure in BI-RADS 3 is a discrimination failure, not merely a calibration failure.

**E.2 Bootstrap Stability**
The 95% confidence intervals for all DCA net benefit values were estimated using 2,000 bootstrap replicates. At the 5% threshold, the combined BI-RADS+AI strategy net benefit (20.79, 95% CI 18.5–23.1) remained consistently superior to AI alone (9.43, 95% CI 7.2–11.8) across 100% of bootstrap samples, confirming the statistical significance of the clinical utility advantage.
