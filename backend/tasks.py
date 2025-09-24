# Email sending utility
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import csv
import requests
from datetime import datetime, timedelta
from celery import shared_task
from enum import Enum

# Use models and SessionLocal from backend.models or relative import
try:
    from backend.models import SessionLocal, User, Quiz, UserQuiz, Question
except ImportError:
    from models import SessionLocal, User, Quiz, UserQuiz, Question
# --- USER ACTIVE TAB CACHE TASK ---
from celery import current_app

@shared_task(ignore_results=False, name="cache_user_active_tab")
def cache_user_active_tab(user_id, tab=None):
    import redis
    r = redis.Redis(host='localhost', port=6379, db=0)
    cache_key = f"user_active_tab:{user_id}"
    if tab is not None:
        r.set(cache_key, tab)
        return f"Tab '{tab}' cached for user {user_id}"
    else:
        cached = r.get(cache_key)
        if cached:
            # Redis returns bytes, decode to str
            return cached.decode() if isinstance(cached, bytes) else str(cached)
        return None

GOOGLE_CHAT_WEBHOOK_URL = ""

@shared_task(ignore_results=False, name="export_user_quizzes_csv")
def export_user_quizzes_csv(user_id):
    session = SessionLocal()
    try:
        quizzes = session.query(UserQuiz).filter_by(user_id=user_id).all()
        filename = f"user_{user_id}_quizzes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        # Always use backend/exports directory
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        export_dir = os.path.join(backend_dir, 'exports')
        os.makedirs(export_dir, exist_ok=True)
        filepath = os.path.join(export_dir, filename)
        print(f"[DEBUG] Writing CSV to: {filepath}")
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["quiz_id", "chapter_id", "date_of_quiz", "score", "remarks"])
            for uq in quizzes:
                quiz = session.query(Quiz).filter_by(id=uq.quiz_id).first()
                writer.writerow([
                    uq.quiz_id,
                    quiz.chapter_id if quiz else "",
                    uq.timestamp,
                    uq.score,
                    uq.status.name if hasattr(uq.status, 'name') else str(uq.status)
                ])
        print(f"[DEBUG] CSV file created: {filepath}")
        return filename
    finally:
        session.close()

@shared_task(ignore_results=False, name="send_daily_gchat_reminders")
def send_daily_gchat_reminders():
    print("[DEBUG] send_daily_gchat_reminders task starting...")
    session = SessionLocal()
    try:
        # Get latest quiz created_at
        latest_quiz = session.query(Quiz).order_by(Quiz.created_at.desc()).first()
        latest_quiz_time = latest_quiz.created_at if latest_quiz else None
        if not latest_quiz_time:
            print("[DEBUG] No quizzes found.")
            return "No quizzes found."
        
        # Get all users
        users = session.query(User).all()
        reminder_list = []
        for user in users:
            email = getattr(user, 'email', None)
            if not email:
                continue
            last_interaction = getattr(user, 'last_interaction', None)
            if last_interaction is None or last_interaction < latest_quiz_time:
                reminder_list.append(user)
        
        print(f"[DEBUG] Users to remind: {[u.email for u in reminder_list]}")
        
        # For each user, find quizzes added since their last interaction
        for user in reminder_list:
            last_interaction = getattr(user, 'last_interaction', None)
            # Get quizzes newer than last_interaction
            if last_interaction:
                new_quizzes = session.query(Quiz).filter(Quiz.created_at > last_interaction).all()
            else:
                new_quizzes = session.query(Quiz).all()
            
            quiz_names = [q.name for q in new_quizzes]
            if quiz_names:
                content = f"Hi {user.name or user.username}, new quizzes have been added since your last visit!\nQuizzes: " + ", ".join(quiz_names)
            else:
                content = f"Hi {user.name or user.username}, new quizzes have been added since your last visit!"
            
            # Send G-Chat message using webhook
            payload = {
                "text": content + f"\n(Your registered email: {user.email})"
            }
            print(f"[DEBUG] Sending G-Chat reminder to {user.email}: {content}")
            response = requests.post(GOOGLE_CHAT_WEBHOOK_URL, json=payload)
            print(f"[DEBUG] Sent G-Chat reminder to {user.email} | Status: {response.status_code}")
        
        print(f"[DEBUG] Reminders sent to {len(reminder_list)} users.")
        return f"Reminders sent to {len(reminder_list)} users."
    except Exception as e:
        print(f"[DEBUG] Error in send_daily_gchat_reminders: {e}")
        return f"Error: {str(e)}"
    finally:
        session.close()

@shared_task(ignore_results=False, name="simple_test_task")
def simple_test_task(message):
    """Simple test task to verify Celery is working"""
    print(f"Simple test task received: {message}")
    return f"Task completed with message: {message}"

