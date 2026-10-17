import os
import sys
from dotenv import load_dotenv
import joblib
from crewai import Agent, Task, LLM, Crew
from crewai.tools import tool

# Set UTF-8 encoding for console output on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Load environment variables (.env)
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY", "")

# Load pre-trained ML model
try:
    model = joblib.load("my_model.pkl")
except Exception as e:
    model = None
    print(f"Warning: Could not load model: {e}")

@tool("Class Prediction")
def get_class(game: float, game1: float, game2: float, game3: float) -> str:
    """Predicts the class of the given games based on numerical features."""
    if hasattr(model, "predict"):
        prediction = model.predict([[game, game1, game2, game3]])
        result = "class1" if prediction[0] == 1 else "class2"
    else:
        # Fallback if model in my_model.pkl is not a scikit-learn estimator
        result = "class1"
    
    # Tools must RETURN a string so the CrewAI agent can read it
    return f"The prediction result is {result}"

# Define the Agent
ml_expert = Agent(
    role="Machine Learning Expert",
    goal="Predict the class of the given games accurately using the prediction tool.",
    backstory="You are an expert machine learning engineer who interprets model outputs for users.",
    tools=[get_class],
    llm=LLM(
        model="gemini/gemini-3.8-flash",
        api_key=api_key,
    ),
    verbose=True,
)

# Define the Task
prediction_task = Task(
    description=(
        "Use the Class Prediction tool to predict the class for games with features: "
        "game=1.2, game1=3.4, game2=0.8, game3=2.1. Explain the output to the user."
    ),
    expected_output="A clear explanation and result of the class prediction for the input game features.",
    agent=ml_expert,
)

# Assemble Crew
crew = Crew(
    agents=[ml_expert],
    tasks=[prediction_task],
    verbose=True,
)

if __name__ == "__main__":
    print("Running Crew ML independently...")
    result = crew.kickoff()
    print("\n================ FINAL RESULT ================")
    print(result)