import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Retirement Tax Optimizer", layout="wide")

# -----------------------------
# TITLE
# -----------------------------
st.title("📊 Retirement Tax Optimizer for High-Income Professionals")

st.markdown("""
Plan your retirement, reduce taxes, and optimize Roth conversions.
Built for high-income professionals approaching retirement.
""")

st.header("Why Tax Planning Matters in Retirement")

st.subheader("🔹 Social Security Is Often Taxable")
st.write("""
Many people assume Social Security benefits are tax-free — this is not true.

Up to **85% of your Social Security income can be taxable**, depending on your total income.

If you have:
- withdrawals from retirement accounts  
- capital gains  
- Roth conversions  

These can push you into higher tax levels and make more of your Social Security taxable.

👉 Poor planning can lead to significantly higher taxes in retirement.
""")

st.subheader("🔹 IRMAA: The Hidden Medicare Cost")
st.write("""
IRMAA (Income-Related Monthly Adjustment Amount) is a **stealth tax** on retirees.

If your income exceeds certain thresholds, your Medicare premiums increase significantly.

Examples:
- Crossing a threshold by just $1 can increase premiums by **thousands per year**
- Applies to both spouses

Common triggers:
- Large Roth conversions  
- RMD withdrawals  
- Capital gains  

👉 Many retirees overpay Medicare simply because they didn't plan their income levels.
""")

st.subheader("🔹 RMD: Mandatory Withdrawals = Mandatory Taxes")
st.write("""
At age **73**, the IRS requires you to take withdrawals from pre-tax accounts.

These are called Required Minimum Distributions (RMDs), and they:

- Are fully taxable as ordinary income  
- Cannot be avoided  
- Can push you into higher tax brackets  

For large balances, RMDs can be **$100K+ per year**, even if you don't need the money.

👉 Without planning, RMDs can trigger:
- higher tax brackets  
- higher Medicare premiums (IRMAA)  
- more Social Security taxation  
""")

st.subheader("⚠ Why These Factors Compound Each Other")

st.write("""
These three factors do not act independently — they interact and compound.

For example:
- RMD increases income →
- pushes you into higher tax bracket →
- causes more Social Security to be taxable →
- triggers IRMAA premiums

👉 This creates a chain reaction of higher taxes.

Without planning, retirees often:
- pay significantly more lifetime tax than necessary  
- lose flexibility  
""")

st.subheader("✅ How Smart Planning Reduces Taxes")

st.write("""
With proper planning, you can:

✅ Convert pre-tax money to Roth at lower tax rates  
✅ Reduce future RMDs  
✅ Keep income below IRMAA thresholds  
✅ Preserve tax-free income sources  
✅ Increase after-tax wealth  

The most valuable strategy is typically:

👉 Controlled Roth conversions between ages **65–70**
(when income is temporarily lower)
""")

st.subheader("📈 Get Your Personalized Strategy")

st.write("""
Your optimal strategy depends on your exact situation.

Use this tool to explore your plan — or request a personalized analysis.
""")

st.info("👉 Want a detailed tax optimization plan? Contact us for a personalized report.")

# -----------------------------
# SIDEBAR INPUTS
# -----------------------------
st.sidebar.header("Your Inputs")

age = st.sidebar.slider("Current Age", 40, 70, 60)
retire_age = st.sidebar.slider("Retirement Age", 50, 75, 65)

pretax = st.sidebar.number_input("Pre-tax Balance ($)", value=500000)
roth = st.sidebar.number_input("Roth Balance ($)", value=200000)
taxable = st.sidebar.number_input("Taxable Balance ($)", value=500000)

income_now = st.sidebar.number_input("Current AGI ($)", value=100000)
retirement_income = st.sidebar.number_input("Retirement Income ($)", value=50000)

spend = st.sidebar.number_input("Annual Spending ($)", value=50000)

return_rate = st.sidebar.slider("Expected Return (%)", 3, 10, 6) / 100
volatility = st.sidebar.slider("Volatility (%)", 5, 20, 11) / 100

conversion_cap = st.sidebar.slider("Max Roth Conversion", 0, 200000, 120000)

simulations = st.sidebar.slider("Simulations", 50, 500, 200)

# -----------------------------
# SIMULATION FUNCTION
# -----------------------------
def run_sim():
    pretax_val = pretax
    roth_val = roth
    taxable_val = taxable
    
    wealth = []
    
    for yr in range(30):
        age_now = age + yr
        
        r = np.random.normal(return_rate, volatility)
        
        pretax_val *= (1 + r)
        roth_val *= (1 + r)
        taxable_val *= (1 + r)
        
        income = 0
        
        # Income logic
        if age_now < retire_age:
            income += income_now
        else:
            income += retirement_income
        
        # Social Security
        if age_now >= 70:
            income += 40000 * 1.24 * 0.85
        
        # Conversion (65–73 window)
        if retire_age <= age_now < 73:
            convert = min(conversion_cap, pretax_val)
            pretax_val -= convert
            roth_val += convert
            income += convert
        
        # RMD
        if age_now >= 73:
            divisor = max(27.4 - (age_now - 73), 10)
            rmd = pretax_val / divisor
            pretax_val -= rmd
            income += rmd
        
        # Spending logic
        if age_now >= retire_age:
            gap = spend - retirement_income
            if gap < 0:
                gap = 0
            
            if taxable_val >= gap:
                taxable_val -= gap
            else:
                shortfall = gap - taxable_val
                taxable_val = 0
                pretax_val -= shortfall
        
        net = pretax_val * 0.76 + roth_val + taxable_val
        wealth.append(net)
    
    return wealth

# -----------------------------
# RUN MONTE CARLO
# -----------------------------
results = np.array([run_sim() for _ in range(simulations)])

median = np.median(results, axis=0)
p10 = np.percentile(results, 10, axis=0)
p90 = np.percentile(results, 90, axis=0)

final_vals = results[:, -1]

# -----------------------------
# RESULTS
# -----------------------------
st.subheader("📈 Results")

col1, col2, col3 = st.columns(3)

col1.metric("Median Wealth", f"${int(np.median(final_vals)):,}")
col2.metric("Downside (10%)", f"${int(np.percentile(final_vals,10)):,}")
col3.metric("Upside (90%)", f"${int(np.percentile(final_vals,90)):,}")

# -----------------------------
# CHART
# -----------------------------
st.subheader("Wealth Projection")

ages = list(range(age, age+30))

fig, ax = plt.subplots()

for i in range(min(50, simulations)):
    ax.plot(ages, results[i], color="gray", alpha=0.2)

ax.plot(ages, median, color="blue", linewidth=3, label="Median")
ax.plot(ages, p10, linestyle="--", label="Downside")
ax.plot(ages, p90, linestyle="--", label="Upside")

ax.legend()
ax.grid()

st.pyplot(fig)

# -----------------------------
# STRATEGY OUTPUT
# -----------------------------
st.subheader("🧠 Recommended Strategy")

st.write("✅ Max pre-tax contributions before retirement")

st.write(f"✅ Convert up to ~${conversion_cap:,}/year between {retire_age}–70")

st.write("✅ Delay Social Security to age 70")

st.write("✅ Use taxable account first for retirement spending")

# -----------------------------
# SIMPLE TAX INSIGHT
# -----------------------------
if income_now > 250000:
    st.warning("⚠ You are currently in a high tax bracket — avoid Roth conversions before retirement")

if retirement_income < 80000:
    st.success("✅ You have a strong low-income window for tax-efficient conversions")

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.markdown("Built for financial education only. Not investment or tax advice.")