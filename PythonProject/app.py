from flask import Flask, request, render_template, jsonify
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain_groq import ChatGroq
from langchain.agents.agent import AgentExecutor
import time

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/query", methods=["POST"])
def query():
    user_input = request.json.get("query", "")

    for attempt in range(5):
        try:
            # Recreate the LLM and Agent each time
            llm = ChatGroq(
                model="llama3-70b-8192",
                api_key="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"
            )
            db = SQLDatabase.from_uri("sqlite:///mydb.db")
            agent = create_sql_agent(
                llm=llm,
                toolkit=SQLDatabaseToolkit(db=db, llm=llm),
                verbose=False,
            handle_parsing_errors = True
            )

            result = agent.run(user_input)
            return jsonify({"response": result})

        except Exception as e:
            if "rate limit" in str(e).lower():
                wait_time = 2 ** attempt
                time.sleep(wait_time)  # exponential backoff
            else:
                return jsonify({"response": f"Error: {str(e)}"})

    return jsonify({"response": "Rate limit hit multiple times. Please try again later."})

if __name__ == "__main__":
    app.run(debug=True, threaded=True)  # Enable threaded to handle concurrent requests
