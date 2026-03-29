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
            {"role": "user", "content": "You are a LinkedIn content creator for Bijaya Acharya, a Mechanical Engineering junior at UT Arlington graduating in 2027. International student from Nepal, looking for engineering internships.His skills: AutoCAD, SolidWorks, MATLAB, LabVIEW, Arduino, Python, GD&T, DAQ systems, thermocouple sensors, servo motors.Rotate between these post ideas every time, never repeat the same topic twice in a row:Something new he tried in SolidWorks like a new feature, design trick, or assembly technique.A cool thing he detected or measured using LabVIEW or DAQ like vibration, frequency, temperature, or flow rate.A small Arduino or sensor experiment he ran and what he found.A real recent breakthrough in Mechanical Engineering happening in the world and how it connects to what he is learning.A short take on new manufacturing or materials technology like 3D printing, composite materials, EV components, or robotics.A quick lesson from MATLAB or data analysis that surprised him.Life as an international engineering student, short and real.Rules:Write like a curious hands-on engineering student who loves discovering new things.Never use bullet points, dashes, asterisks, or any special characters anywhere in the post.Never use em dashes or hyphens to connect sentences.Write in plain flowing sentences like a real person texting or talking.Make it feel fresh and specific every time, not generic or robotic.Short and punchy, max 4 sentences plus hashtags.End with a question or reaction to get engagement.Mention internship search naturally only once every 4 posts.Max 3 hashtags, no special formatting around them.Write only the post, nothing else."}
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

post_to_linkedin()

random_hour1 = random.randint(0, 2)
random_minute1 = random.randint(0, 59)
post_time1 = f"{random_hour1:02d}:{random_minute1:02d}"

random_hour2 = random.randint(9, 19)
random_minute2 = random.randint(0, 59)
post_time2 = f"{random_hour2:02d}:{random_minute2:02d}"

print(f"Today's posts will go out at {post_time1} and {post_time2}")
schedule.every().day.at(post_time1).do(post_to_linkedin)
schedule.every().day.at(post_time2).do(post_to_linkedin)
