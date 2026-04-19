import anthropic
import requests
import schedule
import time
import random
import os

ANTHROPIC_API_KEY = "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"
LINKEDIN_ACCESS_TOKEN = "AQWzWcmrlmJ2rhDBz7FrzeeI0Oq2ElfPkpwdicq9gIcaX51W-Hd65AFjO9rm-a9J_NKtASxIZCVxYXfDVOfsdhuYWrFhn_-yg_JYOy2NWiH2gDgAX15U0plQvS1QhPh74GQXn06TKMZIVsdWeC5IQew6ReGzrTRru476OiDcK98u4pw5NMrKu-PY_RWqCRoLyY059G1eozQud3YRfNVVmYTOeU0aWbqOVPkOtUL7uEonOndDUDUqE-ltJTeIIqglOoFmjWpjWzZC4IO3xLT-NrdofpgP_CtiuLNHIu5CHOzh_6a0RDRwqypwg56vqDd-IOXz7-Ao5K48u9hTv4TeOfs-dOnn-w
LINKEDIN_ACCESS_TOKEN=AQWUXa46QTqcAQdoOTOKkzOUpO1Rjx9ZrLh2MYW7yh6ra-DV3XdNVBv3z5E-WyuG1UaDoAp8z9vTPThJCS7K9mv9tJI8ZW42dY_KnY8G9pangG0_6WdYnkl3S3t7oq1q3W8sJVJr-fVTtgsDA04HO3zOsuCoZaTNeUBdAZi9mmTiHdrlS7VLgCLeDIzPZDUA8QWJ1Il1nPeYPU5g48JMLUaJcgDfjHskKunsawTgIqbakFHdjoPYQHVcx047f223llhdLG_r8hPi57PHa27m0TMDIjRg_s7gqq2uYIZkRNLZup97P5g4a1pLNmJX6mlCP1dNkJ9FgVDj615SJ7rdrd1wN4xG0w
LINKEDIN_ACCESS_TOKEN=AQVAJQqLebEW_QREGYN-_QakzMU1FeoM3atoOvLdtQ3qrBxaDJT2d2gfPUiqt3ayrE0nZOl-P1sa4rTNzZvM-I79dN-zV9eSVBTEhP2V67ix06v6y8SfwVwRmZ7n-vn_wnVfE6pfUXNetz9cJBoessxpbyvFkkxPIk8GI3PQQdDbndmQx_MpWPls0wa-p8XfJyanv0Jxffx68_A_cX0_aMtxKxhiIJKhHT3tczwB893pj-jxVJ7auuQBFL2-9jtv594AkaZLdRiWnVBAftoy78-cmQcfFkbvDvaFF47v6G_4ovwIfcEu70HfUvom6tNbk6063JZxudH58EEccYboKDBDCf2lrg
LINKEDIN_ACCESS_TOKEN=AQXS6H49xyd4rRNajhg8yrXS3wYixNuF83XS1vbMHmbALjwXLecYrFF4uQCfBK5l5tTj4pgjsnXrmdIqYyhOP28236yiLPIx1VNPN2SiQJkKJieyybX7HQLylq-jV7VcyVYrJX0NxFO0I55qNorqh3l6KQb95VvTGVzLM9tdEsuv6qWGxUFfioAD24ARlqc-APltn7TsWXoX2jDoqugGvtrLAw2316vNkROOAewSmyvmU7kpioeUS5HQnLlmqqp6I3dAvoZIwX7DMQ2W630eCsJIXQ0QBKNON4EhkLG6tS8CtiX0Wk3aQnPP3-4FYarkBLslKV0vNO_wo-pVXGXeqM-JKw-VeA%"

STAGE_FILE = os.path.join(os.path.dirname(__file__), "stage.txt")
LAST_POST_FILE = os.path.join(os.path.dirname(__file__), "last_post.txt")

