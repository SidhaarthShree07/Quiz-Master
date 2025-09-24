from sqlalchemy import func
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from ..models import SessionLocal, Subject, Chapter, Quiz, UserRole, User, UserQuiz, UserRating, Question
from datetime import date, datetime
from ..models import QuizStatus
import os 
import uuid

admin_bp = Blueprint('admin_bp', __name__)

# --- Stats APIs for dashboard ---
@admin_bp.route('/stats/subject-top-scorers', methods=['GET'])
@login_required
def subject_top_scorers():
    if current_user.role.value != 'teacher':
        return jsonify({'message': 'Forbidden'}), 403
    session = SessionLocal()
    try:
        subjects = session.query(Subject).all()
        # Step 1: Build subject_id -> total_marks dictionary using relationships
        subject_total_marks = {}
        for subject in subjects:
            total_marks = 0
            print(f"Subject: {subject.name} ({subject.id})")
            for chapter in subject.chapters:
                print(f"  Chapter: {chapter.name} ({chapter.id})")
                for quiz in chapter.quizzes:
                    print(f"    Quiz: {quiz.name} ({quiz.id})")
                    for question in quiz.questions:
                        try:
                            score_val = int(question.score or 0)
                        except:
                            score_val = 0
                        print(f"      Question: {question.id}, Score: {score_val}")
                        total_marks += score_val
            subject_total_marks[subject.id] = total_marks
            print(f"Subject {subject.name} ({subject.id}) total marks: {total_marks}")

        # Step 2: Build subject_id -> {user_id: total_score} dictionary using relationships
        subject_user_scores = {sub.id: {} for sub in subjects}
        user_quizzes = session.query(UserQuiz).filter(UserQuiz.status=='ATTEMPTED').all()
        for uq in user_quizzes:
            quiz = uq.quiz
            if not quiz:
                continue
            chapter = quiz.chapter
            if not chapter:
                continue
            subject = chapter.subject
            if not subject:
                continue
            subject_id = subject.id
            user = uq.user
            if not user:
                continue
            score_raw = uq.score
            if score_raw is None:
                score = 0
            elif isinstance(score_raw, int):
                score = score_raw
            else:
                try:
                    score = int(float(score_raw))
                except:
                    score = 0
            print(f"UserQuiz {uq.id}: User {user.username} ({user.id}) scored {score} in quiz {quiz.id} for subject {subject.name} ({subject_id}) (raw: {score_raw})")
            subject_user_scores[subject_id][user.username] = subject_user_scores[subject_id].get(user.username, 0) + score

        print(f"Subject user scores: {subject_user_scores}")

        # Step 3: For each subject, get top 3 users by score and calculate percent
        result = []
        for subject in subjects:
            sub_id = subject.id
            total_marks = subject_total_marks.get(sub_id, 0)
            user_scores = subject_user_scores.get(sub_id, {})
            user_percent = []
            for username, score in user_scores.items():
                percent = (score / total_marks * 100) if total_marks > 0 else 0
                print(f"User {username} scored {score} out of {total_marks} ({percent}%) for subject {subject.name}")
                user_percent.append({
                    'username': username,
                    'percent': round(percent, 2),
                    'score': score
                })
            top_3 = sorted(user_percent, key=lambda x: x['score'], reverse=True)[:3]
            print(f"Subject {subject.name} top 3: {top_3}")
            result.append({
                'subject': subject.name,
                'top_scorers': top_3
            })
        return jsonify(result)
    finally:
        session.close()

@admin_bp.route('/stats/subject-quiz-attempts', methods=['GET'])
@login_required
def subject_quiz_attempts():
    if current_user.role.value != 'teacher':
        return jsonify({'message': 'Forbidden'}), 403
    session = SessionLocal()
    try:
        subjects = session.query(Subject).all()
        result = []
        for subject in subjects:
            chapters = subject.chapters
            quizzes = []
            for chapter in chapters:
                quizzes.extend(chapter.quizzes)
            quiz_ids = [q.id for q in quizzes]
            user_quizzes = session.query(UserQuiz).filter(UserQuiz.quiz_id.in_(quiz_ids)).all()
            user_attempts = {}
            for uq in user_quizzes:
                user = uq.user
                if not user:
                    continue
                user_attempts[user.username] = user_attempts.get(user.username, 0) + 1
            result.append({
                'subject': subject.name,
                'attempts': user_attempts
            })
        return jsonify(result)
    finally:
        session.close()

