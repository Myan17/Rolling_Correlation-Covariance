#!/usr/bin/env python3
"""
Rolling Correlation & Covariance Explorer

- Downloads historical adjusted close prices for user-provided tickers
- Converts prices to daily returns
- Computes:
    * Static correlation matrix
    * Static covariance matrix
    * Rolling correlations vs a reference asset
    * Simple PCA on covariance (risk factor intuition)
- Plots:
    * Correlation heatmap
    * Rolling correlation time series
"""

from __future__ import annotations

import sys
from typing import List, Tuple

import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt


# =========================
# Data loading and returns
# =========================

def download_prices(tickers: List[str], start: str, end: str) -> pd.DataFrame:
    """
    Download adjusted close (or close) prices for a list of tickers.

    We explicitly set auto_adjust=False so that yfinance returns an 'Adj Close'
    field like the older behavior. If that is not present, we fall back to 'Close'.
    """
    data = yf.download(
        tickers,
        start=start,
        end=end,
        progress=False,
        auto_adjust=False,  # important: keep 'Adj Close' separate
    )

    if data.empty:
        raise ValueError("No data downloaded. Check tickers and date range.")

    # yfinance usually returns a MultiIndex with top level like 'Adj Close'
    if isinstance(data.columns, pd.MultiIndex):
        # First try Adj Close
        if "Adj Close" in data.columns.get_level_values(0):
            prices = data["Adj Close"]
        elif "Close" in data.columns.get_level_values(0):
            prices = data["Close"]
        else:
            raise ValueError(
                f"Could not find 'Adj Close' or 'Close' in columns: {data.columns}"
            )
    else:
        # Single-level columns (less common)
        if "Adj Close" in data.columns:
            prices = data["Adj Close"]
        elif "Close" in data.columns:
            prices = data["Close"]
        else:
            raise ValueError(
                f"Could not find 'Adj Close' or 'Close' in columns: {data.columns}"
            )

    # Ensure a DataFrame even if there's only one ticker
    if isinstance(prices, pd.Series):
        prices = prices.to_frame()

    # Drop days where all tickers are NaN
    prices = prices.dropna(how="all")
    return prices


def compute_daily_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """
    Convert price series into simple daily percentage returns.

    r_t = (P_t / P_{t-1}) - 1

    Correlations and covariances should always be computed on returns,
    not raw prices.
    """
    returns = prices.pct_change().dropna(how="all")
    return returns


# =========================
# Correlation / covariance
# =========================

def compute_static_correlation(returns: pd.DataFrame) -> pd.DataFrame:
    """Full-sample Pearson correlation matrix."""
    return returns.corr()


def compute_static_covariance(returns: pd.DataFrame) -> pd.DataFrame:
    """Full-sample covariance matrix."""
    return returns.cov()


def compute_rolling_correlation(
    returns: pd.DataFrame,
    ref_ticker: str,
    window: int = 60,
) -> pd.DataFrame:
    """
    Rolling correlations between a reference ticker and all others.

    For each day t, correlation is computed over the previous `window` days.
    This shows how relationships change over time (regime shifts, crises, etc.).
    """
    if ref_ticker not in returns.columns:
        raise ValueError(f"Reference ticker {ref_ticker!r} not found in returns columns")

    rolling_corrs = pd.DataFrame(index=returns.index)

    for ticker in returns.columns:
        if ticker == ref_ticker:
            continue

        series = (
            returns[ref_ticker]
            .rolling(window=window)
            .corr(returns[ticker])
        )
        rolling_corrs[ticker] = series

    # drop early rows where all correlations are NaN
    return rolling_corrs.dropna(how="all")


# =========================
# PCA on covariance
# =========================

