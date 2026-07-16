# CAI Platform: Certification-Occupant Alignment Analysis & Optimization

**Research Tool for Building Science, Policy, and Design**

Analyze how well building certification systems (LEED, WELL, BREEAM, etc.) align with occupant priorities. Measure misalignment, visualize gaps, and predict optimal point reallocations.

---

## 📋 What Is CAI?

**Certification-Occupant Alignment (CAI)** measures how well building certification systems allocate credit points toward the indoor environmental quality (IEQ) factors that occupants actually complain about.

**Example finding:** LEED allocates 0.9% of points to acoustics, but 54% of occupants report dissatisfaction with acoustic comfort. This −53.1% gap indicates systematic misalignment.

---

## 🎯 Use Cases

1. **Research:** Analyze whether green certifications deliver on occupant well-being promises
2. **Policy:** Advocate for reweighting certification credits toward occupant priorities
3. **Design:** Understand which IEQ factors to prioritize in building design
4. **Validation:** Compare multiple certification systems to identify best practices

---

## 🚀 Quick Start

### Option 1: Web App (Easiest)
```bash
pip install streamlit pandas scipy matplotlib seaborn
streamlit run app_streamlit.py
```
Then open your browser to `http://localhost:8501`

### Option 2: CLI Tool
```bash
python cai_cli.py analyze \
  --cert-file data/certification_points.csv \
  --occupant-file data/occupant_data.json

python cai_cli.py predict \
  --cert-file data/certification_points.csv \
  --occupant-file data/occupant_data.json \
  --system LEED \
  --version v5 \
  --target-tau 0.5
```

### Option 3: Jupyter Notebook
```bash
jupyter notebook CAI_Interactive_Analysis.ipynb
```

### Option 4: Python Library
```python
from cai_core import CAIAnalyzer, CAIOptimizer
import pandas as pd

# Load data
cert_data = pd.read_csv('data/certification_points.csv')
occupant_data = {'Acoustics': 54, 'Thermal': 39, 'Lighting': 26, 'Air': 20}

# Analyze
analyzer = CAIAnalyzer(cert_data, occupant_data)
results = analyzer.analyze()

# Predict
optimizer = CAIOptimizer(cert_data, occupant_data, 'LEED', 'v5')
prediction = optimizer.predict(target_tau=0.5)
```

---

## 📊 Data Format

### Certification Data (CSV)
```csv
system,version,year,topic,points,system_total,source
LEED,v5,2025,Acoustics,1,110,USGBC Official Scorecard
LEED,v5,2025,Thermal,2,110,USGBC Official Scorecard
LEED,v5,2025,Lighting,4,110,USGBC Official Scorecard
LEED,v5,2025,Air,10,110,USGBC Official Scorecard
WELL,v2,2018,Acoustics,17,120,IWBI Official Documentation
...
```

### Occupant Data (JSON or CSV)
**JSON:**
```json
{
  "Acoustics": 54,
  "Thermal": 39,
  "Lighting": 26,
  "Air": 20
}
```

**CSV:**
```csv
topic,dissatisfaction_pct
Acoustics,54
Thermal,39
Lighting,26
Air,20
```

---

## 🔧 Core Methods

### Alignment Analysis
- **Metric:** Kendall tau-b rank correlation (τ)
  - Measures agreement between cert rankings and occupant complaint rankings
  - τ = 1: Perfect alignment
  - τ = 0: No relationship
  - τ = −1: Perfect misalignment (opposite priorities)

- **Confidence Intervals:** Bootstrap resampling (default: 1000)
  - Quantifies uncertainty in τ estimates
  - Reports 95% CI range

- **Sensitivity Analysis:** Kendall τ vs. Spearman ρ
  - Confirms findings are robust across correlation metrics
  - Identifies metric-dependent artifacts

### Trend Analysis
- Linear regression of τ vs. Year for each system
- Tests null hypothesis: H₀: slope = 0 (no trend)
- Reports p-values and R²

### Gap Analysis
```
Gap(topic) = Certification%(topic) − Occupant%(topic)
```
- Positive gap = over-allocation (cert allocates more than occupant concern warrants)
- Negative gap = under-allocation (cert allocates less than occupant concern warrants)

### Prediction & Optimization
**Method 1: Target Alignment**
- Input: Target τ value
- Output: Suggested point reallocation to achieve target
- Algorithm: Scipy L-BFGS-B constrained optimization

**Method 2: Gap-Based Reallocation**
- Input: Fraction of gap to close (0.0–1.0)
- Output: Linear reallocation toward occupant proportions
- Simpler, more interpretable approach

---

## 📁 File Structure

```
cai_platform/
├── cai_core.py                    # Core analysis/optimization engine
├── cai_cli.py                     # Command-line interface
├── app_streamlit.py               # Web app (Streamlit)
├── CAI_Interactive_Analysis.ipynb # Jupyter notebook template
├── README.md                       # This file
├── requirements.txt               # Python dependencies
└── data/
    ├── certification_points_complete.csv  # Cert data (40 versions)
    └── occupant_data.json                 # Occupant priorities
```

