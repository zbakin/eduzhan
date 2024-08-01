from pydantic import BaseModel

class StudentBase(BaseModel):
    name: str
    age: int

class StudentCreate(StudentBase):
    pass

class StudentResponse(StudentBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

class CourseBase(BaseModel):
    name: str
    description: str
    teacher_id: int

class CourseCreate(CourseBase):
    pass

class CourseResponse(CourseBase):
    id: int

    class Config:
        orm_mode = True
