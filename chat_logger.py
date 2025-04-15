import csv
import os

def log_chat(question, answer, scores=None):
    os.makedirs("logs", exist_ok=True)
    with open("logs/chat_log.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([question, answer, scores])
