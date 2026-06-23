# Appendix A: Data Simulation Methodology

This document outlines the statistical assumptions and methodology used to generate the simulated dataset for the BI-RADS anchored AI evaluation framework.

## 1. Objective

Because publicly available datasets (such as VinDr-Mammo) do not provide both radiologist-assigned BI-RADS assessments and calibrated continuous AI risk scores suitable for deployment, we simulated a dataset of $N=5,000$ screening mammography examinations. The goal was to exactly reproduce the published statistical properties of the VinDr-Mammo dataset while introducing a realistic, slightly miscalibrated AI risk score to test the evaluation framework.

## 2. Demographic and Clinical Variables

The simulation matched the following published distributions:

### 2.1 BI-RADS Categories
- BI-RADS 1: ~65%
- BI-RADS 2: ~23%
- BI-RADS 3: ~7%
- BI-RADS 4: ~4%
- BI-RADS 5: ~1%

### 2.2 Breast Density
- Density A: ~10%
- Density B: ~40%
- Density C: ~40%
- Density D: ~10%

### 2.3 Age
- Mean: 50 years
- Standard Deviation: 10 years
- Range clipped to: [25, 80] years

### 2.4 Lesion Types
Assigned probabilistically based on BI-RADS category:
- BI-RADS 1: No Finding (100%)
- BI-RADS 2: No Finding (70%), Mass (20%), Calcification (10%)
- BI-RADS 3: Mass (45%), Focal Asymmetry (30%), Calcification (15%), No Finding (10%)
- BI-RADS 4: Mass (50%), Calcification (25%), Architectural Distortion (15%), Focal Asymmetry (10%)
- BI-RADS 5: Mass (60%), Calcification (25%), Architectural Distortion (15%)

## 3. Cancer Outcomes

Cancer prevalence was anchored to realistic positive predictive values (PPV) per BI-RADS category to achieve an overall prevalence of ~3.2%:
- BI-RADS 1: 0.5%
- BI-RADS 2: 1.0%
- BI-RADS 3: 5.0%
- BI-RADS 4: 35.0%
- BI-RADS 5: 90.0%

*Note: In the simulation, outcome status and predictor values were generated concurrently; blinding was inherently maintained during model evaluation as the evaluation scripts had no access to the data generation parameters.*

## 4. AI Risk Score Generation

The continuous AI score was generated using a logistic model with added Gaussian noise to achieve a target global AUC of ~0.89.

1. **Base Log-Odds:** Derived from BI-RADS category, density, and age.
2. **Noise:** $\mathcal{N}(0, 1.1)$ added to simulate model uncertainty.
3. **Miscalibration:** The log-odds were systematically shifted (`log_odds * 0.82 + 0.35`) before applying the sigmoid function. This creates an overconfident model at low probabilities (intercept shift), deliberately introducing calibration errors (especially in BI-RADS 3 and 4) to demonstrate the framework's ability to detect them.

## 5. Reproducibility

The complete generation script is available in `src/data/simulate_data.py`. Random seeds are fixed (`np.random.seed(42)`) to ensure the exact same dataset is generated across different environments.
