# Finance Tip Generator

A single-page Streamlit app that generates personalized savings advice using an LLM (via OpenRouter), with an optional budget pie-chart visualization.

## What this actually does

- Collects income, expenses, savings goal, persona, and desired advice tone/style through a Streamlit form.
- Sends a prompt built from those inputs to OpenRouter's chat completions API (`mistralai/mixtral-8x7b-instruct`).
- Displays the returned tips, an optional pie-chart budget breakdown (expenses / suggested 20% savings / leftover), and a simple rule-based spending assessment (not LLM-generated).
- Lets the user download the generated tips as a `.txt` file.

This is a real, working integration -- it makes a genuine API call and displays a genuine model response. It's a thin single-file app, not a system with a database, auth, or persistence.

## Setup

1. Get an API key from [OpenRouter](https://openrouter.ai/keys).
2. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and paste in your key.
3. Install dependencies and run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

**Do not commit `.streamlit/secrets.toml`** -- it's gitignored for a reason. If you're deploying to Streamlit Community Cloud, set the secret in the app's dashboard instead of committing a file.

## Known Limitations

- No conversation history or persistence -- each generation is a one-off, stateless request.
- No input validation beyond "non-zero/non-empty" -- e.g. a savings goal of empty string with only whitespace would pass.
- The "suggested savings" in the pie chart is a fixed 20% of income, not personalized to the user's actual goal or persona.
- Error handling now distinguishes timeouts, network errors, and malformed API responses, but there's no retry logic.

## License

MIT
