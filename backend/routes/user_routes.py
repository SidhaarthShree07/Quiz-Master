# Add this import for AsyncResult
from celery.result import AsyncResult
from flask import Blueprint, request, jsonify, send_from_directory, make_response
from flask import session as flask_session
from werkzeug.security import generate_password_hash
from flask_login import login_required, current_user
from ..models import User, SessionLocal, UserRole, UserQuiz, UserQuizStatus, Subject, Chapter, Quiz, QuizStatus, UserRating
from ..models import Question
import re
import os
from datetime import datetime, date
# Task is now imported in celery_worker.py

user_bp = Blueprint('user_bp', __name__)

# Utility function to update quiz status
def update_quiz_status(quiz):
    today = date.today()
    try:
        quiz_date = datetime.strptime(str(quiz.date), '%Y-%m-%d').date()
    except Exception:
        return
    if quiz_date == today and quiz.status != QuizStatus.ONGOING:
        quiz.status = QuizStatus.ONGOING
    elif quiz_date < today and quiz.status != QuizStatus.EXPIRED:
        quiz.status = QuizStatus.EXPIRED

@user_bp.route('/quizzes/<quiz_id>', methods=['GET'])
def get_quiz_details(quiz_id):
    session = SessionLocal()
    try:
        quiz = session.query(Quiz).filter_by(id=quiz_id).first()
        if not quiz:
            return jsonify({'message': 'Quiz not found'}), 404
        # Update status if needed
        update_quiz_status(quiz)
        session.commit()
        return jsonify({
            'id': quiz.id,
            'name': quiz.name,
            'date': quiz.date,
            'duration': quiz.duration,
            'cost': quiz.cost,
            'status': quiz.status.value if hasattr(quiz.status, 'value') else str(quiz.status)
        })
    finally:
        session.close()

@user_bp.route('/quizzes/<quiz_id>/questions', methods=['GET'])
def get_quiz_questions(quiz_id):
    session = SessionLocal()
    try:
        questions = session.query(Question).filter_by(quiz_id=quiz_id).all()
        result = []
        for q in questions:
            # Check if question_statement contains a space
            statement = q.question_statement
            if ' ' in statement:
                question_statement = statement
            else:
                # Treat as image filename, construct local URL
                image_url = f"http://localhost:5000/api/user/uploads/question_images/{statement}"
                question_statement = image_url
            result.append({
                'id': q.id,
                'question_statement': question_statement,
                'options': [q.option_1, q.option_2, q.option_3, q.option_4],
                'score': q.score
            })
        return jsonify(result)
    finally:
        session.close()

