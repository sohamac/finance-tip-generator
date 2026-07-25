import streamlit as st
import requests
import json
from typing import List
import matplotlib.pyplot as plt

# Load API Key from Streamlit secrets (see .streamlit/secrets.toml.example)
api_key = st.secrets.get("OPENROUTER_API_KEY")

# Page Config
st.set_page_config(page_title="\U0001f4b8 Finance Tip Generator", layout="centered")
st.title("\U0001f4b8 Personal Finance Tip Generator")
st.markdown("Get personalized savings advice based on your goals, habits, and profile.")

if not api_key:
    st.error(
        "No OPENROUTER_API_KEY found. Add one to `.streamlit/secrets.toml` "
        "(see `.streamlit/secrets.toml.example`) or your Streamlit Cloud secrets."
    )
    st.stop()

# Inputs
income = st.number_input("Monthly Income (\u20b9)", min_value=0, step=1000)
expenses = st.number_input("Monthly Expenses (\u20b9)", min_value=0, step=1000)
goal = st.text_input("Your Savings Goal (e.g., emergency fund, new phone)")
persona = st.selectbox("Who are you financially?", ["Student", "Freelancer", "Salaried", "Investor", "Parent"])
tone = st.selectbox("Style of Advice", ["Short and Practical", "Conversational", "Educational", "Step-by-Step"])
expense_breakdown = st.text_area("Optional: Break down your expenses (e.g., Rent: 10000, Food: 5000)")

show_graph = st.checkbox("\U0001f4ca Show Budget Visualization")


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
        return "\U0001f534 You're spending more than you earn. Consider cutting back!"
    elif expenses > 0.8 * income:
        return "\U0001f7e1 You're spending a lot \u2014 try to save at least 20% of income."
    else:
        return "\U0001f7e2 Great! You're spending responsibly."


if st.button("\U0001f9e0 Generate Financial Tips"):
    if not income or not expenses or not goal:
        st.warning("Please fill all mandatory fields.")
    else:
        with st.spinner("Thinking..."):
            prompt = f"""
            I'm a {persona} earning \u20b9{income}/month, spending \u20b9{expenses}/month.
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
                r = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30,
                )
                r.raise_for_status()
                response_json = r.json()

                if "choices" not in response_json:
                    error_msg = response_json.get("error", {}).get("message", "Unknown API response format")
                    st.error(f"The API did not return a completion: {error_msg}")
                else:
                    output = response_json["choices"][0]["message"]["content"]
                    st.success("Here are your personalized finance tips:")
                    st.markdown(output)

                    if show_graph:
                        st.subheader("\U0001f4c8 Budget Breakdown")
                        make_chart(income, expenses)

                    st.markdown("### \U0001f9fe Spending Assessment")
                    st.info(format_expense_check(income, expenses))

                    st.download_button("\U0001f4e5 Download Tips as Text", output.encode("utf-8"), file_name="finance_tips.txt")

            except requests.exceptions.Timeout:
                st.error("The request to OpenRouter timed out. Please try again.")
            except requests.exceptions.RequestException as e:
                st.error(f"Network error contacting OpenRouter: {e}")
            except (KeyError, IndexError, json.JSONDecodeError) as e:
                st.error(f"Unexpected response format from OpenRouter: {e}")
