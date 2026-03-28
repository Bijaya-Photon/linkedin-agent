import anthropic
import requests
import os
import schedule
import time
import random
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")

def generate_post():
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "You are a LinkedIn content creator for Bijaya Acharya, an international student from UTA majoring in Mechanical Engineering, currently a Junior graduating in 2027. He is actively looking for internships. Write a short engaging LinkedIn post about mechanical engineering, student life, or internship search. Casual but professional tone. Max 3 hashtags. Write only the post."}
        ]
    )
    return message.content[0].text

def get_linkedin_user_id():
    res = requests.get(
        "https://api.linkedin.com/v2/userinfo",
        headers={"Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}"}
    )
    return res.json().get("sub")

def post_to_linkedin():
    print("Generating post...")
    post_text = generate_post()
    print(f"Post generated:\n{post_text}\n")
    user_id = get_linkedin_user_id()
    res = requests.post(
        "https://api.linkedin.com/v2/ugcPosts",
        headers={
            "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        },
        json={
            "author": f"urn:li:person:{user_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": post_text},
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
    )
    if res.status_code == 201:
        print("Posted to LinkedIn successfully!")
    else:
        print(f"Error: {res.status_code} {res.text}")

random_hour = random.randint(8, 20)
random_minute = random.randint(0, 59)
post_time = f"{random_hour:02d}:{random_minute:02d}"
print(f"Today's post will go out at {post_time}")
schedule.every().day.at(post_time).do(post_to_linkedin)

print("Scheduler running!")
while True:
    schedule.run_pending()
    time.sleep(60)