@admin_bp.route('/stats/monthly-revenue', methods=['GET'])
@login_required
def monthly_revenue():
    if current_user.role.value != 'teacher':
        return jsonify({'message': 'Forbidden'}), 403
    session = SessionLocal()
    try:
        monthly = {}
        user_quizzes = session.query(UserQuiz).all()
        for uq in user_quizzes:
            quiz = uq.quiz
            if not quiz:
                continue
            dt = uq.timestamp
            if not dt:
                continue
            try:
                month = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m')
            except:
                try:
                    month = datetime.strptime(dt, '%Y-%m-%d').strftime('%Y-%m')
                except:
                    month = str(dt)[:7]
            try:
                cost = float(quiz.cost or 0)
            except:
                cost = 0
            monthly[month] = monthly.get(month, 0) + cost
        result = [{'month': k, 'revenue': v} for k, v in sorted(monthly.items())]
        return jsonify(result)
    finally:
        session.close()

@admin_bp.route('/stats/summary', methods=['GET'])
@login_required
def stats_summary():
    if current_user.role.value != 'teacher':
        return jsonify({'message': 'Forbidden'}), 403
    session = SessionLocal()
    try:
        total_users = session.query(User).filter(User.role != UserRole.TEACHER).count()
        # Count all quizzes (across all chapters)
        total_quizzes = session.query(Quiz).count()
        avg_rating = session.query(func.avg(UserRating.rating)).scalar() or 0
        return jsonify({
            'total_users': total_users,
            'total_quizzes': total_quizzes,
            'avg_rating': round(avg_rating, 2)
        })
    finally:
        session.close()
        
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
    else:
        quiz.status = QuizStatus.UPCOMING

@admin_bp.route('/user/info', methods=['GET'])
@login_required
def get_user_info():
    return jsonify({
        'username': current_user.username,
        'role': current_user.role.value
    })
# Delete question endpoint
@admin_bp.route('/questions/<question_id>', methods=['DELETE'])
@login_required
def delete_question(question_id):
    if current_user.role.value != 'teacher':
        return jsonify({'message': 'Forbidden: Only teachers can delete questions.'}), 403
    session = SessionLocal()
    try:
        question = session.query(Question).filter_by(id=question_id).first()
        if not question:
            return jsonify({'message': 'Question not found.'}), 404
        session.delete(question)
        session.commit()
        return jsonify({'message': 'Question deleted successfully.'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'message': str(e)}), 500
    finally:
        session.close()
        
# Get single question details for editing
@admin_bp.route('/questions/<question_id>', methods=['GET'])
@login_required
def get_question(question_id):
    if current_user.role.value != 'teacher':
        return jsonify({'message': 'Forbidden: Only teachers can view questions.'}), 403

    session = SessionLocal()
    try:
        question = session.query(Question).filter_by(id=question_id).first()
        if not question:
            return jsonify({'message': 'Question not found.'}), 404

        # Determine type based on content of question_statement
        if question.question_statement and ' ' in question.question_statement.strip():
            statement_type = 'text'
        else:
            statement_type = 'image'

        return jsonify({
            'id': question.id,
            'question_title': question.question_title,
            'question_type': statement_type,
            'question_statement': question.question_statement,
            'option_1': question.option_1,
            'option_2': question.option_2,
            'option_3': question.option_3,
            'option_4': question.option_4,
            'correct_options': question.correct_options,
            'score': question.score
        })
    finally:
        session.close()


