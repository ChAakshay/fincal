import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="The Reality Check | Elite Edition",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stApp { background-color: #0e1117; }
    h1, h2, h3 { color: #fafafa !important; font-family: 'Helvetica Neue', sans-serif; }
    .stMetricLabel { color: #a0a0a0 !important; }
    .stMetricValue { color: #ffffff !important; }
    
    .level-card {
        padding: 1.5rem; border-radius: 10px; 
        background: linear-gradient(145deg, #1e1e1e, #252525);
        border: 1px solid #333; box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 1rem; color: #fff;
    }
    .highlight-green { color: #00ff7f; font-weight: bold; }
    .highlight-red { color: #ff4b4b; font-weight: bold; }
    .highlight-gold { color: #ffd700; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HELPER FUNCTIONS ---

def apply_dark_theme(fig):
    """Manually applies dark theme to charts"""
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e0e0e0'),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='#333333', zeroline=False),
    )
    return fig

def format_currency(value):
    if value >= 10000000: return f"₹{value/10000000:.2f} Cr"
    elif value >= 100000: return f"₹{value/100000:.2f} L"
    else: return f"₹{value:,.0f}"

def calculate_ltcg(corpus, invested_amount):
    gains = corpus - invested_amount
    if gains < 125000: return 0
    return (gains - 125000) * 0.125

def monte_carlo_rent_vs_buy(home_price, rent_start, tenure, market_ret_mean, market_vol, home_appr_mean):
    results_buy = []
    results_rent = []
    
    down_payment = home_price * 0.20
    loan_amount = home_price * 0.80
    upfront_costs = home_price * 0.06
    initial_investable = down_payment + upfront_costs
    
    r = 8.5 / 12 / 100
    n = tenure * 12
    emi = loan_amount * r * ((1 + r)**n) / (((1 + r)**n) - 1)
    
    for _ in range(500):
        sim_market_ret = np.random.normal(market_ret_mean, market_vol) / 100
        sim_home_appr = np.random.normal(home_appr_mean, 1.0) / 100 
        sim_rent_infl = np.random.normal(6.0, 1.0) / 100 
        
        # --- BUY SCENARIO (Includes Land Appreciation) ---
        # We grow the ENTIRE home value, which effectively captures land value growth
        final_home_val = home_price * ((1 + sim_home_appr) ** tenure)
        results_buy.append(final_home_val)
        
        # --- RENT SCENARIO ---
        portfolio = initial_investable
        curr_rent = rent_start
        curr_maint = (home_price * 0.005) / 12 
        
        for year in range(tenure):
            yearly_emi = emi * 12
            yearly_rent = curr_rent * 12
            yearly_maint = curr_maint * 12
            
            # Renters save EMI + Maintenance cost
            cost_buy = yearly_emi + yearly_maint
            cost_rent = yearly_rent
            surplus = cost_buy - cost_rent
            
            portfolio = portfolio * (1 + sim_market_ret) + surplus
            
            curr_rent *= (1 + sim_rent_infl)
            curr_maint *= (1 + 0.05)
            
        results_rent.append(portfolio)
        
    return np.mean(results_buy), np.mean(results_rent), np.sum(np.array(results_rent) > np.array(results_buy))

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("💎 Reality Check")
    st.caption("Elite Edition")
    st.markdown("---")
    page = st.radio("Select Module:", 
        ["Cost of Delay (Age Based)", "Rent vs Buy (Land Value Included)", "The Wealth Illusion (SIP)", "The Debt Trap (EMI)"])
    st.markdown("---")
    st.info("💡 **Philosophy:** Time in the market > Timing the market.")

# --- PAGE 1: COST OF DELAY (AGE BASED) ---
if page == "Cost of Delay (Age Based)":
    st.title("⏳ The 'Catch-Up' Tax")
    st.markdown("### How much extra do you have to pay because you started late?")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Your Profile")
        target_corpus_cr = st.number_input("Target Wealth at Retirement (Crores)", value=5.0, step=0.5)
        current_age = st.number_input("Your Current Age", value=30, step=1)
        start_age = st.number_input("Ideal Start Age", value=22, help="When you got your first job")
        retire_age = st.number_input("Retirement Age", value=60)
        exp_return = st.number_input("Exp. Return (%)", value=12.0)
        
    # --- MATH ENGINE ---
    target_corpus = target_corpus_cr * 10000000
    
    def calculate_required_sip(target, years, r):
        if years <= 0: return 0
        r_monthly = r/1200
        n_months = years * 12
        # SIP Formula: P = FV / [((1+r)^n - 1)/r * (1+r)]
        factor = (((1 + r_monthly)**n_months) - 1) / r_monthly * (1 + r_monthly)
        return target / factor

    # 1. Ideal Scenario (Started at 22)
    years_ideal = retire_age - start_age
    sip_ideal = calculate_required_sip(target_corpus, years_ideal, exp_return)
    
    # 2. Reality Scenario (Starting Now at 30)
    years_real = retire_age - current_age
    sip_real = calculate_required_sip(target_corpus, years_real, exp_return)
    
    # 3. The Tax
    catch_up_tax = sip_real - sip_ideal
    tax_percentage = (catch_up_tax / sip_ideal) * 100 if sip_ideal > 0 else 0

    with col2:
        c1, c2, c3 = st.columns(3)
        c1.metric("Target Goal", f"₹{target_corpus_cr} Cr")
        c2.metric("SIP Needed (Then)", format_currency(sip_ideal), help=f"If you started at age {start_age}")
        c3.metric("SIP Needed (Now)", format_currency(sip_real), delta=f"+{tax_percentage:.0f}% Higher", delta_color="inverse", help=f"Starting at age {current_age}")
        
        st.markdown(f"""
        <div class='level-card'>
            <h3 class='highlight-gold'>⚡ Your Catch-Up Tax: {format_currency(catch_up_tax)} / month</h3>
            Because you waited <b>{current_age - start_age} years</b>, you don't just pay the missed installments.<br>
            You pay a penalty of <b>{format_currency(catch_up_tax)}</b> every single month for the rest of your life to hit the same goal.
        </div>
        """, unsafe_allow_html=True)
        
        # VISUALIZATION: The Exponential Cost Curve
        ages = list(range(start_age, 50)) # Plot cost for starting at ages 22 to 50
        sips = []
        for age in ages:
            y = retire_age - age
            if y > 0:
                sips.append(calculate_required_sip(target_corpus, y, exp_return))
            else:
                sips.append(0)
                
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ages, y=sips, mode='lines', name='SIP Required', line=dict(color='#ff4b4b', width=3)))
        
        # Add a marker for "You Are Here"
        fig.add_trace(go.Scatter(
            x=[current_age], y=[sip_real],
            mode='markers+text',
            name='You Are Here',
            text=[f"Age {current_age}"],
            textposition="top left",
            marker=dict(size=12, color='#00ff7f')
        ))
        
        fig = apply_dark_theme(fig)
        fig.update_layout(
            title=f"SIP Required to hit ₹{target_corpus_cr} Cr (By Starting Age)",
            xaxis_title="Age You Start Investing",
            yaxis_title="Monthly SIP Required (₹)",
            height=350, margin=dict(l=0,r=0,t=40,b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

# --- PAGE 2: RENT VS BUY (LAND VALUE) ---
elif page == "Rent vs Buy (Land Value Included)":
    st.title("🏠 Rent vs Buy AI")
    st.markdown("Running 500 Simulations. **Includes Land Value Appreciation.**")
    
    c1, c2 = st.columns(2)
    with c1:
        price = st.number_input("Property Price", value=10000000, step=500000)
        rent = st.number_input("Monthly Rent", value=25000, step=1000)
        tenure = st.slider("Years", 10, 30, 20)
    with c2:
        home_appr = st.slider("Property/Land Appreciation (%)", 2.0, 12.0, 6.0, help="Land appreciates faster than apartments. Set 8-10% for prime land.")
        market_risk = st.selectbox("Market Risk Profile", ["Conservative (10%)", "Balanced (12%)", "Aggressive (15%)"])
    
    risk_map = {"Conservative (10%)": (10, 10), "Balanced (12%)": (12, 15), "Aggressive (15%)": (15, 20)}
    mean, vol = risk_map[market_risk]
    
    if st.button("🚀 Run Simulation"):
        with st.spinner("Calculating Land Value & Market Returns..."):
            avg_buy, avg_rent, rent_wins = monte_carlo_rent_vs_buy(price, rent, tenure, mean, vol, home_appr)
            win_pct = (rent_wins / 500) * 100
            
            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            m1.metric("Rent Win Probability", f"{win_pct:.1f}%")
            m2.metric("Final Asset Value (Buy)", format_currency(avg_buy), help="Includes Land + Building Appreciation")
            m3.metric("Final Wealth (Rent)", format_currency(avg_rent), delta=format_currency(avg_rent - avg_buy))
            
            diff = avg_rent - avg_buy
            if win_pct > 60:
                st.markdown(f"""
                <div class='level-card'>
                    <h3 class='highlight-green'>✅ Strategy: RENT</h3>
                    Even with {home_appr}% land appreciation, the market returns on your surplus (EMI - Rent) outperformed real estate by <b>{format_currency(diff)}</b>.
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='level-card'>
                    <h3 class='highlight-gold'>✅ Strategy: BUY</h3>
                    At {home_appr}% appreciation, the <b>Land Value</b> is compounding faster than the stock market + rent savings. Buying creates more wealth here.
                </div>""", unsafe_allow_html=True)

# --- PAGE 3: WEALTH ILLUSION ---
elif page == "The Wealth Illusion (SIP)":
    st.title("📉 The Wealth Illusion")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        sip = st.number_input("Monthly SIP", value=25000, step=1000)
        years = st.slider("Years", 5, 40, 20)
        ret = st.slider("Return (%)", 8.0, 15.0, 12.0)
        inf = st.slider("Inflation (%)", 4.0, 8.0, 6.0)
        
    months = years * 12
    m_rate = ret/100/12
    invested = sip * months
    fv_nom = sip * ((((1 + m_rate)**months) - 1) / m_rate) * (1 + m_rate)
    
    tax = calculate_ltcg(fv_nom, invested)
    fv_post_tax = fv_nom - tax
    fv_real = fv_post_tax / ((1 + inf/100)**years)
    
    with col2:
        c1, c2, c3 = st.columns(3)
        c1.metric("Screen Shows", format_currency(fv_nom))
        c2.metric("Real Value", format_currency(fv_real), delta=f"-{(1 - fv_real/fv_nom)*100:.0f}% Inflation/Tax")
        c3.metric("Tax Liability", format_currency(tax))
        
        fig = go.Figure(go.Bar(
            y=['Nominal', 'Real'], 
            x=[fv_nom, fv_real], 
            orientation='h',
            marker=dict(color=['#555', '#00ff7f']),
            text=[format_currency(fv_nom), format_currency(fv_real)],
            textposition='auto'
        ))
        fig = apply_dark_theme(fig)
        fig.update_layout(height=250, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

# --- PAGE 4: DEBT TRAP ---
elif page == "The Debt Trap (EMI)":
    st.title("⛓️ The Debt Trap Calculator")
    
    col1, col2 = st.columns([1,2])
    with col1:
        price = st.number_input("Product Price", value=1500000)
        down_pay = st.number_input("Down Payment", value=200000)
        rate = st.number_input("Loan Interest (%)", value=9.5)
        years = st.slider("Loan Tenure (Years)", 1, 7, 5)
        
    loan_amt = price - down_pay
    r = rate/12/100
    n = years*12
    emi = loan_amt * r * ((1 + r)**n) / (((1 + r)**n) - 1)
    total_paid = (emi * n) + down_pay
    
    opp_r = 12.0/12/100
    fv_opp = emi * (((1 + opp_r)**n) - 1) / opp_r * (1 + opp_r)
    
    with col2:
        st.metric("Monthly EMI", format_currency(emi))
        st.markdown(f"""
        <div class='level-card'>
            <h3>The True Cost</h3>
            You aren't paying <b>{format_currency(price)}</b>.<br>
            You are paying <span class='highlight-red'>{format_currency(total_paid)}</span>.
            <hr>
            <b>Opportunity Cost:</b> If you invested this EMI, you'd have <span class='highlight-green'>{format_currency(fv_opp)}</span>.
        </div>
        """, unsafe_allow_html=True)