# --- SUBMIT QUIZ ENDPOINT ---
@user_bp.route('/submit-quiz', methods=['POST'])
def submit_quiz():
    data = request.get_json()
    user_id = data.get('user_id')
    quiz_id = data.get('quiz_id')
    answers = data.get('answers', [])
    timestamp = data.get('timestamp')
    if not user_id or not quiz_id or not answers:
        return jsonify({'message': 'Missing data'}), 400
    session = SessionLocal()
    try:
        # Get all questions for quiz
        questions = session.query(Question).filter_by(quiz_id=quiz_id).all()
        q_map = {str(q.id): q for q in questions}
        total_score = 0
        for ans in answers:
            qid = str(ans.get('question_id'))
            selected = ans.get('selected_option')
            print(f"Processing answer for question {qid}, selected: {selected}")
            q = q_map.get(qid)
            if not q:
                continue
            # Debug: print all attributes of q
            print(f"Question object attributes: {q.__dict__}")
            # Correct options: can be multiple, stored as comma-separated string or list in q.correct_options
            correct_opts = []
            raw_correct = getattr(q, 'correct_options', None)
            print(f"Raw correct_options for question {qid}: {raw_correct}")
            # Handle if correct_options is a string like '[1,4]' or '1,4'
            if isinstance(raw_correct, str):
                # Remove brackets if present
                raw_correct = raw_correct.strip('[]')
                correct_opts = [int(x) for x in raw_correct.split(',') if x.strip().isdigit()]
            elif isinstance(raw_correct, list):
                correct_opts = [int(x) for x in raw_correct if isinstance(x, int)]
            print(f"Correct options for question {qid}: {correct_opts}")
            # Map frontend index (0-3) to backend (1-4)
            selected_backend = None
            if selected is not None:
                try:
                    selected_backend = int(selected) + 1
                except Exception:
                    selected_backend = None
            # If selected is None, score is 0
            if selected_backend is None:
                continue
            # If correct_opts is empty, skip
            if not correct_opts:
                continue
            # If selected is array (for multi-select), handle as array
            if isinstance(selected, list):
                selected_set = set([int(s) + 1 for s in selected if isinstance(s, int)])
            else:
                selected_set = set([selected_backend])
            correct_set = set(correct_opts)
            match_count = len(selected_set & correct_set)
            total_correct = len(correct_set)
            if match_count == 0:
                score_awarded = 0
            else:
                score_awarded = float(q.score) * (match_count / total_correct)
            total_score += score_awarded
        # Update UserQuiz row
        uq_id = f"{user_id}_{quiz_id}"
        user_quiz = session.query(UserQuiz).filter_by(id=uq_id).first()
        if user_quiz:
            user_quiz.score = round(total_score, 2)
            user_quiz.timestamp = timestamp
            user_quiz.status = UserQuizStatus.ATTEMPTED
            session.commit()
        return jsonify({'message': 'Quiz submitted', 'score': round(total_score, 2)})
    except Exception as e:
        session.rollback()
        return jsonify({'message': str(e)}), 500
    finally:
        session.close()

# --- SUBMIT RATING ENDPOINT ---
@user_bp.route('/submit-rating', methods=['POST'])
def submit_rating():
    data = request.get_json()
    user_id = data.get('user_id')
    quiz_id = data.get('quiz_id')
    rating = data.get('rating')
    if not user_id or not quiz_id or not rating:
        return jsonify({'message': 'Missing data'}), 400
    session = SessionLocal()
    print(f"Submitting rating: user_id={user_id}, quiz_id={quiz_id}, rating={rating}")
    try:
        print("lets go")
        # Manually set id as max id + 1
        max_id_row = session.query(UserRating.id).order_by(UserRating.id.desc()).first()
        print(f"Max ID: {max_id_row}")
        next_id = (int(max_id_row[0]) + 1) if max_id_row and max_id_row[0] is not None else 1
        print(f"Next UserRating ID: {next_id}")
        ur = UserRating(id=next_id, user_id=user_id, quiz_id=quiz_id, rating=rating)
        session.add(ur)
        session.commit()
        return jsonify({'message': 'Rating submitted'})
    except Exception as e:
        session.rollback()
        return jsonify({'message': str(e)}), 500
    finally:
        session.close()
        
@user_bp.route('/check-username', methods=['GET'])
def check_username():
    username = request.args.get('username')
    if not username:
        return jsonify({'available': False}), 400
    session = SessionLocal()
    try:
        exists = session.query(User).filter_by(username=username).first() is not None
        return jsonify({'available': not exists})
    finally:
        session.close()

@user_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    if not username or not password or not name:
        return jsonify({'message': 'Missing required fields'}), 400
    # Password validation
    if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[^A-Za-z\d]).{8,}$', password):
        return jsonify({'message': 'Password must be at least 8 characters long, contain a letter, a number, and a special character.'}), 400
    session = SessionLocal()
    try:
        # Check for duplicate username
        if session.query(User).filter_by(username=username).first():
            return jsonify({'message': 'Username already exists'}), 409
        user = User(
            id=username,  # or use uuid if preferred
            username=username,
            password=generate_password_hash(password),
            name=name,
            role=UserRole.STUDENT
        )
        session.add(user)
        session.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        session.rollback()
        return jsonify({'message': str(e)}), 500
    finally:
        session.close()

