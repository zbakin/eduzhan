from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from schemas import StudentCreate, StudentResponse, CourseCreate, CourseResponse
from models import Student as DBStudent, Course as DBCourse
from database import SessionLocal, engine
from fastapi.staticfiles import StaticFiles

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

app.mount("/", StaticFiles(directory="frontend", html=True), name="static")
