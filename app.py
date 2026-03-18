import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

st.set_page_config(
    page_title="Primetrade Sentiment Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        header[data-testid="stHeader"] { display: none !important; }
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        .stApp { background-color: #ffffff !important; }
        .stApp * { color: #262730 !important; }
        [data-testid="stSidebar"] {
            background-color: #f0f2f6 !important;
            min-width: 550px !important;
            max-width: 550px !important;
        }
        [data-testid="stSidebar"] > div { background-color: #f0f2f6 !important; }
        [data-testid="stSidebar"] * { color: #262730 !important; }
        [data-testid="stMetric"] {
            background-color: #f0f2f6 !important;
            border-radius: 8px;
            padding: 16px !important;
        }
        [data-testid="stMetric"] * { color: #262730 !important; }
        [data-testid="stDataFrame"] { background-color: #ffffff !important; }
        [data-testid="stDataFrame"] * { color: #262730 !important; background-color: #ffffff !important; }
        iframe { color-scheme: light !important; }
        [data-baseweb="tag"] { background-color: #1a9850 !important; }
        [data-baseweb="tag"] * { color: #ffffff !important; }
        table { width: 100%; border-collapse: collapse; }
        thead tr th {
            background-color: #f0f2f6 !important;
            color: #262730 !important;
            font-size: 13px;
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        tbody tr td {
            color: #262730 !important;
            font-size: 13px;
            padding: 10px;
            border-bottom: 1px solid #eee;
        }
        tbody tr:hover { background-color: #f9f9f9; }
        .block-container {
            padding-top: 2rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }
        [data-testid="stInfo"] { background-color: #e8f5e9 !important; }
        [data-testid="stInfo"] * { color: #262730 !important; }
        div[class*="sidebar"] { background-color: #f0f2f6 !important; }
        div[class*="sidebar"] * { color: #262730 !important; }
        [data-testid="stSidebar"] .stMarkdown p { font-size: 16px !important; }
[data-testid="stSidebar"] .stMarkdown h3 { font-size: 20px !important; }
[data-testid="stSidebar"] .stMarkdown h2 { font-size: 24px !important; }
[data-testid="stSidebar"] label { font-size: 16px !important; }
[data-testid="stSidebar"] .stRadio label { font-size: 16px !important; }
[data-testid="stSidebar"] .stSlider label { font-size: 16px !important; }
[data-testid="stSidebar"] .stMultiSelect label { font-size: 16px !important; }
[data-testid="stSidebar"] .stDateInput label { font-size: 16px !important; }
[data-testid="stSidebar"] li { font-size: 15px !important; }
    </style>
""", unsafe_allow_html=True)

logo = Image.open('Image.png')
crypto = Image.open('Image.png')

col_logo, col_title = st.columns([1, 10])
with col_logo:
    st.image(crypto, width=200)
with col_title:
    st.title("Primetrade.ai - Trader Sentiment Dashboard")
    st.caption("Analyzing how Bitcoin Fear & Greed sentiment affects trader behavior on Hyperliquid")

st.markdown("---")

@st.cache_data
def load_data():
    fg = pd.read_csv('fear_greed_index.csv')
    trades = pd.read_csv('historical_data.csv')

    fg['date'] = pd.to_datetime(fg['date'])
    trades['Timestamp IST'] = pd.to_datetime(trades['Timestamp IST'], dayfirst=True)
    trades['date'] = pd.to_datetime(trades['Timestamp IST'].dt.date)

    merged = pd.merge(trades, fg[['date', 'value', 'classification']], on='date', how='inner')
    merged['is_win'] = merged['Closed PnL'] > 0
    merged['is_long'] = merged['Direction'] == 'Buy'

    daily = merged.groupby(['date', 'Account', 'classification']).agg(
        pnl=('Closed PnL', 'sum'),
        avg_trade=('Size USD', 'mean'),
        num_trades=('Trade ID', 'count'),
        total_fee=('Fee', 'sum')
    ).reset_index()

    win_rate = merged.groupby(['date', 'Account'])['is_win'].mean().reset_index()
    win_rate.columns = ['date', 'Account', 'win_rate']
    ls_ratio = merged.groupby(['date', 'Account'])['is_long'].mean().reset_index()
    ls_ratio.columns = ['date', 'Account', 'long_ratio']

    daily = daily.merge(win_rate, on=['date', 'Account'])
    daily = daily.merge(ls_ratio, on=['date', 'Account'])

    return merged, daily

merged, daily = load_data()

order = ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed']
palette = {
    'Extreme Fear': '#d73027',
    'Fear': '#fc8d59',
    'Neutral': '#fee08b',
    'Greed': '#91cf60',
    'Extreme Greed': '#1a9850'
}

st.sidebar.image(logo, width=450)
st.sidebar.markdown("## Primetrade.ai")
st.sidebar.markdown("---")
st.sidebar.markdown("### Filters")

selected_sentiments = st.sidebar.multiselect(
    "Select Sentiments",
    options=order,
    default=order
)

min_date = merged['date'].min().date()
max_date = merged['date'].max().date()
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

top_n = st.sidebar.slider("Display Top N Traders", 5, 32, 32)

st.sidebar.markdown("---")
st.sidebar.markdown("### Dataset Info")
st.sidebar.info(f"""
- **Total Trades:** {len(merged):,}
- **Unique Traders:** {merged['Account'].nunique()}
- **From:** {min_date}
- **To:** {max_date}
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### Navigation")
page = st.sidebar.radio("Go to", ["Overview", "Performance Analysis", "Trader Segments"])

filtered = merged[
    (merged['classification'].isin(selected_sentiments)) &
    (merged['date'].dt.date >= date_range[0]) &
    (merged['date'].dt.date <= date_range[1])
]

filtered_daily = daily[
    (daily['classification'].isin(selected_sentiments)) &
    (daily['date'].dt.date >= date_range[0]) &
    (daily['date'].dt.date <= date_range[1])
]

if page == "Overview":
    st.subheader("Overview")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Trades", f"{len(filtered):,}")
    col2.metric("Unique Traders", f"{filtered['Account'].nunique():,}")
    col3.metric("Total PnL", f"${filtered['Closed PnL'].sum():,.0f}")
    col4.metric("Avg Win Rate", f"{filtered['is_win'].mean()*100:.1f}%")

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### Sentiment Distribution of Trades")
        sent_counts = filtered['classification'].value_counts().reindex(order).dropna()
        fig, ax = plt.subplots(figsize=(7, 4))
        sns.barplot(x=sent_counts.index, y=sent_counts.values,
                    hue=sent_counts.index, palette=palette, legend=False, ax=ax)
        ax.set_xlabel("Sentiment")
        ax.set_ylabel("Number of Trades")
        ax.tick_params(axis='x', rotation=15)
        plt.tight_layout()
        st.pyplot(fig)

    with col_b:
        st.markdown("### Sentiment Breakdown Table")
        sent_table = filtered['classification'].value_counts().reindex(order).dropna().reset_index()
        sent_table.columns = ['Sentiment', 'Number of Trades']
        sent_table['% of Total'] = (sent_table['Number of Trades'] / len(filtered) * 100).round(1)
        st.table(sent_table)
        st.success("Traders most active during Fear, least during Extreme Fear - panic causes paralysis.")

elif page == "Performance Analysis":
    st.subheader("Performance by Market Sentiment")

    sa = filtered_daily.groupby('classification').agg(
        avg_pnl=('pnl', 'mean'),
        avg_win_rate=('win_rate', 'mean'),
        avg_trades=('num_trades', 'mean'),
        avg_long_ratio=('long_ratio', 'mean')
    ).reset_index()

    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    fig.suptitle('Trader Performance by Market Sentiment', fontsize=14, fontweight='bold')

    for (ax, col, title) in [
        (axes[0,0], 'avg_pnl', 'Average PnL ($)'),
        (axes[0,1], 'avg_win_rate', 'Average Win Rate'),
        (axes[1,0], 'avg_trades', 'Avg Number of Trades'),
        (axes[1,1], 'avg_long_ratio', 'Long Ratio')
    ]:
        filtered_order = [o for o in order if o in sa['classification'].values]
        sns.barplot(data=sa, x='classification', y=col, order=filtered_order,
                    hue='classification', palette=palette, legend=False, ax=ax)
        ax.set_title(title)
        ax.set_xlabel('')
        ax.tick_params(axis='x', rotation=15)

    plt.tight_layout()
    st.pyplot(fig)

    st.markdown("---")
    st.markdown("### Key Findings")
    st.success("Fear days yield the highest avg PnL ($5,328) - calm traders profit while others panic")
    st.warning("Greed days surprisingly underperform ($3,318) - overconfidence leads to poor decisions")
    st.error("Extreme Fear = most trades (133/day) but lowest win rate (32.9%) - panic trading hurts")

elif page == "Trader Segments":
    st.subheader("Trader Segmentation")

    trader_profile = filtered_daily.groupby('Account').agg(
        total_pnl=('pnl', 'sum'),
        avg_win_rate=('win_rate', 'mean'),
        avg_trades=('num_trades', 'mean'),
        avg_trade_size=('avg_trade', 'mean'),
        total_days=('date', 'count')
    ).reset_index()

    trader_profile['freq_segment'] = pd.qcut(trader_profile['avg_trades'], q=2,
                                              labels=['Infrequent', 'Frequent'])
    trader_profile['winner_segment'] = pd.qcut(trader_profile['avg_win_rate'], q=2,
                                                labels=['Inconsistent', 'Consistent Winner'])
    trader_profile['size_segment'] = pd.qcut(trader_profile['avg_trade_size'], q=2,
                                              labels=['Low Size', 'High Size'])

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle('Trader Segmentation Analysis', fontsize=14, fontweight='bold')

    for ax, seg, title, pal in zip(
        axes,
        ['freq_segment', 'winner_segment', 'size_segment'],
        ['Frequent vs Infrequent', 'Consistent vs Inconsistent', 'High vs Low Trade Size'],
        [{'Infrequent': '#fc8d59', 'Frequent': '#1a9850'},
         {'Inconsistent': '#fc8d59', 'Consistent Winner': '#1a9850'},
         {'Low Size': '#fc8d59', 'High Size': '#1a9850'}]
    ):
        seg_pnl = trader_profile.groupby(seg)['total_pnl'].mean().reset_index()
        sns.barplot(data=seg_pnl, x=seg, y='total_pnl',
                    hue=seg, palette=pal, legend=False, ax=ax)
        ax.set_title(f'Avg PnL\n{title}')
        ax.set_xlabel('')

    plt.tight_layout()
    st.pyplot(fig)

    st.markdown("---")
    st.markdown(f"### Top {top_n} Trader Profiles")
    st.table(
        trader_profile[['Account', 'total_pnl', 'avg_win_rate',
                         'avg_trades', 'freq_segment',
                         'winner_segment', 'size_segment']]
        .sort_values('total_pnl', ascending=False)
        .head(top_n)
        .round(2)
    )