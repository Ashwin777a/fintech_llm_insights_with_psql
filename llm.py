import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# --- Environment ---

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_llm_insights(df):
    prompt = f"You are a fintech analyst. Based on the following stock data for {df['date'].iloc[0]}, provide a short summary and 3 actionable recommendations:\n\n{df.to_string(index=False)}"
    
    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = completion.choices[0].message.content
        return prompt, response_text

    except Exception as e:
        print("Error calling Groq API:", e)
        return prompt, f"Error: {e}"