# Edit question endpoint (PUT)
@admin_bp.route('/questions/<question_id>', methods=['PUT'])
@login_required
def edit_question(question_id):
    if current_user.role.value != 'teacher':
        return jsonify({'message': 'Forbidden: Only teachers can edit questions.'}), 403
    session = SessionLocal()
    try:
        question = session.query(Question).filter_by(id=question_id).first()
        if not question:
            return jsonify({'message': 'Question not found.'}), 404
        # Accept partial updates
        question_statement_type = request.form.get('question_type')
        question_title = request.form.get('question_title')
        question_statement_image = request.files.get('question_statement_image')
        question_statement = request.form.get('question_statement')
        option_1 = request.form.get('option_1')
        option_2 = request.form.get('option_2')
        option_3 = request.form.get('option_3')
        option_4 = request.form.get('option_4')
        correct_options = request.form.get('correct_options')
        score = request.form.get('score')
        # Only update fields if provided
        if question_statement_type:
            question.question_statement_type = question_statement_type
        if question_title:
            question.question_title = question_title
        if question_statement:
            question.question_statement = question_statement
        if question_statement_type == 'image' and question_statement_image:
            upload_folder = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'question_images')
            os.makedirs(upload_folder, exist_ok=True)
            image_path = os.path.join(upload_folder, question_statement_image.filename)
            question_statement_image.save(image_path)
            question.question_statement = question_statement_image.filename
        if option_1:
            question.option_1 = option_1
        if option_2:
            question.option_2 = option_2
        if option_3:
            question.option_3 = option_3
        if option_4:
            question.option_4 = option_4
        if correct_options:
            question.correct_options = correct_options
        if score:
            question.score = score
        session.commit()
        return jsonify({'message': 'Question updated successfully.'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'message': str(e)}), 500
    finally:
        session.close()
        
# Edit quiz endpoint (PUT)
@admin_bp.route('/quizzes/<quiz_id>', methods=['PUT'])
@login_required
def edit_quiz(quiz_id):
    if current_user.role.value != 'teacher':
        return jsonify({'message': 'Forbidden: Only teachers can edit quizzes.'}), 403
    session = SessionLocal()
    try:
        quiz = session.query(Quiz).filter_by(id=quiz_id).first()
        if not quiz:
            return jsonify({'message': 'Quiz not found.'}), 404
        # Accept partial updates
        title = request.form.get('title')
        description = request.form.get('description')
        subject_id = request.form.get('subject_id')
        chapter_id = request.form.get('chapter_id')
        date_val = request.form.get('date')
        duration = request.form.get('duration')
        cost = request.form.get('cost')
        # Only update fields if provided
        if title:
            quiz.name = title
        if description is not None:
            quiz.remarks = description
        if subject_id:
            quiz.subject_id = subject_id
        if chapter_id:
            quiz.chapter_id = chapter_id
        if date_val:
            quiz.date = date_val
        if duration:
            try:
                quiz.duration = int(duration)
            except:
                pass
        if cost is None:
            quiz.cost = 0
        # Update quiz status after edit
        update_quiz_status(quiz)
        session.commit()
        return jsonify({'message': 'Quiz updated successfully.'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'message': str(e)}), 500
    finally:
        session.close()

# Add question to quiz
@admin_bp.route('/questions', methods=['POST'])
@login_required
def add_question():
    if current_user.role.value != 'teacher':
        return jsonify({'message': 'Forbidden: Only teachers can add questions.'}), 403
    quiz_id = request.form.get('quiz_id')
    question_statement_type = request.form.get('question_type', 'text')
    question_title = request.form.get('question_title')
    question_statement_image = request.files.get('question_statement_image')
    question_statement = request.form.get('question_statement')
    option_1 = request.form.get('option_1')
    option_2 = request.form.get('option_2')
    option_3 = request.form.get('option_3')
    option_4 = request.form.get('option_4')
    correct_options = request.form.get('correct_options')
    score = request.form.get('score', '1')
    session = SessionLocal()
    try:
        quiz = session.query(Quiz).filter_by(id=quiz_id).first()
        if not quiz:
            return jsonify({'message': 'Quiz not found.'}), 404
        # Save image if provided
        if question_statement_type == 'image' and question_statement_image:
            upload_folder = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'question_images')
            os.makedirs(upload_folder, exist_ok=True)
            image_path = os.path.join(upload_folder, question_statement_image.filename)
            question_statement_image.save(image_path)
            question_statement = question_statement_image.filename
        q_id = str(uuid.uuid4())
        question = Question(
            id=q_id,
            quiz_id=quiz_id,
            question_title=question_title,
            question_statement=question_statement,
            option_1=option_1,
            option_2=option_2,
            option_3=option_3,
            option_4=option_4,
            correct_options=correct_options,
            score=score
        )
        session.add(question)
        session.commit()
        return jsonify({'message': 'Question added successfully.'}), 201
    except Exception as e:
        session.rollback()
        return jsonify({'message': str(e)}), 500
    finally:
        session.close()