@user_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    if current_user.role.value == 'teacher':
        dashboard_type = 'admin'
    else:
        dashboard_type = 'user'
    is_remembered = False
    if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
        is_fresh = flask_session.get('_fresh', True)
        if not is_fresh:
            is_remembered = True
    return jsonify({
        'dashboard_type': dashboard_type,
        'is_remembered': is_remembered,
        'username': current_user.username
    })

@user_bp.route('/subjects', methods=['GET'])
def get_subjects():
    session = SessionLocal()
    try:
        subjects = session.query(Subject).all()
        result = []
        for subject in subjects:
            result.append({
                'id': subject.id,
                'name': subject.name,
                'image_file_name': subject.image_file_name,
                'color': subject.color
            })
        return jsonify(result)
    finally:
        session.close()

@user_bp.route('/uploads/subject_images/<filename>', methods=['GET'])
def serve_subject_image(filename):
    uploads_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'subject_images')
    return send_from_directory(uploads_dir, filename)

@user_bp.route('/subjects/<subject_id>/chapters', methods=['GET'])
def get_chapters(subject_id):
    session = SessionLocal()
    try:
        chapters = session.query(Chapter).filter_by(subject_id=subject_id).all()
        result = []
        for chapter in chapters:
            quiz_count = session.query(Quiz).filter_by(chapter_id=chapter.id).count()
            result.append({
                'id': chapter.id,
                'name': chapter.name,
                'image_file_name': chapter.image_file_name,
                'quiz_count': quiz_count
            })
        return jsonify(result)
    finally:
        session.close()

@user_bp.route('/uploads/chapter_images/<filename>', methods=['GET'])
def serve_chapter_image(filename):
    uploads_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'chapter_images')
    return send_from_directory(uploads_dir, filename)

@user_bp.route('/chapters/<chapter_id>/quizzes', methods=['GET'])
def get_quizzes_for_chapter(chapter_id):
    status = request.args.get('status', '')
    status_list = [s.strip() for s in status.split(',') if s.strip()]
    session = SessionLocal()
    try:
        query = session.query(Quiz).filter_by(chapter_id=chapter_id)
        if status_list:
            query = query.filter(Quiz.status.in_(status_list))
        quizzes = query.all()
        # Update status for each quiz
        for quiz in quizzes:
            update_quiz_status(quiz)
        session.commit()
        result = []
        for quiz in quizzes:
            question_count = session.query(Question).filter_by(quiz_id=quiz.id).count()
            result.append({
                'id': quiz.id,
                'name': quiz.name,
                'question_count': question_count,
                'date': quiz.date,
                'duration': quiz.duration,
                'cost': quiz.cost,
                'status': quiz.status.value if hasattr(quiz.status, 'value') else str(quiz.status)
            })
        return jsonify(result)
    finally:
        session.close()

@user_bp.route('/register-quiz', methods=['POST'])
def register_quiz():
    data = request.get_json()
    quiz_id = data.get('quiz_id')
    user_id = data.get('user_id')
    if not quiz_id or not user_id:
        return jsonify({'message': 'Missing quiz_id or user_id'}), 400
    session = SessionLocal()
    try:
        # Generate id by joining user_id and quiz_id
        uq_id = f"{user_id}_{quiz_id}"
        # Check if already registered
        existing = session.query(UserQuiz).filter_by(id=uq_id).first()
        if existing:
            return jsonify({'message': 'Already registered'}), 409
        uq = UserQuiz(
            id=uq_id,
            quiz_id=quiz_id,
            user_id=user_id,
            status=UserQuizStatus.BOOKED,
            score=None,
            timestamp=None
        )
        session.add(uq)
        session.commit()
        return jsonify({'message': 'Registered successfully'}), 201
    except Exception as e:
        session.rollback()
        return jsonify({'message': str(e)}), 500
    finally:
        session.close()

