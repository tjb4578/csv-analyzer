import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import altair as alt
import datetime as dt
import openai

def generate(prompt, df, file):
  columns = df.columns
  column_types = df.dtypes
  col_types = {}
  for i in range(len(columns)):
    col_types[columns[i]] = column_types[i]

  col_types_str = ""
  for col in col_types:
    col_types_str += col + ": " + str(col_types[col]) + ".  "
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
      { "role": "system", "content": "You are a CSV analyzer.  The user has uploaded a csv file called " + file.name + " with the following columns: " + col_types_str + " Assume the data has already been loaded into a dataframe df and all necessary packages have already been imported.  The user will submit a prompt asking you to analyze the data in some way, and you will return python code to accomplish this.  If the result is text, display the result by using st.write(result).  If it requires a chart, create an altair chart and use st.write(chart).  Return only code in a markdown code block, no explanations.  Do not import packages or read the csv." },
      { "role": "user", "content": prompt },
    ]
  )

  return response.choices[0].message.content

def trim_output(output):
  output = output.replace("```python", "")
  output = output.replace("```", "")

  # If line is an import statement or read_csv statement, remove it
  lines = output.splitlines()
  for line in lines:
    if line.startswith("import") or line.startswith("df = pd.read_csv"):
      output = output.replace(line, "")
  return output

openai.api_key = None

st.set_page_config(layout="wide")

st.title('CSV Analyzer')

st.write("Upload a CSV file to analyze")
file = st.file_uploader("Upload CSV", type=["csv"])

if file is not None:
  assert file.name.endswith('.csv'), 'File must be a CSV'
  df = pd.read_csv(file)

  st.write("File uploaded successfully")
  st.write(df.head(5))

  openai.api_key = st.text_input("Enter your OpenAI API key", type="password")
    
  prompt = st.text_input("Enter a prompt", "The following table contains information about ...")

  if st.button("Generate"):
    output = generate(prompt, df, file)
    st.write(output)

    print(output)
    # Trim output to only include code
    output = trim_output(output)
    exec(output)
  