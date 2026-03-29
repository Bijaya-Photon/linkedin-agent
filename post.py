import anthropic
import requests
import os
import schedule
import time
import random
import smtplib
import tempfile
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

PROJECT_CONTEXT = """
Bijaya is working on a personal project called Smart Environmental Monitor for Mechanical Systems.
The project monitors a running motor using temperature sensors, humidity sensors, and accelerometers.
He is designing the sensor enclosure in SolidWorks, wiring sensors with Arduino, collecting data with LabVIEW DAQ, and analyzing results in MATLAB.

Project timeline being followed:
Week 1: Came up with the idea, researching sensors and doing initial sketches
Week 2: Designing the enclosure in SolidWorks, figuring out sensor placement
Week 3: Got the Arduino wired up with DHT11 temp sensor and MPU6050 accelerometer
Week 4: Connected everything to LabVIEW DAQ, first data collection attempt
Week 5: Running FFT analysis in MATLAB, finding interesting vibration patterns
Week 6: Comparing baseline vs abnormal motor behavior in the data
Week 7 onwards: Refining, fixing problems, sharing findings

Current week: randomly pick a week between 1 and 7 and post accordingly.
"""

def send_email_notification(post_text, had_image):
    try:
        msg = MIMEMultipart()
        msg["From"] = GMAIL_USER
        msg["To"] = "bxa4754@mavs.uta.edu"
        msg["Subject"] = "LinkedIn Post Published!"
        image_note = "with an image" if had_image else "without an image"
        body = f"Your LinkedIn post was just published {image_note}!\n\n---\n\n{post_text}\n\n---\n\nKeep building!"
        msg.attach(MIMEText(body, "plain"))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, "bxa4754@mavs.uta.edu", msg.as_string())
        server.quit()
        print("Email notification sent!")
    except Exception as e:
        print(f"Email failed: {e}")

def get_image_for_post(post_text):
    try:
        keywords = ["mechanical engineering", "Arduino sensors", "SolidWorks CAD", "LabVIEW data", "MATLAB analysis", "engineering lab", "circuit board", "motor engineering"]
        query = random.choice(keywords)
        res = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": PEXELS_API_KEY},
            params={"query": query, "per_page": 10, "orientation": "landscape"}
        )
        photos = res.json().get("photos", [])
        if photos:
            photo = random.choice(photos)
            image_url = photo["src"]["large"]
            image_data = requests.get(image_url).content
            return image_data
        return None
    except Exception as e:
        print(f"Image fetch failed: {e}")
        return None

def upload_image_to_linkedin(image_data, user_id):
    try:
        register_res = requests.post(
            "https://api.linkedin.com/v2/assets?action=registerUpload",
            headers={
                "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "owner": f"urn:li:person:{user_id}",
                    "serviceRelationships": [{
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }]
                }
            }
        )
        upload_data = register_res.json()
        asset = upload_data["value"]["asset"]
        upload_url = upload_data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]

        requests.put(
            upload_url,
            headers={
                "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
                "Content-Type": "image/jpeg"
            },
            data=image_data
        )
        return asset
    except Exception as e:
        print(f"Image upload failed: {e}")
        return None

def generate_post():
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": f"""You are a LinkedIn content creator for Bijaya Acharya, a Mechanical Engineering junior at UTA GPA 3.25 graduating 2027. International student from Nepal, looking for engineering internships.

{PROJECT_CONTEXT}

Post types to rotate between:
1. Project update on the Smart Environmental Monitor, specific to the current week in the timeline
2. Something new discovered in LabVIEW or MATLAB during the project
3. A real recent breakthrough in Mechanical Engineering from a real source like MIT, NASA, GE, or a journal, related to what he is working on
4. A short motivational or honest reflection about being an engineering student or international student
5. Something specific about SolidWorks design challenge he hit while designing the enclosure

Rules:
Write like a real curious engineering student not corporate or AI.
Never use bullet points, dashes, asterisks, or any special characters.
No em dashes or hyphens connecting sentences.
Plain flowing sentences like a real person talking.
Fresh and specific every time, not generic.
Short and punchy, max 4 sentences plus hashtags.
End with a question or reaction to boost engagement.
Mention internship search naturally only once every 5 posts.
Max 3 hashtags no formatting around them.
Make it sound like real ongoing work not made up.
Write only the post nothing else."""}
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
    current_hour = datetime.now().hour
    is_daytime = 9 <= current_hour <= 19

    asset = None
    if is_daytime:
        print("Daytime post, fetching image...")
        image_data = get_image_for_post(post_text)
        if image_data:
            asset = upload_image_to_linkedin(image_data, user_id)

    if asset:
        post_body = {
            "author": f"urn:li:person:{user_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": post_text},
                    "shareMediaCategory": "IMAGE",
                    "media": [{
                        "status": "READY",
                        "description": {"text": "Engineering project update"},
                        "media": asset,
                        "title": {"text": "Smart Environmental Monitor"}
                    }]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
    else:
        post_body = {
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

    res = requests.post(
        "https://api.linkedin.com/v2/ugcPosts",
        headers={
            "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        },
        json=post_body
    )

    if res.status_code == 201:
        print("Posted to LinkedIn successfully!")
        send_email_notification(post_text, asset is not None)
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

print("Scheduler running!")
while True:
    schedule.run_pending()
    time.sleep(60)