@user_bp.route('/user-quizzes/<user_id>', methods=['GET'])
def get_user_quizzes(user_id):
    session = SessionLocal()
    try:
        # Update last_interaction in User table
        user = session.query(User).filter_by(id=user_id).first()
        if user:
            user.last_interaction = datetime.now()
            session.commit()
        user_quizzes = session.query(UserQuiz).filter_by(user_id=user_id).all()
        result = []
        for uq in user_quizzes:
            result.append({
                'quiz_id': uq.quiz_id,
                'status': uq.status.value if hasattr(uq.status, 'value') else str(uq.status)
            })
        return jsonify(result)
    finally:
        session.close()

@user_bp.route('/uploads/question_images/<filename>', methods=['GET'])
def serve_question_image(filename):
    uploads_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'question_images')
    return send_from_directory(uploads_dir, filename)

# --- USER QUIZ SCORES ENDPOINT ---
@user_bp.route('/user/quiz-scores/<user_id>', methods=['GET'])
def get_user_quiz_scores(user_id):
    session = SessionLocal()
    try:
        user_quizzes = session.query(UserQuiz).filter_by(user_id=user_id).all()
        result = []
        for uq in user_quizzes:
            # Get quiz name
            quiz = session.query(Quiz).filter_by(id=uq.quiz_id).first()
            quiz_name = quiz.name if quiz else ''
            # Get total score for quiz (sum of all question scores)
            total_score = session.query(Question).filter_by(quiz_id=uq.quiz_id).with_entities(Question.score).all()
            total_score_sum = sum([float(q.score) for q in total_score if q.score is not None])
            # Get number of questions
            question_count = session.query(Question).filter_by(quiz_id=uq.quiz_id).count()
            # Get rating from UserRating
            rating_obj = session.query(UserRating).filter_by(user_id=user_id, quiz_id=uq.quiz_id).first()
            rating = rating_obj.rating if rating_obj else None
            result.append({
                'quiz_id': uq.quiz_id,
                'quiz_name': quiz_name,
                'question_count': question_count,
                'status': uq.status.value if hasattr(uq.status, 'value') else str(uq.status),
                'date': uq.timestamp,
                'score': uq.score,
                'total_score': total_score_sum,
                'rating': rating, 
                'subject_name': quiz.subject.name if quiz and hasattr(quiz, 'subject') and quiz.subject else ''
            })
        return jsonify(result)
    finally:
        session.close()