@admin_bp.route('/subjects', methods=['GET'])
@login_required
def get_subjects():
    if current_user.role.value != 'teacher':
        return jsonify({'message': 'Forbidden: Only teachers can access subjects.'}), 403
    session = SessionLocal()
    try:
        subjects = session.query(Subject).all()
        if not subjects:
            return jsonify([])
        result = []
        for subject in subjects:
            chapters = []
            for chapter in subject.chapters:
                quiz_count = session.query(Quiz).filter_by(chapter_id=chapter.id).count()
                chapters.append({
                    'id': chapter.id,
                    'name': chapter.name,
                    'quiz_count': quiz_count
                })
            result.append({
                'id': subject.id,
                'name': subject.name,
                'chapters': chapters
            })
        return jsonify(result)
    finally:
        session.close()

@admin_bp.route('/subjects', methods=['POST'])
@login_required
def add_subject():
    if current_user.role.value != 'teacher':
        return jsonify({'message': 'Forbidden: Only teachers can add subjects.'}), 403
    if 'name' not in request.form:
        return jsonify({'message': 'Subject name is required.'}), 400
    name = request.form['name']
    description = request.form.get('description')
    color = request.form.get('color')
    image_file = request.files.get('image')
    image_file_name = image_file.filename if image_file else None
    session = SessionLocal()
    try:
        if session.query(Subject).filter_by(name=name).first():
            return jsonify({'message': 'Subject with this name already exists.'}), 409
        # Save image if provided
        if image_file:
            upload_folder = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'subject_images')
            os.makedirs(upload_folder, exist_ok=True)
            image_path = os.path.join(upload_folder, image_file.filename)
            image_file.save(image_path)
        subject = Subject(
            id=name.lower().replace(' ', '_'),
            name=name,
            description=description,
            color=color,
            image_file_name=image_file_name
        )
        session.add(subject)
        session.commit()
        return jsonify({'message': 'Subject added successfully.'}), 201
    except Exception as e:
        session.rollback()
        return jsonify({'message': str(e)}), 500
    finally:
        session.close()

# Get single subject details for editing
@admin_bp.route('/subjects/<subject_id>', methods=['GET'])
@login_required
def get_subject(subject_id):
    if current_user.role.value != 'teacher':
        return jsonify({'message': 'Forbidden: Only teachers can view subjects.'}), 403
    session = SessionLocal()
    try:
        subject = session.query(Subject).filter_by(id=subject_id).first()
        if not subject:
            return jsonify({'message': 'Subject not found.'}), 404
        return jsonify({
            'id': subject.id,
            'name': subject.name,
            'description': subject.description,
            'color': subject.color,
            'image_file_name': subject.image_file_name
        })
    finally:
        session.close()

# Edit subject endpoint (PUT)
@admin_bp.route('/subjects/<subject_id>', methods=['PUT'])
@login_required
def edit_subject(subject_id):
    if current_user.role.value != 'teacher':
        return jsonify({'message': 'Forbidden: Only teachers can edit subjects.'}), 403
    session = SessionLocal()
    try:
        subject = session.query(Subject).filter_by(id=subject_id).first()
        if not subject:
            return jsonify({'message': 'Subject not found.'}), 404
        name = request.form.get('name')
        description = request.form.get('description')
        color = request.form.get('color')
        image_file = request.files.get('image')
        if name:
            subject.name = name
        if description is not None:
            subject.description = description
        if color:
            subject.color = color
        if image_file:
            upload_folder = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'subject_images')
            os.makedirs(upload_folder, exist_ok=True)
            image_path = os.path.join(upload_folder, image_file.filename)
            image_file.save(image_path)
            subject.image_file_name = image_file.filename
        session.commit()
        return jsonify({'message': 'Subject updated successfully.'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'message': str(e)}), 500
    finally:
        session.close()

