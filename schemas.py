from pydantic import BaseModel

class StudentBase(BaseModel):
    name: str
    age: int

class StudentCreate(StudentBase):
    pass

class Student(StudentBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

class CourseCreate(BaseModel):
    name: str
    description: str
    teacher_id: int

class CourseResponse(CourseCreate):
    id: int