# --- USER QUIZ STATISTICS ENDPOINT ---
@user_bp.route('/user/quiz-statistics/<user_id>', methods=['GET'])
def get_user_quiz_statistics(user_id):
    session = SessionLocal()
    try:
        user_quizzes = session.query(UserQuiz).filter_by(user_id=user_id).all()
        subject_count = {}
        avg_score_map = {}
        month_count = {}
        # Get all subjects for reference
        all_subjects = session.query(Subject).all()
        subject_names = {s.id: s.name for s in all_subjects}
        for uq in user_quizzes:
            quiz = session.query(Quiz).filter_by(id=uq.quiz_id).first()
            if not quiz:
                continue
            chapter = session.query(Chapter).filter_by(id=quiz.chapter_id).first() if quiz.chapter_id else None
            subject_id = chapter.subject_id if chapter else None
            subject_name = subject_names.get(subject_id, None)
            if subject_name:
                subject_count[subject_name] = subject_count.get(subject_name, 0) + 1
                if subject_name not in avg_score_map:
                    avg_score_map[subject_name] = {'total': 0, 'count': 0}
                if uq.score is not None:
                    total_score = session.query(Question).filter_by(quiz_id=uq.quiz_id).with_entities(Question.score).all()
                    total_score_sum = sum([float(q.score) for q in total_score if q.score is not None])
                    if total_score_sum > 0:
                        avg_score_map[subject_name]['total'] += (float(uq.score) / total_score_sum) * 100
                        avg_score_map[subject_name]['count'] += 1
            # Month-wise attempted count
            if uq.timestamp:
                try:
                    ts = str(uq.timestamp)
                    # Handle ISO format: '2025-07-29T11:25:41.815Z'
                    if 'T' in ts:
                        date_part = ts.split('T')[0]
                        year, month, *_ = date_part.split('-')
                        month_key = f"{year}-{month}"
                        month_count[month_key] = month_count.get(month_key, 0) + 1
                    else:
                        # Fallback to previous parsing
                        dt = uq.timestamp if isinstance(uq.timestamp, datetime) else datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
                        month_key = f"{dt.year}-{dt.month:02d}"
                        month_count[month_key] = month_count.get(month_key, 0) + 1
                except Exception:
                    pass
        # Ensure all subjects are present in output, even if not attempted
        subjectWise = [
            {'subject_name': s.name, 'attempted_count': subject_count.get(s.name, 0)} for s in all_subjects
        ]
        avgScorePerSubject = [
            {
                'subject_name': s.name,
                'avg_score_percentage': round(avg_score_map[s.name]['total'] / avg_score_map[s.name]['count'], 2) if s.name in avg_score_map and avg_score_map[s.name]['count'] > 0 else 0
            } for s in all_subjects
        ]
        monthWise = [
            {'month': k, 'attempted_count': v} for k, v in sorted(month_count.items())
        ]
        return jsonify({
            'subjectWise': subjectWise,
            'avgScorePerSubject': avgScorePerSubject,
            'monthWise': monthWise
        })
    finally:
        session.close()

# --- EXPORT QUIZ CSV ENDPOINTS ---
# Remove celery task definition from this file

# API endpoint to trigger export job
@user_bp.route('/export-csv', methods=['POST'])
def export_csv():
    user_id = request.json.get('user_id')
    print(f"Received export request for user_id: '{user_id}'")
    
    if not user_id:
        print("Error: No user_id provided")
        return jsonify({'error': 'No user_id provided'}), 400
    
    # Use direct task execution for immediate results
    try:
        from ..tasks import export_user_quizzes_csv
        filename = export_user_quizzes_csv(user_id)
        print(f"Export completed with filename: {filename}")
        if filename:
            download_url = f'/api/user/export-csv-file/{filename}'
            return jsonify({'status': 'done', 'download_url': download_url})
        else:
            return jsonify({'error': 'Export failed - no filename returned'}), 500
    except Exception as e:
        print(f"Error in direct export: {e}")
        return jsonify({'error': str(e)}), 500

# API endpoint to check export job status
@user_bp.route('/export-csv-status/<task_id>', methods=['GET'])
def export_csv_status(task_id):
    # For direct execution, return done immediately
    if task_id == 'direct':
        return jsonify({'status': 'done', 'download_url': '/api/user/export-csv-file/direct'})
    
    # For Celery tasks (if we fix the issue later)
    from ..celery_worker import celery
    task = celery.AsyncResult(task_id)
    if task.state == 'SUCCESS':
        filename = task.result
        download_url = f'/api/user/export-csv-file/{filename}'
        return jsonify({'status': 'done', 'download_url': download_url})
    return jsonify({'status': task.state})


