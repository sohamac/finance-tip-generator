import streamlit as st
import requests
import json
from typing import List
import matplotlib.pyplot as plt

# Load API Key
api_key = st.secrets["OPENROUTER_API_KEY"]

# Page Config
st.set_page_config(page_title="💸 Finance Tip Generator", layout="centered")
st.title("💸 Personal Finance Tip Generator")
st.markdown("Get personalized savings advice based on your goals, habits, and profile.")

# Inputs
income = st.number_input("Monthly Income (₹)", min_value=0, step=1000)
expenses = st.number_input("Monthly Expenses (₹)", min_value=0, step=1000)
goal = st.text_input("Your Savings Goal (e.g., emergency fund, new phone)")
persona = st.selectbox("Who are you financially?", ["Student", "Freelancer", "Salaried", "Investor", "Parent"])
tone = st.selectbox("Style of Advice", ["Short and Practical", "Conversational", "Educational", "Step-by-Step"])
expense_breakdown = st.text_area("Optional: Break down your expenses (e.g., Rent: 10000, Food: 5000)")

show_graph = st.checkbox("📊 Show Budget Visualization")
download_btn = False

def make_chart(income, expenses):
    labels = ["Expenses", "Suggested Savings", "Leftover"]
    savings = income * 0.2
    leftover = income - expenses - savings
    values = [expenses, savings, max(leftover, 0)]
    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=140)
    ax.axis("equal")
    st.pyplot(fig)

def format_expense_check(income, expenses):
    if expenses > income:
        return "🔴 You're spending more than you earn. Consider cutting back!"
    elif expenses > 0.8 * income:
        return "🟡 You're spending a lot — try to save at least 20% of income."
    else:
        return "🟢 Great! You're spending responsibly."

if st.button("🧠 Generate Financial Tips"):
    if not income or not expenses or not goal:
        st.warning("Please fill all mandatory fields.")
    else:
        with st.spinner("Thinking..."):
            prompt = f"""
            I'm a {persona} earning ₹{income}/month, spending ₹{expenses}/month.
            My goal is to: {goal}.
            {f"My expense breakdown is: {expense_breakdown}" if expense_breakdown else ""}
            Give me 3 {tone.lower()} financial tips to help save more, and a 3-month roadmap.
            Output in clear bullet points.
            """

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "mistralai/mixtral-8x7b-instruct",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            }

            try:
                r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
                output = r.json()["choices"][0]["message"]["content"]
                st.success("Here are your personalized finance tips:")
                st.markdown(output)
                download_btn = True

                if show_graph:
                    st.subheader("📈 Budget Breakdown")
                    make_chart(income, expenses)

                st.markdown("### 🧾 Spending Assessment")
                st.info(format_expense_check(income, expenses))

                st.download_button("📥 Download Tips as Text", output.encode("utf-8"), file_name="finance_tips.txt")

            except Exception as e:
                st.error(f"Error: {e}")
