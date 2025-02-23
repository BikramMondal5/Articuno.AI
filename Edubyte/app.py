from flask import Flask, render_template
import markdown
import os
from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown

# Initializing the app
app = Flask(__name__)
console = Console()

@app.route('/')
def home_page():
    # OpenAI API Configuration
    token = "github-pat"
    endpoint = "https://models.inference.ai.azure.com"
    model_name = "gpt-4o"
    client = OpenAI(
        base_url=endpoint,
        api_key=token,
    )
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Respond in well-structured format using headings, lists, and appropriate interactive emojis."},
            {"role": "user", "content": "Who is the CEO of Google"}
        ],
        temperature=1.0,
        top_p=1.0,
        max_tokens=1000,
        model=model_name
    )

    # Extract response text
    markdown_output = response.choices[0].message.content 
    final_response = markdown.markdown(markdown_output)
    return render_template('index.html', final_response=final_response)


if __name__ == '__main__':
    app.run(debug=True)