PROJECT_CONTEXT = (
    "Bijaya Acharya is a Mechanical Engineering junior at UTA, GPA 3.25, graduating 2027. "
    "International student from Nepal looking for engineering internships.\n\n"
    "He is building a PID Temperature Controlled Fan System as a personal project. "
    "The system automatically adjusts a DC fan speed based on temperature readings using a PID control algorithm.\n\n"
    "Skills being used: SolidWorks for fan mount and enclosure design, Arduino with thermocouple sensor "
    "for temperature reading and PWM fan control, PID algorithm coded in Arduino, LabVIEW for real time "
    "temperature and fan speed monitoring dashboard, MATLAB for PID tuning analysis and step response plots.\n\n"
    "Project stages in order:\n"
    "Stage 1: Got the idea, researching PID control and planning the build\n"
    "Stage 2: Sketching and designing the fan mount and enclosure in SolidWorks\n"
    "Stage 3: Finalized SolidWorks design, figuring out part list and wiring plan\n"
    "Stage 4: Parts arrived, starting to wire Arduino and thermocouple\n"
    "Stage 5: First temperature readings working on serial monitor\n"
    "Stage 6: Fan PWM control working, fan responds to manual input\n"
    "Stage 7: Writing the PID algorithm in Arduino, tuning Kp Ki Kd values\n"
    "Stage 8: Building the LabVIEW dashboard for real time display\n"
    "Stage 9: First full closed loop test, system responding to heat changes\n"
    "Stage 10: Running step response tests, collecting data for MATLAB\n"
    "Stage 11: Analyzing PID tuning results in MATLAB, comparing response curves\n"
    "Stage 12: Final enclosure assembly and full system build\n"
    "Stage 13: Final demo working, documenting results\n"
    "Stage 14: Project complete, wrap up and lessons learned\n"
)

def get_next_stage():
    if os.path.exists(STAGE_FILE):
        with open(STAGE_FILE, "r") as f:
            stage = int(f.read().strip())
    else:
        stage = 1
    next_stage = stage + 1 if stage < 14 else 14
    with open(STAGE_FILE, "w") as f:
        f.write(str(next_stage))
    return stage

def get_last_post():
    if os.path.exists(LAST_POST_FILE):
        with open(LAST_POST_FILE, "r") as f:
            return f.read().strip()
    return ""

def save_last_post(text):
    with open(LAST_POST_FILE, "w") as f:
        f.write(text)

def generate_post():
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    stage = get_next_stage()
    bonus_types = [
        "just post the project update for this stage naturally",
        "post the project update but connect it briefly to a real engineering concept or fact",
        "post the project update and mention something that did not go as planned",
        "post the project update and connect it to a recent real engineering news or achievement found via web search",
    ]
    bonus = random.choice(bonus_types)
    prompt = (
        "You are writing a LinkedIn post for Bijaya Acharya, a Mechanical Engineering junior at UTA.\n\n"
        + PROJECT_CONTEXT
        + "\nCurrent project stage: " + str(stage) + " out of 14"
        + "\nWhat to do: " + bonus
        + "\n\nRules:\n"
        "Write like a real engineering student, grounded and honest, not corporate or hyped.\n"
        "NEVER start with Just, Just finished, Just completed, Excited to share, Thrilled, or any opener like that.\n"
        "Start mid thought as if you are already doing it.\n"
        "No bullet points, no dashes, no asterisks, no em dashes, no special characters of any kind.\n"
        "Plain flowing sentences only like a real person writing.\n"
        "Max 3 sentences total then 3 hashtags on the last line.\n"
        "Keep it short and specific to this stage only, not vague or generic.\n"
        "Do not try to sound impressive or prove too much. One simple honest thought.\n"
        "If this is stage 13 or 14 make it sound like the project is wrapping up naturally.\n"
        "Mention internship search only once across all posts, not every time.\n"
        "End with a question or honest thought that invites a reply.\n"
        "Write only the post, nothing else."
    )
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}]
    )
    for block in message.content:
        if hasattr(block, "text"):
            return block.text
    return message.content[0].text

def get_linkedin_user_id():
    res = requests.get(
        "https://api.linkedin.com/v2/userinfo",
        headers={"Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}"}
    )
    return res.json().get("sub")

def post_to_linkedin():
    print("Generating post...")
    last = get_last_post()
    post_text = generate_post()
    if post_text.strip() == last.strip():
        post_text = generate_post()
    save_last_post(post_text)
    print(f"Post:\n{post_text}\n")
    user_id = get_linkedin_user_id()
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
        print("Posted successfully!")
    else:
        print(f"Failed: {res.status_code} {res.text}")

random_hour = random.randint(8, 20)
random_minute = random.randint(0, 59)
post_time = f"{random_hour:02d}:{random_minute:02d}"
print(f"Next post at {post_time} every 2 days")
schedule.every(2).days.at(post_time).do(post_to_linkedin)
print("Scheduler running!")
while True:
    schedule.run_pending()
    time.sleep(60)
