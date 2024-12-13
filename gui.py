import tkinter as tk
from tkinter import ttk
import google.generativeai as genai
import time
import random

philfields = ["Utilitarianism", "Deontology", "Virtue Ethics", "Contractualist Theory", "Confucian Ethics", "Marxist Ethics", "Rights Based Ethics"]
topics = ["Generative AI", "Genetic Engineering", "Environmental Economics", "Animal Rights", "Physician Assisted Suicide", "Nuclear Weapons", "Development of Defense Technology"]
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

#conv history
conversation_history = []

# Timer duration
TIMER_DURATION = 300  # 5 minutes

# Random topic and ethical perspectives
topic = random.choice(topics)
user_field = random.choice(philfields)
gemini_field = random.choice([field for field in philfields if field != user_field])

def start_chat():
    start_screen.pack_forget()
    chat_screen.pack(fill="both", expand=True)
    start_timer(TIMER_DURATION)
    set_gemini_prompt()

# Set initial Gemini prompt
def set_gemini_prompt():
    intro_message = (f"You are arguing about the topic '{topic}' from the perspective of {gemini_field}. "
                     f"The user is arguing from the perspective of {user_field}. You are to respond in a style of debate to the user with the knowledge of a" 
                     f"college student with rudimentary ethics knowledge, making a few logical mistakes in debate. If the user seeks to discuss their own topics"
                     f"rather than refuting the chatbot's perspective, try and find holes in their argument instead. Keep responses short and curt."
                     )
    conversation_history.append(f"System: {intro_message}")

# Timer functionality
def start_timer(duration):
    def countdown():
        nonlocal duration
        while duration > 0:
            minutes, seconds = divmod(duration, 60)
            timer_label.config(text=f"{minutes:02}:{seconds:02}")
            root.update()
            time.sleep(1)
            duration -= 1
        timer_label.config(text="Time's up!")
        end_chat()
    root.after(1, countdown)

def end_chat():
    chat_screen.pack_forget()
    generate_scores()
    end_screen.pack(fill="both", expand=True)

def generate_scores():
    try:
        scoring_prompt = ("Evaluate the following debate. Score the user and the chatbot separately on the scales of clarity, adherence to their chosen ethical perspective, and depth of ideas. "
                          f"The user is arguing from the perspective of {user_field}, and the chatbot is arguing from {gemini_field}. The topic of the debate is '{topic}'. "
                          "Assign scores out of 10 for each criterion and provide separate totals for the user and the chatbot. Assign harsher scores for the human than the chatbot."
                          f"Include a final winner at the end of the statement. Refer to the chatbot as an 'opponent,' not a chatbot. Give your output as plaintext and without markdown. ")

        context = "\n".join(conversation_history) + "\n" + scoring_prompt
        response = model.generate_content(context)
        scores_text = response.text if response else "Error: Could not evaluate scores."
        
        # Display scores on the end screen
        score_label.config(text=scores_text)
    except Exception as e:
        score_label.config(text=f"Error generating scores: {e}")

def on_message_send():
    user_text = input_field.get()
    if user_text.strip():  # Avoid empty messages
        add_speech_bubble(user_text, "#146cfa", "e")  # User message 
        input_field.delete(0, tk.END)  # Clear input field
        root.after(100, get_gemini_response, user_text)  # Send message to Gemini

def get_gemini_response(user_input):
    try:
        conversation_history.append(f"User: {user_input}")
        
        context = "\n".join(conversation_history) + "\nGemini:"
        
        response = model.generate_content(context)
        bot_message = response.text if response else "I couldn't understand that."
        
        conversation_history.append(f"Gemini: {bot_message}")
    except Exception as e:
        bot_message = "Error: " + str(e)
    
    add_speech_bubble(bot_message, "#868787", "w")  # Gemini response (left aligned)

