from typing import List
from schemas import StudentCreate, StudentResponse, CourseCreate, CourseResponse
from models import Student as DBStudent, Course as DBCourse
from database import SessionLocal, engine
from fastapi.staticfiles import StaticFiles
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from models import Base, User, UserRole
from schemas import UserCreate, UserResponse, Token
from auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_current_active_admin,
)
from datetime import timedelta

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Create the database tables
DBStudent.metadata.create_all(bind=engine)
DBCourse.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/students/", response_model=StudentResponse)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    db_student = DBStudent(name=student.name, age=student.age)
    db.add(db_student)
    try:
        db.commit()
        db.refresh(db_student)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    return db_student

@app.get("/students/", response_model=List[StudentResponse])
def read_students(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    students = db.query(DBStudent).offset(skip).limit(limit).all()
    return students

@app.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    db_student = db.query(DBStudent).filter(DBStudent.id == student_id).first()
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(db_student)
    db.commit()
    return {"detail": "Student deleted"}

@app.post("/courses/", response_model=CourseResponse)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    db_course = DBCourse(name=course.name, description=course.description, teacher_id=course.teacher_id)
    db.add(db_course)
    try:
        db.commit()
        db.refresh(db_course)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    return db_course

@app.get("/courses/", response_model=List[CourseResponse])
def read_courses(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    courses = db.query(DBCourse).offset(skip).limit(limit).all()
    return courses

@app.delete("/courses/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db)):
    db_course = db.query(DBCourse).filter(DBCourse.id == course_id).first()
    if db_course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(db_course)
    db.commit()
    return {"detail": "Course deleted"}

@app.post("/register/", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(SessionLocal)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(SessionLocal)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=UserResponse)
def read_users_me(current_user: UserResponse = Depends(get_current_active_user)):
    return current_user

@app.get("/admin/", response_model=UserResponse)
def read_admins_me(current_user: UserResponse = Depends(get_current_active_admin)):
    return current_user

app.mount("/", StaticFiles(directory="frontend", html=True), name="static")
