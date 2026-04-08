import random

base_template = '''from pydantic import BaseModel
from typing import List, Optional

class LegalTask(BaseModel):
    name: str
    difficulty: str
    clause: str
    simplified_text_keywords: List[str]
    risk: str
    key_points_keywords: List[str]

TASKS = [
    LegalTask(
        name="late_payment_penalty",
        difficulty="easy",
        clause="Any payment not received within five (5) business days of the due date shall be subject to a late fee of 5% of the outstanding balance.",
        simplified_text_keywords=["late", "fee", "5%", "5 days"],
        risk="NOT SAFE",
        key_points_keywords=["late fee", "5%", "5 business days"]
    ),
    LegalTask(
        name="termination_notice",
        difficulty="medium",
        clause="Either party may terminate this agreement upon sixty (60) days' prior written notice to the other party. In the event of termination by the Client without cause, the Client shall pay a termination fee equal to one month's service fees.",
        simplified_text_keywords=["terminate", "60 days", "notice", "one month fee", "without cause"],
        risk="NOT SAFE",
        key_points_keywords=["60 days notice", "termination fee", "one month fee"]
    ),
    LegalTask(
        name="indemnification_complexity",
        difficulty="hard",
        clause="Provider shall indemnify, defend, and hold harmless Client from and against any and all third-party claims, liabilities, losses, and expenses (including reasonable attorneys' fees) arising out of or related to Provider's gross negligence or willful misconduct, provided that Client promptly notifies Provider in writing of such claim.",
        simplified_text_keywords=["indemnify", "defend", "third-party claims", "gross negligence", "prompt notice"],
        risk="SAFE",
        key_points_keywords=["indemnification", "third-party claims", "gross negligence", "prompt notice"]
    )
'''

def generate_late_payment(index):
    days = random.randint(1, 30)
    fee = random.randint(1, 20)
    return f"""    LegalTask(
        name="late_payment_penalty_{index}",
        difficulty="easy",
        clause="Any payment not received within {days} business days of the due date shall be subject to a late fee of {fee}% of the outstanding balance.",
        simplified_text_keywords=["late", "fee", "{fee}%", "{days} days"],
        risk="NOT SAFE",
        key_points_keywords=["late fee", "{fee}%", "{days} business days"]
    )"""

def generate_termination(index):
    days = random.randint(15, 120)
    return f"""    LegalTask(
        name="termination_notice_{index}",
        difficulty="medium",
        clause="Either party may terminate this agreement upon {days} days' prior written notice to the other party. In the event of termination by the Client without cause, the Client shall pay a termination fee equal to one month's service fees.",
        simplified_text_keywords=["terminate", "{days} days", "notice", "one month fee", "without cause"],
        risk="NOT SAFE",
        key_points_keywords=["{days} days notice", "termination fee", "one month fee"]
    )"""

def generate_indemnification(index):
    return f"""    LegalTask(
        name="indemnification_complexity_{index}",
        difficulty="hard",
        clause="Provider shall indemnify, defend, and hold harmless Client from and against any and all third-party claims, liabilities, losses, and expenses (including reasonable attorneys' fees) arising out of or related to Provider's gross negligence or willful misconduct, provided that Client promptly notifies Provider in writing of such claim.",
        simplified_text_keywords=["indemnify", "defend", "third-party claims", "gross negligence", "prompt notice"],
        risk="SAFE",
        key_points_keywords=["indemnification", "third-party claims", "gross negligence", "prompt notice"]
    )"""

tasks_str = []
for i in range(1, 35):
    tasks_str.append(generate_late_payment(i))
    tasks_str.append(generate_termination(i))
    tasks_str.append(generate_indemnification(i))

file_content = base_template + ",\n" + ",\n".join(tasks_str) + "\n]\n"

with open("tasks.py", "w") as f:
    f.write(file_content)

print(f"Generated {3 + len(tasks_str)} test cases in tasks.py!")
