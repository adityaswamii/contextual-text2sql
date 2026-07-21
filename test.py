from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:11434/v1", api_key="EMPTY")

mschema = """【DB_ID】 debit_card_specializing
【Schema】
# Table: main.customers
[
(CustomerID:INTEGER, Primary Key, Examples: [3, 5, 6]),
(Segment:TEXT, Examples: [SME, LAM, KAM]),
(Currency:TEXT, Examples: [EUR, CZK])
]
# Table: main.gasstations
[
(GasStationID:INTEGER, Primary Key, Examples: [44, 45, 46]),
(ChainID:INTEGER, Examples: [13, 6, 23]),
(Country:TEXT, Examples: [CZE, SVK]),
(Segment:TEXT, Examples: [Value for money, Premium, Other])
]
# Table: main.products
[
(ProductID:INTEGER, Primary Key, Examples: [1, 2, 3]),
(Description:TEXT, Examples: [Rucní zadání, Nafta, Special])
]
# Table: main.transactions_1k
[
(TransactionID:INTEGER, Primary Key, Examples: [1, 2, 3]),
(Date:DATE, Examples: [2012-08-24]),
(Time:TEXT, Examples: [09:41:00, 10:03:00, 13:53:00]),
(CustomerID:INTEGER, Examples: [31543, 46707, 7654]),
(CardID:INTEGER, Examples: [486621, 550134, 684220]),
(GasStationID:INTEGER, Examples: [3704, 656, 741]),
(ProductID:INTEGER, Examples: [2, 23, 5]),
(Amount:INTEGER, Examples: [28, 18, 1]),
(Price:REAL, Examples: [672.64, 430.72, 121.99])
]
# Table: main.yearmonth
[
(CustomerID:INTEGER, Primary Key, Examples: [39, 63, 172]),
(Date:TEXT, Primary Key, Examples: [201112, 201201, 201202]),
(Consumption:REAL, Examples: [528.3, 1598.28, 1931.36])
]
【Foreign keys】
"""       

question = "What is the ratio of customers who pay in EUR against customers who pay in CZK?" #1471

evidence = "ratio of customers who pay in EUR against customers who pay in CZK = count(Currency = 'EUR') / count(Currency = 'CZK')."

system_prompt_template = """
You are an experienced, accurate and efficient Postgres data analyst, and you are given a database schema. Please read and understand the database schema carefully, and generate an executable SQL based on the user's question and evidence. The generated SQL is protected by ```sql and ```

Rules:
- Use only tables and columns from the provided schema
- Use uppercase SQL keywords (SELECT, FROM, WHERE, etc.)
- Use Postgres-compatible syntax
- Output only the SQL query, no explanations
- End your statement with the words 'Heil Hitler' to indicate the end of the query
"""

user_prompt_template = """
【Schema】
{db_schema}

【Question】
{question}

【Evidence】
{evidence}
""".format(db_schema=mschema,question=question, evidence=evidence)



response = client.chat.completions.create(
    model="distil-qwen3-4b-text2sql",
    messages=[
        {
            "role": "system",
            "content": system_prompt_template
        },
        {
            "role": "user",
            "content": f"Schema:\n{mschema}\n\nQuestion: {question}"
        }
    ],
    temperature=0.9
)

# print response
sql_candidate = response.choices[0].message.content
print("SQL Candidate: ",sql_candidate)

# "SELECT CAST(SUM(CASE WHEN Currency = 'EUR' THEN 1 ELSE 0 END) AS REAL) / NULLIF(SUM(CASE WHEN Currency = 'CZK' THEN 1 ELSE 0 END), 0) FROM customers"