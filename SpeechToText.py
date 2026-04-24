from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from dotenv import dotenv_values

import os
import mtranslate as mt

# Load environment variables
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage")

# HTML content with speech recognition
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# Inject Input Language
HtmlCode = HtmlCode.replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Save HTML to file
os.makedirs("Data", exist_ok=True)
with open("Data/Voice.html", "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# Construct local file URL
current_dir = os.getcwd()
Link = f"{current_dir}/Data/Voice.html"

# Set Chrome options for Chrome Beta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

chrome_options = webdriver.ChromeOptions()

# optional clean logs
chrome_options = webdriver.ChromeOptions()

# 🔕 suppress logs
chrome_options.add_argument("--log-level=3")
chrome_options.add_argument("--silent")
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
chrome_options.add_argument("--log-level=3")
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)
# Set manually downloaded ChromeDriver for Chrome Beta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--start-maximized")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

# Setup temp status path
TempDirPath = os.path.join(current_dir, "Frontend", "Files")
os.makedirs(TempDirPath, exist_ok=True)

def SetAssistantStatus(Status):
    with open(os.path.join(TempDirPath, "Status.data"), "w", encoding='utf-8') as file:
        file.write(Status)

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you"]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()

def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation

def SpeechRecognition():
    driver.get("file:///" + Link)
    driver.find_element(By.ID, "start").click()

    while True:
        try:
            Text = driver.find_element(By.ID, "output").text
            if Text:
                driver.find_element(By.ID, "end").click()
                if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                    return QueryModifier(Text)
                else:
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslator(Text))
        except Exception:
            pass

# Run the assistant
if __name__ == "__main__":
    while True:
        Text = SpeechRecognition()
        print(Text)
