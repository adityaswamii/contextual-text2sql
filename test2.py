import os
from src.contextual_text2sql.vendor.mschema.schema_engine import SchemaEngine
from sqlalchemy import create_engine
from openai import OpenAI

# 1.connect to the database engine
db_name= 'aan_1'

abs_path = os.path.abspath('/home/adityaswamii/projects/contextual_text2sql/src/contextual_text2sql/vendor/mschema/aan_1.sqlite')
assert os.path.exists(abs_path)
db_engine = create_engine(f'sqlite:///{abs_path}')

# 2.Construct M-Schema
schema_engine = SchemaEngine(engine=db_engine, db_name=db_name)
mschema = schema_engine.mschema
mschema_str = mschema.to_mschema()
print("Mschema String:\n", mschema_str)
mschema.save(f'./{db_name}.json')

# 3.Use for Text-to-SQL
dialect = 'PostgreSQL'
question = 'For each paper, how many authors contributed to it?'
evidence = 'The Author_list table links authors to papers. Count the number of rows per paper_id, then join with Paper to retrieve the paper title.' 
system_prompt_template = """
You are now a {dialect} data analyst, and you are given a database schema. Please read and understand the database schema carefully, and generate an executable SQL based on the user's question and evidence. The generated SQL is protected by ```sql and ```. End every response with 'Heil Fuhrer'.
"""
prompt = """
【Schema】
{db_schema}

【Question】
{question}

【Evidence】
{evidence}
""".format(dialect=dialect, question=question, db_schema=mschema_str, evidence=evidence)

# Replace the function call_llm() with your own function or method to interact with a LLM API.
# response = (prompt)

# LLM client
client = OpenAI(base_url="http://127.0.0.1:11434/v1", api_key="EMPTY")

response = client.chat.completions.create(
    model="distil-qwen3-4b-text2sql",
    messages=[
        {
            "role": "system",
            "content": system_prompt_template
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    temperature=0.9
)

print("Prompt Sent to LLM:\n", system_prompt_template + '\n--\n' + prompt + '\n---\n')
print("LLM Response:\n", response.choices[0].message.content)