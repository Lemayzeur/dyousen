from db.manager import ModelBase
from db.fields import Column
from config import constants

class User(ModelBase):
    class Props:
        table_name = 'users'
    
    id = Column(int, required=True, constraint=constants.PK_CONSTRAINT)
    email = Column(str, required=True, max_length=140)
    password = Column(str, required=True, max_length=140) 

class Classroom(ModelBase):
    class Props:
        table_name = 'classrooms'
    
    id = Column(int, required=True, constraint=constants.PK_CONSTRAINT)
    name = Column(str, max_length=40)

    def __repr__(self):
        return f"<Classroom(name={self.name})>"


class Student(ModelBase):
    class Props:
        table_name = 'students'

    id = Column(int, required=True, constraint=constants.PK_CONSTRAINT)
    first_name = Column(str, max_length=200, required=True)
    last_name = Column(str, max_length=200, required=True)
    classroom = Column(int, constraint=constants.FK_CONSTRAINT, model=Classroom)

    def __repr__(self):
        return f"<Student(id={self.id}, first_name={self.first_name}, last_name={self.last_name}, classroom={self.classroom})>"


class Teacher(ModelBase):
    class Props:
        table_name = 'teachers'
    
    id = Column(int, required=True, constraint=constants.PK_CONSTRAINT)
    first_name = Column(str, max_length=200)
    last_name = Column(str, max_length=200)
    classrooms = Column(list, constraint=constants.M2M_CONSTRAINT, model=Classroom, through_model='TeacherClassroom')

    def __repr__(self):
        return f"<Teacher(first_name={self.first_name}, last_name={self.last_name}>, classrooms={self.classrooms}"

class TeacherClassroom(ModelBase):
    class Props:
        table_name = 'teacher_classrooms'

    teacher = Column(int, constraint=constants.FK_CONSTRAINT, model=Teacher)
    classroom = Column(int, constraint=constants.FK_CONSTRAINT, model=Classroom)