def pca_from_covariance(cov: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    """
    Simple PCA on covariance matrix.

    Returns:
        eigenvalues (sorted descending),
        eigenvectors (columns correspond to eigenvalues).
    """
    vals, vecs = np.linalg.eigh(cov.values)
    idx = np.argsort(vals)[::-1]
    eigenvalues = vals[idx]
    eigenvectors = vecs[:, idx]
    return eigenvalues, eigenvectors


def print_pca_summary(
    eigenvalues: np.ndarray,
    eigenvectors: np.ndarray,
    asset_names: List[str],
    max_factors: int = 3,
) -> None:
    """Print variance explained and first factor loadings."""
    total_var = float(eigenvalues.sum())
    frac_var = eigenvalues / total_var

    print("\n--- PCA on Covariance Matrix (Risk Factors) ---")
    print("Eigenvalues (variance explained by each factor):")
    print(np.round(eigenvalues, 6))

    print("\nFraction of total variance explained by top factors:")
    for i in range(min(max_factors, len(frac_var))):
        print(f"  Factor {i+1}: {frac_var[i]:.2%}")

    print("\nFirst principal component loadings (Factor 1):")
    first_vec = eigenvectors[:, 0]
    for name, loading in zip(asset_names, first_vec):
        print(f"  {name}: {loading:.3f}")


# =========================
# Plotting helpers
# =========================

def plot_correlation_heatmap(corr: pd.DataFrame, title: str = "Correlation Matrix") -> None:
    """Static correlation heatmap."""
    fig, ax = plt.subplots(figsize=(8, 6))

    cax = ax.imshow(corr.values, vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.columns)))
    ax.set_xticklabels(corr.columns, rotation=45, ha="right")
    ax.set_yticklabels(corr.columns)
    ax.set_title(title)

    fig.colorbar(cax, ax=ax, label="Correlation")

    plt.tight_layout()
    plt.show()


def plot_rolling_correlations(
    rolling_corrs: pd.DataFrame,
    ref_ticker: str,
    window: int,
    title: str | None = None,
) -> None:
    """Line plot of rolling correlations vs reference ticker."""
    if title is None:
        title = f"{window}-Day Rolling Correlation vs {ref_ticker}"

    fig, ax = plt.subplots(figsize=(10, 6))

    for col in rolling_corrs.columns:
        ax.plot(rolling_corrs.index, rolling_corrs[col], label=f"{ref_ticker}-{col}")

    ax.axhline(0.0, linestyle="--")
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Correlation")
    ax.legend(loc="best")

    plt.tight_layout()
    plt.show()


# =========================
# CLI main
# =========================

def main() -> None:
    """
    Interactive CLI entrypoint:

    - Asks for tickers, date range, reference ticker, window
    - Downloads prices
    - Computes returns, correlation, covariance, rolling correlations, PCA
    - Prints matrices + PCA summary and shows plots
    """
    print("=== Rolling Correlation & Covariance Explorer ===")

    tickers_input = input("Enter tickers (space-separated, e.g. AAPL MSFT GOOG): ").strip()
    tickers = tickers_input.split()

    if len(tickers) < 2:
        print("ERROR: Please provide at least 2 tickers.")
        sys.exit(1)

    start = input("Enter START date (YYYY-MM-DD): ").strip()
    end = input("Enter END date   (YYYY-MM-DD): ").strip()

    ref_ticker = input(
        f"Enter reference ticker for rolling correlations [{tickers[0]}]: "
    ).strip()
    if not ref_ticker:
        ref_ticker = tickers[0]

    window_str = input("Rolling window in days [60]: ").strip()
    try:
        window = int(window_str) if window_str else 60
    except ValueError:
        print("WARN: Invalid window, using default 60.")
        window = 60

    # --- Download prices and compute returns ---
    prices = download_prices(tickers, start, end)
    returns = compute_daily_returns(prices)

    # --- Static correlation & covariance ---
    corr = compute_static_correlation(returns)
    cov = compute_static_covariance(returns)

    print("\n--- Static Correlation Matrix ---")
    print(corr.round(3))

    print("\n--- Static Covariance Matrix ---")
    print(cov.round(6))

    # --- Rolling correlations ---
    rolling_corrs = compute_rolling_correlation(returns, ref_ticker, window)

    # --- PCA ---
    eigenvalues, eigenvectors = pca_from_covariance(cov)
    print_pca_summary(eigenvalues, eigenvectors, list(cov.columns))

    # --- Plots ---
    plot_correlation_heatmap(corr, title="Static Correlation Matrix")
    plot_rolling_correlations(rolling_corrs, ref_ticker=ref_ticker, window=window)

    print(
        """
How this helps you as a quant
-----------------------------
- Correlation matrix  -> how assets move together on average.
- Rolling correlation -> how those relationships change over time (regimes).
- Covariance matrix   -> core input to portfolio variance / optimization.
- PCA on covariance   -> first taste of factor/risk decomposition.
"""
    )


if __name__ == "__main__":
    main()
