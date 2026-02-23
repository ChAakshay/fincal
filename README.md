# fincal
The Reality Check Dashboard
The Reality Check Dashboard is a financial analysis terminal built with Python and Streamlit. Unlike standard financial calculators that rely on optimistic nominal returns, this tool incorporates real-world economic friction—including inflation, taxation (LTCG), and market volatility—to reveal the true purchasing power of investments.

It is designed to challenge common wealth-building myths through rigorous mathematical modeling, offering users a probabilistic perspective on decisions regarding SIPs, real estate, and debt.

Project Overview
This application serves as an "anti-hype" financial tool. It shifts the focus from simple compound interest calculators to complex, scenario-based modeling.

Key Features
1. The Wealth Illusion Module

Real Purchasing Power: Calculates the actual value of a future corpus by adjusting for inflation and the 12.5% Long Term Capital Gains (LTCG) tax applicable in India.

Wealth Level System: Classifies financial standing into tiered levels based on real, inflation-adjusted wealth rather than nominal figures.

2. Rent vs. Buy (Monte Carlo Engine)

Probabilistic Modeling: Runs 500 parallel simulations to determine the mathematical probability of renting versus buying a home.

Variable Inputs: Accounts for market volatility (equity risk), rental inflation, and property appreciation (land + building value) to provide a comprehensive risk profile.

3. The Catch-Up Tax (Cost of Delay)

Age-Based Analysis: Quantifies the exponential cost of delaying investments based on the user's current age versus their ideal starting age.

Recovery Calculation: Determines the exact additional monthly investment required to achieve the same financial goal due to the lost compounding period.

4. The Debt Trap Analyzer

Opportunity Cost Visualization: Calculates the true cost of buying depreciating assets (electronics, vehicles) on EMI.

Future Value Loss: Projects the potential future wealth lost by paying interest to a lender instead of investing that capital.

Technical Stack
Frontend/Backend: Python (Streamlit Framework)

Data Visualization: Plotly Graph Objects (Custom Dark Theme)

Computation: NumPy (Normal Distribution for volatility simulations)

Data Handling: Pandas
