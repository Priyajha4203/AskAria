import csv
import os

def log_feedback(chat_id, feedback):
    os.makedirs("logs", exist_ok=True)
    with open("logs/feedback_log.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([chat_id, feedback])
