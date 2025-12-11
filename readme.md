# Rolling Correlation & Covariance Explorer

This project analyzes **how assets move together over time**, using statistical tools that form the foundation of modern quantitative finance and portfolio construction.  
It is designed as the second project in the Quant Roadmap after *Daily Returns & Volatility Analyzer*.

---

## 📌 Project Overview

This tool:

- Downloads historical price data for multiple assets  
- Converts prices to daily returns  
- Computes:
  - **Static Correlation Matrix**
  - **Static Covariance Matrix**
  - **Rolling Correlations** between a reference ticker and others
  - **PCA (Principal Component Analysis)** on the covariance matrix  
- Generates:
  - Correlation heatmap  
  - Rolling correlation time-series plot  
  - PCA factor loadings

This project teaches you how to interpret **inter-asset relationships**, **regime changes**, and **common risk factors**, all of which are essential for hedge fund work.

---

## 📈 Key Results From This Run

### **Tickers Used:**  
`META`, `NVDA`, `SPY`  
**Date Range:** Jan 1, 2024 → Jan 1, 2025  
**Rolling Window:** 60 days  
**Reference Ticker:** `META`

---

## 🔷 Static Correlation Matrix

This shows how closely assets moved together over the entire period.

| Ticker | META  | NVDA  | SPY   |
|--------|-------|-------|-------|
| META   | 1.000 | 0.382 | 0.530 |
| NVDA   | 0.382 | 1.000 | 0.635 |
| SPY    | 0.530 | 0.635 | 1.000 |

### Interpretation

- **META–SPY correlation (0.53)** → META moves moderately with the overall market.  
- **NVDA–SPY correlation (0.64)** → NVDA moves strongly with the market.  
- **META–NVDA correlation (0.38)** → Lower relationship → some diversification potential.  
- All correlations are **positive**, meaning no natural hedge pairs in this set.

---

## 🔶 Static Covariance Matrix

Covariance is the *raw*, unscaled measure of how two assets move together.

| Ticker | META | NVDA | SPY |
|--------|----------|----------|----------|
| META | 0.000528 | 0.000291 | 0.000096 |
| NVDA | 0.000291 | 0.001094 | 0.000167 |
| SPY  | 0.000096 | 0.000167 | 0.000063 |

### Interpretation

- **NVDA has the largest variance** → expected: it's a high-beta growth stock.  
- **SPY has the smallest variance** → broad market ETF → lowest volatility.  
- Covariance values are all positive, reinforcing the correlation analysis.


---

## 🧠 PCA (Principal Component Analysis) on Covariance

PCA decomposes asset returns into **underlying risk factors**.  
Eigenvalues show how much variance each factor explains.

### **Eigenvalues**

### **Variance Explained**
- **Factor 1:** 74.04%  
- **Factor 2:** 24.15%  
- **Factor 3:** 1.81%  

### Interpretation

- **Factor 1 explains ~74% of ALL risk.**  
  → Strong common driver (macro conditions, market sentiment).

- **Factor 2 explains ~24%.**  
  → Likely related to sector-specific behaviors (e.g., AI/tech vs market).

- **Factor 3 is noise.**

### **First Principal Component Loadings (Factor 1)**

| Asset | Loading |
|-------|---------|
| META | -0.388 |
| NVDA | -0.908 |
| SPY  | -0.159 |

### Interpretation

- **NVDA has the strongest exposure to the dominant risk factor**, meaning it moves most with the market-wide risk driver.  
- META has moderate exposure.  
- SPY has the smallest loading (most diversified basket).

This is your first introduction to **risk-factor modeling**, used in portfolio construction, risk parity, and multi-factor investing.

---

## 📉 Rolling Correlation Analysis

Rolling correlations reveal **regime changes**—how relationships evolve over time.

Examples you would see in the plot:

- Correlations tightening during high-volatility periods  
- NVDA’s correlation with SPY spiking → typical during market stress  
- META & NVDA correlations drifting → sector rotation effects  

This real-time movement is why risk managers never rely only on static correlation.

---

## 🧩 Why This Project Matters (Quant Career Relevance)

This project teaches key concepts used daily in quant roles:

- **Covariance** → required for portfolio variance, Sharpe optimization, efficient frontier  
- **Correlation** → diversification, clustering, regime detection  
- **Rolling correlations** → understanding time-varying market structure  
- **PCA** → risk decomposition, factor extraction, hedge ratio intuition  

By completing it, you're now able to:

- Diagnose diversification breakdown  
- Identify dominant market factors  
- Understand cross-asset dependencies  
- Build the foundation for  
  - Sharpe Ratio Optimizer  
  - Efficient Frontier  
  - Risk Parity  
  - VaR / ES  
  - CAPM & Factor Models

---

## 🏃‍♂️ How to Run the Project

```bash
cd rolling_corr_cov
source .venv/bin/activate
python3 rolling_corr_cov.py