---

## 📖 Example Workflows

### Workflow 1: Analyze Current Alignment
```python
from cai_core import CAIAnalyzer
import pandas as pd

cert_data = pd.read_csv('data/certification_points_complete.csv')
occupant_data = {'Acoustics': 54, 'Thermal': 39, 'Lighting': 26, 'Air': 20}

analyzer = CAIAnalyzer(cert_data, occupant_data)
results = analyzer.analyze()  # Run analysis
summary = analyzer.get_summary()  # Get stats

print(f"Average alignment: τ = {summary['avg_tau']:.3f}")
print(f"Systems analyzed: {summary['n_systems']}")
```

### Workflow 2: Identify Largest Gaps
```python
gaps = analyzer.get_gaps_by_topic()

for topic, gap_info in gaps.items():
    print(f"{topic}: {gap_info['avg_gap']:+.1f}% gap")
    print(f"  Occupant: {gap_info['occupant_pct']:.0f}%")
    print(f"  Cert avg: {gap_info['cert_pct']:.1f}%")
```

### Workflow 3: Predict Optimal Reallocation
```python
from cai_core import CAIOptimizer

optimizer = CAIOptimizer(cert_data, occupant_data, 'LEED', 'v5')

# Method 1: Target a specific τ value
prediction = optimizer.predict(target_tau=0.5)

# Method 2: Close gap by percentage
suggestion = optimizer.suggest_reallocation(target_gap_reduction=0.5)
```

### Workflow 4: Compare Multiple Systems
```python
results = analyzer.analyze()

# Group by system
for system in results['System'].unique():
    system_data = results[results['System'] == system]
    avg_tau = system_data['Tau'].mean()
    print(f"{system}: avg τ = {avg_tau:.3f}")
```

---

## 📊 Output Interpretation

### Kendall τ Values
| τ Value | Interpretation |
|---------|---|
| 1.0 | Perfect alignment: cert priorities match occupant priorities |
| 0.5 | Good alignment: cert leans toward occupant priorities |
| 0.0 | No relationship: cert allocation random vs. occupant priorities |
| −0.5 | Poor alignment: cert leans opposite to occupant priorities |
| −1.0 | Perfect misalignment: cert exactly opposite to occupant priorities |

### Gap Analysis Interpretation
| Gap | Meaning | Action |
|-----|---------|--------|
| −50% | Severe under-allocation: cert allocates 50% less than occupant concern | Increase cert points for this topic |
| −10% | Moderate under-allocation | Consider increasing points |
| +10% | Moderate over-allocation: cert allocates more than occupant concern | Consider reducing points |
| +50% | Severe over-allocation | Reduce cert points for this topic |

---

## 🔬 Scientific Background

### Why Kendall τ?
1. **Non-parametric:** No assumptions about distribution
2. **Rank-based:** Appropriate for ordinal data (rankings)
3. **Interpretable:** Ranges from −1 to +1, easy to communicate
4. **Robust:** Handles ties in rankings

### Why Bootstrap?
1. **Small sample size:** With only 4 IEQ topics, sample variability is high
2. **No distributional assumptions:** Bootstrap doesn't assume normal distribution
3. **Quantifies uncertainty:** Provides confidence intervals without parametric models

### Limitations
1. **Single occupant dataset:** Findings based on one POE study (Graham et al. 2021)
2. **Proxy assumption:** Assumes occupant dissatisfaction ≈ priority (not validated)
3. **No causal validation:** Does NOT prove higher alignment → higher satisfaction
4. **Limited systems:** Covers LEED, WELL, BREEAM; other systems exist

---

## 🎓 Citation

If you use CAI Platform in research or policy work, please cite:

```bibtex
@software{cai_platform,
  title={CAI Platform: Certification-Occupant Alignment Analysis},
  author={[Your Name]},
  year={2026},
  url={https://github.com/your-repo/cai-platform}
}
```

Or in research papers:

> This analysis uses the CAI (Certification-Occupant Alignment) Platform, an open-source tool for measuring alignment between building certification priorities and occupant-identified needs (Author, 2026).

---

## 📬 Contributing & Feedback

**Want to add a new certification system?**
1. Extract point allocations from official documentation
2. Add rows to `certification_points_complete.csv`
3. Re-run analysis

**Found a bug?** [Open an issue](https://github.com)

**Have data on different occupant populations?** Submit via pull request

---

## 📜 License

MIT License. Use freely in research, policy, and commercial applications.

---

## 📚 References

- Graham, R., et al. (2021). Building occupant satisfaction: A meta-analysis of large-scale POE studies. *Building and Environment*, 198.
- Kendall, M. G. (1948). Rank correlation methods. *Journal of the Royal Statistical Society*, 75–91.
- USGBC. (2025). LEED v5 Reference Guide. U.S. Green Building Council.
- IWBI. (2018). WELL Building Standard v2. International WELL Building Institute.
- BREEAM. (2023). BREEAM International New Construction v7. BRE Global.

---

**Last Updated:** July 2026  
**Version:** 1.0.0  
**Status:** Publication-Ready