@admin_bp.route('/subjects/<subject_id>/chapters', methods=['POST'])
@login_required
def add_chapter(subject_id):
    if current_user.role.value != 'teacher':
        return jsonify({'message': 'Forbidden: Only teachers can add chapters.'}), 403
    if 'name' not in request.form:
        return jsonify({'message': 'Chapter name is required.'}), 400
    name = request.form['name']
    description = request.form.get('description')
    image_file = request.files.get('image')
    image_file_name = image_file.filename if image_file else None
    session = SessionLocal()
    try:
        subject = session.query(Subject).filter_by(id=subject_id).first()
        if not subject:
            return jsonify({'message': 'Subject not found.'}), 404
        # Save image if provided
        if image_file:
            upload_folder = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'chapter_images')
            os.makedirs(upload_folder, exist_ok=True)
            image_path = os.path.join(upload_folder, image_file.filename)
            image_file.save(image_path)
        chapter = Chapter(
            id=name.lower().replace(' ', '_'),
            name=name,
            subject_id=subject_id,
            description=description,
            image_file_name=image_file_name
        )
        session.add(chapter)
        session.commit()
        return jsonify({'message': 'Chapter added successfully.'}), 201
    except Exception as e:
        session.rollback()
        return jsonify({'message': str(e)}), 500
    finally:
        session.close()

@admin_bp.route('/subjects/<subject_id>', methods=['DELETE'])
@login_required
def delete_subject(subject_id):
    if current_user.role.value != 'teacher':
        return jsonify({'message': 'Forbidden: Only teachers can delete subjects.'}), 403
    session = SessionLocal()
    try:
        subject = session.query(Subject).filter_by(id=subject_id).first()
        if not subject:
            return jsonify({'message': 'Subject not found.'}), 404
        # Optionally, delete chapters and quizzes associated with this subject
        for chapter in subject.chapters:
            for quiz in chapter.quizzes:
                session.delete(quiz)
            session.delete(chapter)
        session.delete(subject)
        session.commit()
        return jsonify({'message': 'Subject deleted successfully.'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'message': str(e)}), 500
    finally:
        session.close()

@admin_bp.route('/subjects/<subject_id>/chapters/<chapter_id>', methods=['DELETE'])
@login_required
def delete_chapter(subject_id, chapter_id):
    if current_user.role.value != 'teacher':
        return jsonify({'message': 'Forbidden: Only teachers can delete chapters.'}), 403
    session = SessionLocal()
    try:
        chapter = session.query(Chapter).filter_by(id=chapter_id, subject_id=subject_id).first()
        if not chapter:
            return jsonify({'message': 'Chapter not found.'}), 404
        # Optionally, delete quizzes associated with this chapter
        for quiz in chapter.quizzes:
            session.delete(quiz)
        session.delete(chapter)
        session.commit()
        return jsonify({'message': 'Chapter deleted successfully.'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'message': str(e)}), 500
    finally:
        session.close()

@admin_bp.route('/subjects/<subject_id>/chapters/<chapter_id>', methods=['GET'])
@login_required
def get_chapter(subject_id, chapter_id):
    if current_user.role.value != 'teacher':
        return jsonify({'message': 'Forbidden: Only teachers can view chapters.'}), 403
    session = SessionLocal()
    try:
        chapter = session.query(Chapter).filter_by(id=chapter_id, subject_id=subject_id).first()
        if not chapter:
            return jsonify({'message': 'Chapter not found.'}), 404
        return jsonify({
            'id': chapter.id,
            'name': chapter.name,
            'description': chapter.description,
            'image_file_name': chapter.image_file_name
        })
    finally:
        session.close()

@admin_bp.route('/subjects/<subject_id>/chapters/<chapter_id>', methods=['PUT'])
@login_required
def update_chapter(subject_id, chapter_id):
    if current_user.role.value != 'teacher':
        return jsonify({'message': 'Forbidden: Only teachers can update chapters.'}), 403
    session = SessionLocal()
    try:
        chapter = session.query(Chapter).filter_by(id=chapter_id, subject_id=subject_id).first()
        if not chapter:
            return jsonify({'message': 'Chapter not found.'}), 404
        name = request.form.get('name')
        description = request.form.get('description')
        image_file = request.files.get('image')
        if name:
            chapter.name = name
        if description is not None:
            chapter.description = description
        if image_file:
            upload_folder = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'chapter_images')
            os.makedirs(upload_folder, exist_ok=True)
            image_path = os.path.join(upload_folder, image_file.filename)
            image_file.save(image_path)
            chapter.image_file_name = image_file.filename
        session.commit()
        return jsonify({'message': 'Chapter updated successfully.'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'message': str(e)}), 500
    finally:
        session.close()
        
