"""Quick Groq API live test — run once to confirm the model responds."""
from config.llm_client import get_chat_llm

print("Testing Groq API connection...")
llm = get_chat_llm()
res = llm.invoke("You are an Indian stock market analyst. Say Namaste and state which model you are in one sentence.")
print(f"Model:    {llm.model_name}")
print(f"Response: {res.content.strip()}")
print("GROQ CONNECTION: OK")