def send_email(to_email, subject, html_content):
    # Configure your SMTP server here
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    SMTP_USER = ''  # Replace with your email
    SMTP_PASS = ''  # Replace with your app password
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(html_content, 'html'))
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, to_email, msg.as_string())
        server.quit()
        print(f"[DEBUG] Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"[DEBUG] Failed to send email to {to_email}: {e}")
        return False

# Monthly report task
@shared_task(ignore_results=False, name="send_monthly_user_report")
def send_monthly_user_report():
    print("[DEBUG] send_monthly_user_report task starting...")
    session = SessionLocal()
    try:
        now = datetime.now()
        month_start = datetime(now.year, now.month, 1)
        month_end = datetime(now.year, now.month, 1) + timedelta(days=32)
        month_end = datetime(month_end.year, month_end.month, 1)
        users = session.query(User).all()
        for user in users:
            quizzes_taken = session.query(UserQuiz).filter(
                UserQuiz.user_id == user.id,
                UserQuiz.timestamp >= month_start.strftime('%Y-%m-%d'),
                UserQuiz.timestamp < month_end.strftime('%Y-%m-%d')
            ).all()
            total_quizzes = len(quizzes_taken)
            user_score_sum = 0
            user_total_possible = 0
            quiz_details = []
            for uq in quizzes_taken:
                quiz = session.query(Quiz).filter_by(id=uq.quiz_id).first()
                # Sum all 'score' in Question table for this quiz id
                quiz_total = session.query(Question).filter_by(quiz_id=uq.quiz_id).with_entities(
                    Question.score).all()
                quiz_total_sum = sum(float(q[0]) for q in quiz_total) if quiz_total else 0
                user_score_sum += float(uq.score) if uq.score is not None else 0
                user_total_possible += quiz_total_sum
                quiz_details.append({
                    'name': quiz.name if quiz else '',
                    'score': uq.score,
                    'status': uq.status.name if hasattr(uq.status, 'name') else str(uq.status)
                })
            avg_score_percent = round((user_score_sum / user_total_possible) * 100, 2) if user_total_possible else 0
            # Ranking: number of users with higher avg_score_percent this month
            all_users = session.query(User).all()
            user_avg_percents = []
            for u in all_users:
                u_quizzes = session.query(UserQuiz).filter(
                    UserQuiz.user_id == u.id,
                    UserQuiz.timestamp >= month_start.strftime('%Y-%m-%d'),
                    UserQuiz.timestamp < month_end.strftime('%Y-%m-%d')
                ).all()
                u_score_sum = 0
                u_total_possible = 0
                for uq in u_quizzes:
                    quiz = session.query(Quiz).filter_by(id=uq.quiz_id).first()
                    quiz_total = session.query(Question).filter_by(quiz_id=uq.quiz_id).with_entities(
                        Question.score).all()
                    quiz_total_sum = sum(float(q[0]) for q in quiz_total) if quiz_total else 0
                    u_score_sum += float(uq.score) if uq.score is not None else 0
                    u_total_possible += quiz_total_sum
                u_percent = (u_score_sum / u_total_possible) * 100 if u_total_possible else 0
                user_avg_percents.append((u.id, u_percent))
            # Sort by percent descending, assign rank by position
            user_avg_percents_sorted = sorted(user_avg_percents, key=lambda x: x[1], reverse=True)
            print(user_avg_percents_sorted)
            user_rank = next((idx + 1 for idx, (uid_cmp, percent_cmp) in enumerate(user_avg_percents_sorted) if uid_cmp == user.id), len(user_avg_percents_sorted))
            # Read HTML template and fill placeholders
            template_path = os.path.join(os.path.dirname(__file__), 'monthly_report_template.html')
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            quiz_rows = ''.join([
                f"<tr><td>{qd['name']}</td><td>{qd['score']}</td><td>{qd['status']}</td></tr>" for qd in quiz_details
            ])
            html = template.replace('{{name}}', user.name or user.username)
            html = html.replace('{{month_year}}', now.strftime('%B %Y'))
            html = html.replace('{{total_quizzes}}', str(total_quizzes))
            html = html.replace('{{avg_score}}', str(avg_score_percent) + ' %')
            html = html.replace('{{user_rank}}', str(user_rank))
            html = html.replace('{{quiz_rows}}', quiz_rows)
            if user.email:
                send_email(user.email, f"Your Monthly Quiz Report - {now.strftime('%B %Y')}", html)
        print("[DEBUG] Monthly reports sent.")
        return "Monthly reports sent."
    except Exception as e:
        print(f"[DEBUG] Error in send_monthly_user_report: {e}")
        return f"Error: {str(e)}"
    finally:
        session.close()