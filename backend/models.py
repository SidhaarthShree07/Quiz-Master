from datetime import datetime
from sqlalchemy import Column, String, Integer, Date, ForeignKey, create_engine, Enum as SAEnum, DateTime 
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from marshmallow import Schema, fields
from flask_login import UserMixin
from enum import Enum
import os

Base = declarative_base()

# Enums
class UserRole(Enum):
    STUDENT = 'student'
    TEACHER = 'teacher'
    # Add more roles as needed

class QuizStatus(Enum):
    UPCOMING = 'upcoming'
    ONGOING = 'ongoing'
    EXPIRED = 'expired'

class UserQuizStatus(Enum):
    BOOKED = 'booked'
    ATTEMPTED = 'attempted'
    NON_ATTEMPTED = 'non_attempted'

# 1. User
class User(UserMixin, Base):
    __tablename__ = 'user'
    id = Column(String, primary_key=True)
    username = Column(String, nullable=False)
    email = Column(String, nullable=True)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    dob = Column(Date, nullable=True)
    remember_token = Column(String, nullable=True)
    qualification = Column(String, nullable=True)
    role = Column(SAEnum(UserRole), nullable=False, default=UserRole.STUDENT)
    image_file_name = Column(String, nullable=True)
    last_interaction = Column(DateTime, nullable=True)
    quizzes = relationship('UserQuiz', back_populates='user')
    ratings = relationship('UserRating', back_populates='user')

    def to_dict(self):
        d = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        d['role'] = self.role.value if self.role else None
        return d

# 2. Subject
class Subject(Base):
    __tablename__ = 'subject'
    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(String)
    color = Column(String)
    image_file_name = Column(String)
    chapters = relationship('Chapter', back_populates='subject')

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# 3. Chapter
class Chapter(Base):
    __tablename__ = 'chapter'
    id = Column(String, primary_key=True)
    name = Column(String)
    subject_id = Column(String, ForeignKey('subject.id'))
    description = Column(String)
    image_file_name = Column(String)
    subject = relationship('Subject', back_populates='chapters')
    quizzes = relationship('Quiz', back_populates='chapter')

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# 4. Quiz
class Quiz(Base):
    __tablename__ = 'quiz'
    id = Column(String, primary_key=True)
    name = Column(String)
    chapter_id = Column(String, ForeignKey('chapter.id'))
    remarks = Column(String)
    cost = Column(String)
    duration = Column(Integer)
    date = Column(String)
    status = Column(SAEnum(QuizStatus), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    chapter = relationship('Chapter', back_populates='quizzes')
    questions = relationship('Question', back_populates='quiz')
    ratings = relationship('UserRating', back_populates='quiz')
    user_quizzes = relationship('UserQuiz', back_populates='quiz')

    def to_dict(self):
        d = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        d['status'] = self.status.value if self.status else None
        return d

# 5. Question
class Question(Base):
    __tablename__ = 'question'
    id = Column(String, primary_key=True)
    quiz_id = Column(String, ForeignKey('quiz.id'))
    question_title = Column(String)
    question_statement = Column(String)
    option_1 = Column(String)
    option_2 = Column(String)
    option_3 = Column(String)
    option_4 = Column(String)
    correct_options = Column(String)
    score = Column(String)
    quiz = relationship('Quiz', back_populates='questions')

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# 6. UserRating
class UserRating(Base):
    __tablename__ = 'userrating'
    id = Column(String, primary_key=True)
    quiz_id = Column(String, ForeignKey('quiz.id'))
    user_id = Column(String, ForeignKey('user.id'))
    rating = Column(Integer)
    quiz = relationship('Quiz', back_populates='ratings')
    user = relationship('User', back_populates='ratings')

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in UserRating.__table__.columns}

# 7. UserQuiz
class UserQuiz(Base):
    __tablename__ = 'userquiz'
    id = Column(String, primary_key=True)
    quiz_id = Column(String, ForeignKey('quiz.id'))
    user_id = Column(String, ForeignKey('user.id'))
    status = Column(SAEnum(UserQuizStatus), nullable=False)
    score = Column(String)
    timestamp = Column(String)
    quiz = relationship('Quiz', back_populates='user_quizzes')
    user = relationship('User', back_populates='quizzes')

    def to_dict(self):
        d = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        d['status'] = self.status.value if self.status else None
        return d

# Marshmallow Schemas
class UserSchema(Schema):
    role = fields.Function(lambda obj: obj.role.value if obj.role else None)
    class Meta:
        fields = tuple(c.name for c in User.__table__.columns)

class SubjectSchema(Schema):
    class Meta:
        fields = tuple(c.name for c in Subject.__table__.columns)

class ChapterSchema(Schema):
    class Meta:
        fields = tuple(c.name for c in Chapter.__table__.columns)

class QuizSchema(Schema):
    status = fields.Function(lambda obj: obj.status.value if obj.status else None)
    class Meta:
        fields = tuple(c.name for c in Quiz.__table__.columns)

class QuestionSchema(Schema):
    class Meta:
        fields = tuple(c.name for c in Question.__table__.columns)

class UserRatingSchema(Schema):
    class Meta:
        fields = tuple(c.name for c in UserRating.__table__.columns)

class UserQuizSchema(Schema):
    status = fields.Function(lambda obj: obj.status.value if obj.status else None)
    class Meta:
        fields = tuple(c.name for c in UserQuiz.__table__.columns)

# DB creation utility
DB_PATH = os.path.join(os.path.dirname(__file__), 'quiz_master.db')
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
SessionLocal = sessionmaker(bind=engine)

def create_db():
    Base.metadata.create_all(engine)