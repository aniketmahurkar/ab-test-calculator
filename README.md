# ab-test-calculator

**Statistical rigor for your experiments — no spreadsheet required.**

A Streamlit app for A/B test analysis: significance testing, sample size estimation, and power analysis.

## Features

| Tab | What it does |
|-----|-------------|
| **Significance Test** | Two-proportion z-test with confidence intervals and lift calculation |
| **Sample Size Calculator** | How many visitors you need for a given MDE, power, and significance level |
| **Power Analysis** | What power your current sample size achieves, with interactive power curve |

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501`.

## The Math

### Significance Test (Two-Proportion Z-Test)

```
z = (p_B - p_A) / sqrt(p_pool * (1 - p_pool) * (1/n_A + 1/n_B))
```

Where `p_pool = (x_A + x_B) / (n_A + n_B)`.

### Sample Size

```
n = ((z_α * sqrt(2*p₁*(1-p₁)) + z_β * sqrt(p₁*(1-p₁) + p₂*(1-p₂))) / (p₂ - p₁))²
```

### Power

Given a fixed sample size, computes the probability of detecting the specified effect.

## When to Use

- **Before** an experiment: use Sample Size Calculator to plan duration
- **During** an experiment: use Power Analysis to check if you have enough data
- **After** an experiment: use Significance Test to evaluate results

## License

MIT