@admin_bp.route('/quizzes', methods=['POST'])
@login_required
def add_quiz():
    if current_user.role.value != 'teacher':
        return jsonify({'message': 'Forbidden: Only teachers can add quizzes.'}), 403
    name = request.form.get('title')
    remarks = request.form.get('description')
    subject_id = request.form.get('subject_id')
    chapter_id = request.form.get('chapter_id')
    date = request.form.get('date')
    duration = request.form.get('duration')
    cost = request.form.get('cost')
    status = request.form.get('status', 'upcoming')
    session = SessionLocal()
    try:
        chapter = session.query(Chapter).filter_by(id=chapter_id, subject_id=subject_id).first()
        if not chapter:
            return jsonify({'message': 'Invalid chapter.'}), 404
        quiz = Quiz(
            id=name.lower().replace(' ', '_'),
            name=name,
            remarks=remarks,
            cost=cost,
            chapter_id=chapter_id,
            duration=int(duration),
            date=date,
            status=QuizStatus(status),
            created_at=datetime.now()
        )
        session.add(quiz)
        session.commit()
        return jsonify({'message': 'Quiz added successfully.'}), 201
    except Exception as e:
        session.rollback()
        return jsonify({'message': str(e)}), 500
    finally:
        session.close()
        
@admin_bp.route('/quizzes', methods=['GET'])
@login_required
def get_quizzes():
    if current_user.role.value != 'teacher':
        return jsonify({'message': 'Forbidden: Only teachers can view quizzes.'}), 403

    session = SessionLocal()
    try:
        quizzes = session.query(Quiz).all()
        result = []

        for quiz in quizzes:
            chapter = session.query(Chapter).filter_by(id=quiz.chapter_id).first()
            chapter_name = chapter.name if chapter else ''
            
            # Only use fields that exist in the Question model
            questions = [
                {
                    'id': q.id,
                    'question_title': q.question_title,
                    'question_statement': q.question_statement,
                    'score': q.score
                } for q in quiz.questions
            ]

            result.append({
                'id': quiz.id,
                'name': quiz.name,
                'chapter_id': quiz.chapter_id,
                'chapter_name': chapter_name,
                'remarks': quiz.remarks,
                'cost': quiz.cost,
                'duration': quiz.duration,
                'date': quiz.date,
                'status': quiz.status.value,
                'questions': questions
            })

        return jsonify(result)

    finally:
        session.close()

# Delete quiz endpoint
@admin_bp.route('/quizzes/<quiz_id>', methods=['DELETE'])
@login_required
def delete_quiz(quiz_id):
    if current_user.role.value != 'teacher':
        return jsonify({'message': 'Forbidden: Only teachers can delete quizzes.'}), 403
    session = SessionLocal()
    try:
        quiz = session.query(Quiz).filter_by(id=quiz_id).first()
        if not quiz:
            return jsonify({'message': 'Quiz not found.'}), 404
        # Optionally delete questions associated with this quiz
        for question in getattr(quiz, 'questions', []):
            session.delete(question)
        session.delete(quiz)
        session.commit()
        return jsonify({'message': 'Quiz deleted successfully.'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'message': str(e)}), 500
    finally:
        session.close()

@admin_bp.route('/stats/users', methods=['GET'])
@login_required
def get_stats_users():
    if current_user.role.value != 'teacher':
        return jsonify({'message': 'Forbidden'}), 403
    session = SessionLocal()
    try:
        users = session.query(User).filter(User.role != UserRole.TEACHER).all()
        result = []
        for user in users:
            # Get quizzes booked for user
            user_quizzes = session.query(UserQuiz).filter_by(user_id=user.id).all()
            quiz_names = []
            for uq in user_quizzes:
                quiz = session.query(Quiz).filter_by(id=uq.quiz_id).first()
                if quiz:
                    quiz_names.append(quiz.name)
            # Last interaction
            last_interaction = user.last_interaction if hasattr(user, 'last_interaction') else None
            result.append({
                'id': user.id,
                'username': user.username,
                'bookedQuizzes': quiz_names,
                'last_interaction': str(last_interaction) if last_interaction else None
            })
        return jsonify(result)
    finally:
        session.close()