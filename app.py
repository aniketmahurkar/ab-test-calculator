"""A/B Test Calculator — Power analysis, significance testing, sample size estimation."""
import streamlit as st
import numpy as np
from scipy import stats

st.set_page_config(page_title="A/B Test Calculator", page_icon="🧪", layout="wide")
st.title("🧪 A/B Test Calculator")

tab1, tab2, tab3 = st.tabs(["Significance Test", "Sample Size Calculator", "Power Analysis"])

# --- Tab 1: Significance Testing ---
with tab1:
    st.header("Test Results — Is it significant?")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Control (A)")
        visitors_a = st.number_input("Visitors", value=10000, min_value=1, key="va")
        conversions_a = st.number_input("Conversions", value=500, min_value=0, key="ca")

    with col2:
        st.subheader("Variant (B)")
        visitors_b = st.number_input("Visitors", value=10000, min_value=1, key="vb")
        conversions_b = st.number_input("Conversions", value=550, min_value=0, key="cb")

    alpha = st.slider("Significance level (α)", 0.01, 0.10, 0.05, 0.01, key="alpha1")

    if st.button("Run Test", key="run_sig"):
        rate_a = conversions_a / visitors_a
        rate_b = conversions_b / visitors_b
        lift = (rate_b - rate_a) / rate_a * 100

        # Two-proportion z-test
        p_pool = (conversions_a + conversions_b) / (visitors_a + visitors_b)
        se = np.sqrt(p_pool * (1 - p_pool) * (1/visitors_a + 1/visitors_b))
        z_stat = (rate_b - rate_a) / se
        p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))

        # Confidence interval
        se_diff = np.sqrt(rate_a*(1-rate_a)/visitors_a + rate_b*(1-rate_b)/visitors_b)
        z_crit = stats.norm.ppf(1 - alpha/2)
        ci_low = (rate_b - rate_a) - z_crit * se_diff
        ci_high = (rate_b - rate_a) + z_crit * se_diff

        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("Lift", f"{lift:+.2f}%")
        c2.metric("P-value", f"{p_value:.4f}")
        c3.metric("Z-statistic", f"{z_stat:.3f}")

        if p_value < alpha:
            st.success(f"✅ Statistically significant (p={p_value:.4f} < α={alpha})")
        else:
            st.warning(f"⚠️ Not significant (p={p_value:.4f} ≥ α={alpha})")

        st.caption(f"95% CI for difference: [{ci_low*100:.3f}%, {ci_high*100:.3f}%]")
        st.caption(f"Control rate: {rate_a*100:.2f}% | Variant rate: {rate_b*100:.2f}%")

# --- Tab 2: Sample Size Calculator ---
with tab2:
    st.header("How many visitors do you need?")

    baseline_rate = st.number_input("Baseline conversion rate (%)", value=5.0, min_value=0.1, max_value=99.0, step=0.1) / 100
    mde = st.number_input("Minimum detectable effect (%)", value=10.0, min_value=0.1, step=0.5) / 100
    alpha2 = st.slider("Significance level (α)", 0.01, 0.10, 0.05, 0.01, key="alpha2")
    power = st.slider("Power (1-β)", 0.70, 0.99, 0.80, 0.01)

    variant_rate = baseline_rate * (1 + mde)
    z_alpha = stats.norm.ppf(1 - alpha2/2)
    z_beta = stats.norm.ppf(power)

    # Sample size formula for two-proportion test
    p1, p2 = baseline_rate, variant_rate
    n = ((z_alpha * np.sqrt(2 * p1 * (1-p1)) + z_beta * np.sqrt(p1*(1-p1) + p2*(1-p2))) / (p2 - p1)) ** 2
    n = int(np.ceil(n))

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Sample size per variant", f"{n:,}")
    c2.metric("Total visitors needed", f"{n*2:,}")
    c3.metric("Variant rate target", f"{variant_rate*100:.2f}%")

    # Duration estimate
    daily_traffic = st.number_input("Daily traffic (visitors/day)", value=1000, min_value=1)
    days_needed = int(np.ceil(n * 2 / daily_traffic))
    st.info(f"📅 At {daily_traffic:,} visitors/day, you need **{days_needed} days** to reach significance.")

# --- Tab 3: Power Analysis ---
with tab3:
    st.header("What's the power of your current test?")

    n_power = st.number_input("Sample size per variant", value=5000, min_value=100)
    baseline_power = st.number_input("Baseline rate (%)", value=5.0, min_value=0.1, max_value=99.0, step=0.1, key="bp") / 100
    effect_power = st.number_input("Expected effect size (%)", value=10.0, min_value=0.1, step=0.5, key="ep") / 100
    alpha3 = st.slider("Significance level (α)", 0.01, 0.10, 0.05, 0.01, key="alpha3")

    p1_pw = baseline_power
    p2_pw = baseline_power * (1 + effect_power)
    se_pw = np.sqrt(p1_pw*(1-p1_pw)/n_power + p2_pw*(1-p2_pw)/n_power)
    z_alpha_pw = stats.norm.ppf(1 - alpha3/2)
    z_power = (abs(p2_pw - p1_pw) - z_alpha_pw * se_pw) / se_pw
    achieved_power = stats.norm.cdf(z_power)

    st.divider()
    st.metric("Achieved Power", f"{achieved_power*100:.1f}%")

    if achieved_power >= 0.80:
        st.success("✅ Adequate power (≥80%). Your test can reliably detect this effect.")
    else:
        st.warning(f"⚠️ Underpowered ({achieved_power*100:.1f}% < 80%). Consider increasing sample size.")

    # Power curve
    st.subheader("Power Curve")
    effects = np.linspace(0.01, 0.30, 50)
    powers = []
    for eff in effects:
        p2_c = baseline_power * (1 + eff)
        se_c = np.sqrt(p1_pw*(1-p1_pw)/n_power + p2_c*(1-p2_c)/n_power)
        z_c = (abs(p2_c - p1_pw) - z_alpha_pw * se_c) / se_c
        powers.append(stats.norm.cdf(z_c))

    import pandas as pd
    chart_df = pd.DataFrame({"Effect Size (%)": effects*100, "Power": powers})
    st.line_chart(chart_df, x="Effect Size (%)", y="Power")
