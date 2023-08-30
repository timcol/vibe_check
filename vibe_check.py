from concurrent.futures import ThreadPoolExecutor
import openai
import re
import pandas as pd


def get_LLM_scores(chunk):
    criteria = ["Logical Consistency", "Relevance", "Depth", "Originality", "Clarity"]
    scores = {}
    
    print(f"Processing chunk: {chunk[:50]}...")
    
    for criterion in criteria:
        prompt = f"Evaluate the following text in terms of {criterion}: \"{chunk}\". Assign it a numerical integer rating between 1-5, Then return just that number and nothing else."
        print(f"Sending prompt for {criterion}")
        response = ask_gpt(prompt)
        
        try:
            score = int(re.search(r'\b[1-5]\b', response).group(0))
        except (ValueError, AttributeError) as e:
            print(f"Could not interpret the score for {criterion}. Error: {e}")
            score = None
        
        if score is not None:
            scores[criterion.lower().replace(" ", "_")] = score
            
    print(f"Scores for this chunk: {scores}")
    return scores

def ask_gpt(prompt):
    try:
        r = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in all fields and disciplines. Explain concepts, theories and phenomena in an engaging and accessible way"},
                {"role": "user", "content": prompt}
            ],
            timeout=30
        )
        return r["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"API call failed: {e}")
        return None

score_dicts = []

with open("cleaned.txt", "r") as f:
    sentences = f.read().split('. ')

chunks = ['. '.join(sentences[i:i+40]).strip() for i in range(0, len(sentences), 40)]

# Use ThreadPoolExecutor to execute get_LLM_scores in parallel
with ThreadPoolExecutor(max_workers=10) as executor:
    future_to_chunk = {executor.submit(get_LLM_scores, chunk): chunk for chunk in chunks}
    for future in future_to_chunk:
        scores = future.result()
        if scores:
            score_dicts.append(scores)

df = pd.DataFrame(score_dicts)

# Display the DataFrame
print(df)

# Calculate and display averages
print("\nAverage Scores:")
print(df.mean())

# ... (rest of your existing code)

# Calculate the overall average score across all values in the DataFrame
overall_avg = df.mean().mean()

# ASCII Art for the different categories
plane_art = """
    __|__
---( o o )---
 \   ^   /
  |||||||
  |||||||
"""

train_art = """
   o O __
 _][__| o |  
<__________|  
 |_|_| |_|_|
"""

pot_of_gold_art = """
   O  O  O
 O-------O
  \_____/  
"""

# Print appropriate ASCII art and text based on the overall average
if overall_avg <= 2:
    print(plane_art)
    print("Low altitude flyer detected")
elif 2 < overall_avg <= 3.5:
    print(train_art)
    print("Suss")
else:
    print(pot_of_gold_art)
    print("Could be gold")
