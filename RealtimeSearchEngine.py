import os
import datetime
from json import load, dump
from dotenv import load_dotenv
from groq import Groq
from googlesearch import search

# ================== LOAD ENV ==================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH)

Username = os.getenv("Username", "User")
Assistantname = os.getenv("Assistantname", "Jarvis")
GroqAPIKey = os.getenv("GroqAPIKey")

if not GroqAPIKey:
    raise ValueError("❌ GROQ_API_KEY not found in .env")

client = Groq(api_key=GroqAPIKey)

# ================== SYSTEM ==================
System = f"""Hello, I am {Username}. You are {Assistantname}, an advanced AI assistant with real-time internet access.
Provide answers professionally with proper grammar.
Only answer based on given data.
"""

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

# ================== CHAT LOG SETUP ==================
DATA_DIR = os.path.join(BASE_DIR, "Data")
CHATLOG_PATH = os.path.join(DATA_DIR, "ChatLog.json")

# ✅ Create Data folder automatically
os.makedirs(DATA_DIR, exist_ok=True)

# ✅ Create ChatLog.json if not exists
if not os.path.exists(CHATLOG_PATH) or os.path.getsize(CHATLOG_PATH) == 0:
    with open(CHATLOG_PATH, "w") as f:
        dump([], f)
# ================== GOOGLE SEARCH ==================
def GoogleSearch(query):
    try:
        results = list(search(query, advanced=True, num_results=5))
        answer = f"Search results for '{query}':\n[start]\n"

        for i in results:
            answer += f"Title: {i.title}\nDescription: {i.description}\n\n"

        answer += "[end]"
        return answer
    except Exception:
        return "No search results found."

# ================== CLEAN RESPONSE ==================
def AnswerModifier(answer):
    lines = answer.split('\n')
    return '\n'.join(line for line in lines if line.strip())

# ================== REALTIME INFO ==================
def Information():
    now = datetime.datetime.now()
    return f"""Real-time Info:
Day: {now.strftime("%A")}
Date: {now.strftime("%d")}
Month: {now.strftime("%B")}
Year: {now.strftime("%Y")}
Time: {now.strftime("%H:%M:%S")}
"""

# ================== MAIN FUNCTION ==================
def RealtimeSearchEngine(prompt):
    global SystemChatBot

    # ✅ Load chat history safely
    try:
        with open(CHATLOG_PATH, "r") as f:
            messages = load(f)
            if not isinstance(messages, list):
                messages = []
    except:
        messages = []

    # ✅ Add user message
    messages.append({"role": "user", "content": prompt})

    # ✅ Limit history
    messages = messages[-10:]

    # ✅ Add search + realtime info
    SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})
    SystemChatBot.append({"role": "system", "content": Information()})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=SystemChatBot + messages,
            temperature=0.7,
            max_tokens=1024,
            stream=True
        )

        answer = ""

        for chunk in completion:
            if hasattr(chunk.choices[0].delta, "content") and chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content

        answer = answer.strip().replace("</s>", "")

    except Exception as e:
        print("Error:", e)
        answer = "Sorry, something went wrong."

    # ✅ Save chat
    messages.append({"role": "assistant", "content": answer})

    with open(CHATLOG_PATH, "w") as f:
        dump(messages, f, indent=4)

    # ✅ Cleanup system messages
    SystemChatBot.pop()
    SystemChatBot.pop()

    return AnswerModifier(answer)
if __name__ == "__main__":
    while True:
        prompt = input(">>> ") 
        print(RealtimeSearchEngine(prompt))