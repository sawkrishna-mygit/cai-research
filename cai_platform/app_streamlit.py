#!/usr/bin/env python3
"""
CAI Platform Web App (Streamlit Playground)
Run with: streamlit run app_streamlit.py
"""

from pathlib import Path
import os
import json

PLATFORM_ROOT = Path(__file__).resolve().parent
os.environ.setdefault("HOME", str(PLATFORM_ROOT))
os.environ.setdefault("XDG_CACHE_HOME", str(PLATFORM_ROOT / ".cache"))
os.environ.setdefault("MPLCONFIGDIR", str(PLATFORM_ROOT / ".matplotlib"))
(PLATFORM_ROOT / ".cache").mkdir(exist_ok=True)
(PLATFORM_ROOT / ".matplotlib").mkdir(exist_ok=True)

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO
from cai_core import CAIAnalyzer, CAIOptimizer

PORTFOLIO_URL = os.environ.get(
    "CAI_PORTFOLIO_URL",
    "https://sawkrishna-mygit.github.io/cai-research/",
)

st.set_page_config(
    page_title="CAI Analysis Playground",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { padding: 2rem; }
    .portfolio-link {
        display: inline-block;
        margin-bottom: 1rem;
        padding: 0.5rem 1rem;
        background: #0b0b0b;
        color: #fbfaf6 !important;
        border-radius: 6px;
        text-decoration: none;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

st.markdown(
    f'<a class="portfolio-link" href="{PORTFOLIO_URL}" target="_self">← Back to Research Portfolio</a>',
    unsafe_allow_html=True
)

st.title("CAI Analysis Playground")
st.markdown("**Certification-Occupant Alignment — Interactive Analysis & Optimization**")

st.sidebar.title("CAI Platform")
st.sidebar.markdown("""
**Certification-Occupant Alignment (CAI)**

Research tool for measuring alignment between building certification priorities and occupant-identified indoor environmental quality needs.

*Citation:* CAI Platform (2026). Open-source alignment analysis for LEED, WELL, BREEAM, and Fitwel.
""")
mode = st.sidebar.radio("Select Mode", ["Analyze", "Predict & Optimize"])

@st.cache_data
def get_sample_data():
    cert_df = pd.read_csv(PLATFORM_ROOT / 'data' / 'certification_points_complete.csv')
    with open(PLATFORM_ROOT / 'data' / 'occupant_data.json') as f:
        occupant_data = json.load(f)
    return cert_df, occupant_data

cert_data_sample, occupant_dict_sample = get_sample_data()

if mode == "Analyze":
    st.header("Alignment Analysis")
    st.markdown("Analyze how well certification systems align with occupant priorities")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Upload Data")
        cert_file = st.file_uploader("Certification Data (CSV)", type=['csv'], key='cert_upload')
        occ_file = st.file_uploader("Occupant Data (CSV/JSON)", type=['csv', 'json'], key='occ_upload')
        use_sample = st.checkbox("Use Sample Data", value=True)

    with col2:
        st.subheader("Options")
        n_bootstrap = st.slider("Bootstrap Resamples", 100, 5000, 1000, step=100)
        show_details = st.checkbox("Show Detailed Results", value=True)

    try:
        if use_sample:
            cert_data = cert_data_sample
            occupant_data = occupant_dict_sample
            st.info("Using sample data: LEED, WELL, BREEAM, Fitwel (13 versions)")
        else:
            if cert_file and occ_file:
                cert_data = pd.read_csv(cert_file)
                if occ_file.name.endswith('.json'):
                    occupant_data = json.load(occ_file)
                else:
                    occ_df = pd.read_csv(occ_file)
                    occupant_data = dict(zip(occ_df['topic'], occ_df['dissatisfaction_pct']))
                st.success("Data loaded!")
            else:
                st.warning("Please upload files or use sample data")
                st.stop()

        if st.button("Run Analysis", key='analyze_btn'):
            with st.spinner("Analyzing alignment..."):
                analyzer = CAIAnalyzer(cert_data, occupant_data)
                results = analyzer.analyze()
                summary = analyzer.get_summary()
                gaps = analyzer.get_gaps_by_topic()

            st.success("Analysis complete!")

            st.subheader("Summary Statistics")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Systems", summary['n_systems'])
            with col2:
                st.metric("Versions", summary['n_versions'])
            with col3:
                st.metric("Avg Alignment (τ)", f"{summary['avg_tau']:.3f}")
            with col4:
                st.metric("Time Span", summary['years_span'])

            st.info(f"""
            **Interpretation:** Average τ = {summary['avg_tau']:.3f}
            - τ = 1.0: Perfect alignment (cert matches occupant priorities)
            - τ = 0.0: No relationship
            - τ = -1.0: Perfect misalignment (cert opposite to occupant priorities)
            """)

            st.subheader("Topic-Level Gaps")
            gap_df = pd.DataFrame([
                {
                    'Topic': t,
                    'Occupant%': g['occupant_pct'],
                    'Cert%': f"{g['cert_pct']:.1f}",
                    'Gap%': f"{g['avg_gap']:.1f}",
                }
                for t, g in gaps.items()
            ])
            st.dataframe(gap_df, use_container_width=True)

            st.subheader("Visualizations")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Alignment Trajectories**")
                fig, ax = plt.subplots(figsize=(10, 6))
                systems = results['System'].unique()
                colors = {'LEED': '#1f77b4', 'WELL': '#ff7f0e', 'BREEAM': '#2ca02c', 'Fitwel': '#d62728'}
                markers = {'LEED': 'o', 'WELL': 's', 'BREEAM': '^', 'Fitwel': 'D'}

                for system in systems:
                    system_data = results[results['System'] == system].sort_values('Year')
                    ax.errorbar(system_data['Year'], system_data['Tau'],
                               yerr=[system_data['Tau'] - system_data['CI_Lower'],
                                     system_data['CI_Upper'] - system_data['Tau']],
                               fmt=markers.get(system, 'o'), color=colors.get(system, '#666666'), markersize=8,
                               capsize=4, capthick=2, label=system, alpha=0.8)

                ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5, alpha=0.5)
                ax.set_xlabel('Year')
                ax.set_ylabel('Kendall τ')
                ax.set_title('Alignment Over Time')
                ax.legend()
                ax.grid(True, alpha=0.3)
                st.pyplot(fig)

            with col2:
                st.markdown("**Topic Gaps (Latest Versions)**")
                latest = results.loc[results.groupby('System')['Year'].idxmax()]

                fig, axes = plt.subplots(1, min(4, len(latest)), figsize=(14, 4))
                if len(latest) == 1:
                    axes = [axes]

                for ax, (_, row) in zip(axes, latest.iterrows()):
                    topics = list(occupant_data.keys())
                    gaps_vals = [row[f'{t}_gap'] for t in topics]
                    colors_gap = ['#d62728' if g > 0 else '#1f77b4' for g in gaps_vals]

                    x_pos = np.arange(len(topics))
                    ax.barh(x_pos, gaps_vals, color=colors_gap, alpha=0.7)
                    ax.set_yticks(x_pos)
                    ax.set_yticklabels(topics)
                    ax.set_xlabel('Gap (%)')
                    ax.set_title(f"{row['System']} {row['Version']}")
                    ax.axvline(x=0, color='black', linestyle='-', linewidth=1)
                    ax.grid(True, alpha=0.3, axis='x')

                plt.suptitle('Topic-Level Gaps')
                st.pyplot(fig)

            if show_details:
                st.subheader("Detailed Results Table")
                display_cols = ['System', 'Version', 'Year', 'Tau', 'CI_Lower', 'CI_Upper',
                               'Spearman_Rho', 'Acoustics_pct', 'Thermal_pct', 'Lighting_pct', 'Air_pct']
                st.dataframe(results[display_cols], use_container_width=True)

            st.subheader("Download Results")
            csv = results.to_csv(index=False)
            st.download_button(
                label="Download Full Results (CSV)",
                data=csv,
                file_name="cai_analysis_results.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"Error: {e}")

else:
    st.header("Prediction & Optimization")
    st.markdown("Find optimal certification point allocations to improve alignment")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Select System")
        use_sample = st.checkbox("Use Sample Data", value=True, key='sample_predict')

        if use_sample:
            cert_data = cert_data_sample
            occupant_data = occupant_dict_sample

            system = st.selectbox("Certification System", cert_data['system'].unique())
            version = st.selectbox("Version", cert_data[cert_data['system'] == system]['version'].unique())
        else:
            st.warning("Upload data to use custom certification system")
            st.stop()

    with col2:
        st.subheader("Optimization Target")
        optimization_method = st.radio(
            "Method",
            ["Target Alignment (τ)", "Close Gap %"]
        )

        if optimization_method == "Target Alignment (τ)":
            target_tau = st.slider("Target τ", -1.0, 1.0, 0.0, 0.1)
        else:
            gap_reduction = st.slider("Close this % of gap", 0.0, 1.0, 0.5, 0.1)

    if st.button("Optimize", key='predict_btn'):
        with st.spinner("Optimizing..."):
            optimizer = CAIOptimizer(cert_data, occupant_data, system, version)

            if optimization_method == "Target Alignment (τ)":
                result = optimizer.predict(target_tau=target_tau)

                st.subheader("Optimization Results")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Current τ", f"{result['current_tau']:.3f}")
                with col2:
                    st.metric("Optimized τ", f"{result['optimized_tau']:.3f}")
                with col3:
                    st.metric("Improvement", f"{result['tau_improvement']:+.3f}")

            else:
                result = optimizer.suggest_reallocation(target_gap_reduction=gap_reduction)

                st.subheader("Suggested Reallocation")
                st.info(f"Closing {gap_reduction*100:.0f}% of the gap toward occupant priorities")

        realloc_df = pd.DataFrame([
            {
                'Topic': topic,
                'Current Points': result['current_allocation'][topic],
                'New Points': result['optimized_allocation'][topic] if optimization_method == "Target Alignment (τ)" else result['suggested_allocation'][topic],
                'Change %': f"{result['percent_change'][topic]:+.0f}%"
            }
            for topic in result['topics']
        ])

        st.dataframe(realloc_df, use_container_width=True)

        st.subheader("Reallocation Visualization")
        topics = result['topics']
        current = [result['current_allocation'][t] for t in topics]
        new = [result['optimized_allocation'][t] if optimization_method == "Target Alignment (τ)" else result['suggested_allocation'][t] for t in topics]

        fig, ax = plt.subplots(figsize=(10, 5))
        x = np.arange(len(topics))
        width = 0.35

        ax.bar(x - width/2, current, width, label='Current', alpha=0.8)
        ax.bar(x + width/2, new, width, label='Optimized', alpha=0.8)

        ax.set_ylabel('Points')
        ax.set_title(f'{system} {version} - Point Reallocation')
        ax.set_xticks(x)
        ax.set_xticklabels(topics)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        st.pyplot(fig)

        st.subheader("Export Recommendation")
        rec_json = json.dumps(result, indent=2, default=str)
        st.download_button(
            label="Download Recommendation (JSON)",
            data=rec_json,
            file_name=f"cai_optimization_{system}_{version}.json",
            mime="application/json"
        )

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
### Links
[Research Portfolio]({PORTFOLIO_URL})

### About
Open-source CAI analysis for building science, policy, and design research.
""")
