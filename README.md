# Primetrade.ai — Trader Sentiment Analysis

## Overview
This project analyzes how Bitcoin market sentiment (Fear/Greed Index) 
relates to trader behavior and performance on Hyperliquid, 
a decentralized perpetual futures exchange.

## Project Structure
- `app.py` — Streamlit dashboard
- `primetrade.ipynb` — Analysis notebook
- `fear_greed_index.csv` — Bitcoin Fear/Greed dataset
- `historical_data.csv` — Hyperliquid trader dataset
- `sentiment_performance.png` — Performance chart
- `segmentation.png` — Segmentation chart

## Setup & How to Run

### 1. Install dependencies
pip install pandas seaborn matplotlib streamlit Pillow

### 2. Run the Streamlit dashboard
streamlit run app.py

### 3. Or open the notebook
Open primetrade.ipynb in Jupyter or VS Code

## Datasets
| Dataset | Rows | Description |
|---|---|---|
| fear_greed_index.csv | 2,644 | Daily Bitcoin Fear/Greed classification |
| historical_data.csv | 211,224 | Hyperliquid trader transaction history |

- Overlapping date range: May 2023 to May 2025

## Key Insights
1. Fear days yield the highest avg PnL ($5,328) — calm traders profit while others panic
2. Extreme Fear causes panic trading — most trades (133/day) but lowest win rate (32.9%)
3. Frequent traders earn significantly more (~$385k vs ~$258k for infrequent traders)

## Strategy Recommendations
1. Trade more during Fear days, keep sizes conservative
2. Be selective and cautious during Greed days — fewer, quality trades win

## Bonus
Interactive Streamlit dashboard for exploring results visually.