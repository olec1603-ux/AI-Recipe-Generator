import pandas as pd
from openai import OpenAI
import json
import os
try:
    import pyttsx3
    HAS_TTS = True
except ImportError:
    HAS_TTS = False
    print("TTS library not found, running in cloud mode without voice.")

# --- Config ---
API_KEY = st.secrets["API_KEY"] 
client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")
DB_FILE = "recipe_history.csv"

def init_storage():
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=["Date", "Recipe_Name", "Ingredients", "Goal", "Calories", "Protein", "Carbs", "Fat"])
        df.to_csv(DB_FILE, index=False)

def text_to_speech(text, filename="recipe_audio.mp3"):
    
    if not HAS_TTS:
        return None
    
    try:
        engine = pyttsx3.init()
 
        return filename
    except Exception as e:
        print(f"TTS Error: {e}")
        return None

def generate_health_reflection():
    if not os.path.exists(DB_FILE): return "No data."
    df = pd.read_csv(DB_FILE).tail(10)
    if df.empty: return "No history."
    summary_data = df[['Goal', 'Calories', 'Protein', 'Carbs', 'Fat']].to_string()
    prompt = f"Analyze this history and provide a Weekly Health Review in professional Markdown:\n{summary_data}"
    try:
        response = client.chat.completions.create(model="deepseek-chat", messages=[{"role": "system", "content": prompt}])
        return response.choices[0].message.content
    except: return "Error."

def generate_recipe_and_nutrition(ingredients, restriction, goal):
    init_storage()
    # 强制要求 LLM 使用 Markdown 换行符以规整排版
    system_prompt = """You are an elite chef. Return a JSON object. 
    IMPORTANT: Use '\\n' for line breaks in 'steps' and 'substitutions' for vertical alignment.
    - "recipe_name": string
    - "steps": "Numbered list (1., 2., 3.) with newlines."
    - "substitutions": "Bulleted list (- ) with newlines."
    - "grocery_list": ["item 1", "item 2"]
    - "macros": {"calories": int, "protein": int, "carbs": int, "fat": int}
    """
    user_input = f"Ingredients: {ingredients}. Restrictions: {restriction}. Goal: {goal}."
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_input}],
            response_format={'type': 'json_object'}
        )
        result = json.loads(response.choices[0].message.content)
        audio_file = text_to_speech(f"Recipe: {result.get('recipe_name')}. {result.get('steps')}")

        new_record = pd.DataFrame([{
            "Date": pd.Timestamp.now().strftime("%m/%d %H:%M"), # 精简日期格式
            "Recipe_Name": result.get("recipe_name"),
            "Ingredients": ingredients,
            "Goal": goal,
            "Calories": result["macros"].get("calories", 0),
            "Protein": result["macros"].get("protein", 0),
            "Carbs": result["macros"].get("carbs", 0),
            "Fat": result["macros"].get("fat", 0)
        }])
        pd.concat([pd.read_csv(DB_FILE), new_record], ignore_index=True).to_csv(DB_FILE, index=False)
        return result, audio_file
    except Exception as e:
        return {"error": str(e)}, None