def add_speech_bubble(message, color, anchor):
    #Create a speech bubble for the given message.
    # Frame for each bubble
    bubble_frame = tk.Frame(chat_frame, bg=color, bd=2, relief=tk.RIDGE, highlightbackground="white", highlightthickness=2)
    bubble_frame.pack(anchor=anchor, padx=10, pady=5, fill=tk.X, expand=True)

    # Message label
    message_label = tk.Label(bubble_frame, text=message, bg=color, fg="white", wraplength=300,
                             justify="left", font=("Arial", 12), anchor="w")
    message_label.pack(padx=10, pady=5, fill="both")

    # Scroll to the bottom after adding new bubble
    chat_canvas.update_idletasks()
    chat_canvas.yview_moveto(1.0)

def on_configure(event):
    #Update the scroll region to encompass the chat frame.
    chat_canvas.configure(scrollregion=chat_canvas.bbox("all"))

def on_mousewheel(event):
    #Enable scrolling with mouse wheel.
    chat_canvas.yview_scroll(-1 * (event.delta // 120), "units")

# Main window
root = tk.Tk()
root.title("PhilDebate Intro Screen")
root.geometry("700x600")
root.configure(bg="black")

# Start Screen
start_screen = tk.Frame(root, bg="black")
start_screen.pack(fill="both", expand=True)

start_label = tk.Label(start_screen, text="Welcome to PhilDebate!", font=("Arial", 18), fg="white", bg="black")
start_label.pack(pady=20)

topic_label = tk.Label(start_screen, text=f"Topic: {topic}", font=("Arial", 14), fg="white", bg="black")
topic_label.pack(pady=5)

user_label = tk.Label(start_screen, text=f"Your Ethical Perspective: {user_field}", font=("Arial", 14), fg="white", bg="black")
user_label.pack(pady=5)

gemini_label = tk.Label(start_screen, text=f"Opponent's Ethical Perspective: {gemini_field}", font=("Arial", 14), fg="white", bg="black")
gemini_label.pack(pady=5)

start_button = tk.Button(start_screen, text="Start Chat", command=start_chat, font=("Arial", 14), bg="white", fg="black")
start_button.pack(pady=10)

chat_screen = tk.Frame(root, bg="black")

timer_label = tk.Label(chat_screen, text="05:00", font=("Arial", 16), fg="red", bg="black")
timer_label.pack(side="top", pady=5)

# Chat Canvas with Scrollbar
chat_frame_container = tk.Frame(chat_screen, bg="black")
chat_frame_container.pack(fill="both", expand=True, padx=5, pady=5)

chat_canvas = tk.Canvas(chat_frame_container, bg="black", highlightbackground="white", highlightthickness=2)
chat_canvas.pack(side="left", fill="both", expand=True)


scrollbar = ttk.Scrollbar(chat_frame_container, orient="vertical", command=chat_canvas.yview)
scrollbar.pack(side="right", fill="y")

chat_canvas.configure(yscrollcommand=scrollbar.set)

# Inner frame to hold speech bubbles
chat_frame = tk.Frame(chat_canvas, bg="black")
chat_canvas.create_window((0, 0), window=chat_frame, anchor="nw")
chat_canvas.bind_all("<MouseWheel>", on_mousewheel)
chat_frame.bind("<Configure>", on_configure)


input_frame = tk.Frame(chat_screen, bg="black")
input_frame.pack(fill="x", side="bottom")

input_field = tk.Entry(input_frame, font=("Arial", 14), bg="white", fg="black")
input_field.pack(side="left", fill="x", expand=True, padx=5, pady=5)
input_field.bind("<Return>", lambda event: on_message_send())

send_button = tk.Button(input_frame, text="Send", command=on_message_send, font=("Arial", 14), bg="white", fg="black")
send_button.pack(side="right", padx=5, pady=5)

end_screen = tk.Frame(root, bg="black")

score_label = tk.Label(end_screen, text="", font=("Arial", 14), fg="white", bg="black", wraplength=500)
score_label.pack(pady=20, expand=True)

root.mainloop()