# API endpoint to download CSV file
@user_bp.route('/export-csv-file/<filename>', methods=['GET'])
def export_csv_file(filename):
    # Flask app runs from root directory, so exports is in backend/exports
    export_dir = os.path.join(os.path.dirname(__file__), '..', 'exports')
    print(f"DEBUG: export_csv_file called with filename: {filename}")
    print(f"DEBUG: export_dir: {export_dir}")
    print(f"DEBUG: full path: {os.path.join(export_dir, filename)}")
    print(f"DEBUG: file exists: {os.path.exists(os.path.join(export_dir, filename))}")
    # Check if file exists
    filepath = os.path.join(export_dir, filename)
    if os.path.exists(filepath):
        return send_from_directory(export_dir, filename, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404


# --- USER ACTIVE TAB CACHE ENDPOINTS ---

# --- GLOBAL CORS 404 HANDLER FOR OPTIONS PRE-FLIGHT ---
from flask import current_app
from ..tasks import cache_user_active_tab

## NOTE: If your blueprint is registered with url_prefix='/api/user',
@user_bp.route('/active-tab', methods=['POST', 'OPTIONS'])
def set_active_tab():
    if request.method == 'OPTIONS':
        response = make_response('', 200)
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    data = request.get_json()
    user_id = data.get('user_id')
    tab = data.get('tab')
    if not user_id or not tab:
        return jsonify({'error': 'Missing user_id or tab'}), 400
    try:
        # Use Redis directly instead of Celery
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        cache_key = f"user_active_tab:{user_id}"
        r.set(cache_key, tab)
        response = jsonify({'status': 'success'})
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    except Exception as e:
        print(f"Redis caching failed: {e}")
        return jsonify({'error': 'Redis caching unavailable', 'details': str(e)}), 500

@user_bp.route('/active-tab/<user_id>', methods=['GET'])
def get_active_tab(user_id):
    try:
        # Use Redis directly instead of Celery
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        cache_key = f"user_active_tab:{user_id}"
        cached = r.get(cache_key)
        if cached:
            # Redis returns bytes, decode to str
            tab = cached.decode() if isinstance(cached, bytes) else str(cached)
        else:
            tab = None
        return jsonify({'tab': tab or 'home'})
    except Exception as e:
        print(f"Redis caching failed: {e}")
        return jsonify({'error': 'Redis caching unavailable', 'details': str(e)}), 500

# --- USER PROFILE ENDPOINTS ---

@user_bp.route('/profile/<user_id>', methods=['GET'])
def get_user_profile(user_id):
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        # Check if image exists in uploads/user_images, else use default.png
        image_folder = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'user_images')
        image_filename = user.image_file_name if getattr(user, 'image_file_name', None) else 'default.png'
        image_path = os.path.join(image_folder, image_filename)
        if not os.path.exists(image_path):
            image_filename = 'default.png'
        dob_val = getattr(user, 'dob', '')
        dob_str = ''
        if dob_val:
            try:
                dob_str = dob_val.strftime('%Y-%m-%d')
            except Exception:
                dob_str = str(dob_val)
        return jsonify({
            'username': user.username,
            'role': user.role.value if hasattr(user.role, 'value') else str(user.role),
            'name': user.name,
            'email': getattr(user, 'email', ''),
            'dob': dob_str,
            'qualification': getattr(user, 'qualification', ''),
            'image_file_name': image_filename
        })
    finally:
        session.close()

@user_bp.route('/profile/<user_id>', methods=['PUT'])
def update_user_profile(user_id):
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        # Get form data (for image upload, use request.files)
        name = request.form.get('name')
        email = request.form.get('email')
        dob = request.form.get('dob')
        qualification = request.form.get('qualification')
        image = request.files.get('image')
        # Update fields if provided
        if name: user.name = name
        if email: user.email = email
        if dob:
            try:
                # Accepts 'YYYY-MM-DD' from HTML date input
                user.dob = datetime.strptime(dob, '%Y-%m-%d').date()
            except Exception:
                pass
        if qualification: user.qualification = qualification
        # Handle image upload
        if image:
            image_folder = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'user_images')
            os.makedirs(image_folder, exist_ok=True)
            filename = f"{user_id}_{image.filename}"
            image_path = os.path.join(image_folder, filename)
            image.save(image_path)
            user.image_file_name = filename
        session.commit()
        return jsonify({'message': 'Profile updated successfully'})
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

# --- SERVE USER IMAGE ENDPOINT ---
@user_bp.route('/uploads/user_images/<filename>', methods=['GET'])
def serve_user_image(filename):
    uploads_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'user_images')
    return send_from_directory(uploads_dir, filename)