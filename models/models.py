# models.py
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Enum,
    JSON,
    TIMESTAMP,
    UniqueConstraint,
    ForeignKey,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import enum

Base = declarative_base()


# Define Python Enums (using native_enum=False for SQLite compatibility)
class RoomsRoomTypeEnum(enum.Enum):
    classroom = "classroom"
    laboratory = "laboratory"
    lecture_hall = "lecture_hall"
    office = "office"
    meeting_room = "meeting_room"


class RoomsStatusEnum(enum.Enum):
    active = "active"
    maintenance = "maintenance"
    inactive = "inactive"


class TeachersStatusEnum(enum.Enum):
    active = "active"
    on_leave = "on_leave"
    inactive = "inactive"


class StudentGroupsGroupTypeEnum(enum.Enum):
    section = "section"
    elective_group = "elective-group"


class CoursesTypeEnum(enum.Enum):
    theory = "theory"
    lab = "lab"
    project = "project"
    seminar = "seminar"


class CoursesStatusEnum(enum.Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"


# Rooms table
class Room(Base):
    __tablename__ = "Rooms"
    room_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    capacity = Column(Integer, nullable=False)
    room_type = Column(Enum(RoomsRoomTypeEnum, native_enum=False), nullable=False)
    status = Column(
        Enum(RoomsStatusEnum, native_enum=False), default=RoomsStatusEnum.active
    )
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )


# Teachers table
class Teacher(Base):
    __tablename__ = "Teachers"
    teacher_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(20), nullable=False, unique=True)
    name = Column(String(50), nullable=False)
    status = Column(
        Enum(TeachersStatusEnum, native_enum=False), default=TeachersStatusEnum.active
    )
    preferences: JSON = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    constraints = relationship(
        "TeacherConstraints", back_populates="teacher", uselist=False
    )


# TeacherConstraints table
class TeacherConstraints(Base):
    __tablename__ = "TeacherConstraints"
    teacher_id = Column(
        Integer, ForeignKey("Teachers.teacher_id", ondelete="CASCADE"), primary_key=True
    )
    total_hours = Column(Integer, default=20)
    max_hours_continuous = Column(Integer, default=3)
    max_days_per_week = Column(Integer, default=6)
    min_days_per_week = Column(Integer, default=3)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    teacher = relationship("Teacher", back_populates="constraints")


# StudentGroups table
class StudentGroup(Base):
    __tablename__ = "StudentGroups"
    group_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    academic_year = Column(String(4), nullable=False)  # storing YEAR as string
    capacity = Column(Integer, nullable=False)
    advisor_id = Column(Integer, ForeignKey("Teachers.teacher_id", ondelete="SET NULL"))
    group_type = Column(
        Enum(StudentGroupsGroupTypeEnum, native_enum=False), nullable=False
    )
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    __table_args__ = (
        UniqueConstraint("name", "academic_year", name="idx_group_name_year"),
    )


# StudentGroupConstraints table
class StudentGroupConstraints(Base):
    __tablename__ = "StudentGroupConstraints"
    group_id = Column(
        Integer,
        ForeignKey("StudentGroups.group_id", ondelete="CASCADE"),
        primary_key=True,
    )
    hours_daily = Column(Integer, default=6)
    hours_continuous = Column(Integer, default=3)
    max_days_per_week = Column(Integer, default=5)
    min_days_per_week = Column(Integer, default=3)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )


# Courses table
class Course(Base):
    __tablename__ = "Courses"
    course_id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    type = Column(Enum(CoursesTypeEnum, native_enum=False), nullable=False)
    max_hours_continuous = Column(Integer, default=1)
    hours_per_week = Column(Integer, nullable=False)
    status = Column(
        Enum(CoursesStatusEnum, native_enum=False), default=CoursesStatusEnum.active
    )
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    __table_args__ = (UniqueConstraint("code", name="idx_course_code"),)


# TimeSlots table (modified to include day and period for scheduling)
class TimeSlot(Base):
    __tablename__ = "TimeSlots"
    slot_id = Column(Integer, primary_key=True, autoincrement=True)
    day = Column(String(10), nullable=False)
    period = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    __table_args__ = (UniqueConstraint("day", "period", name="idx_time_range"),)


# TeacherCourseAssignments table
class TeacherCourseAssignment(Base):
    __tablename__ = "TeacherCourseAssignments"
    assignment_id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(
        Integer, ForeignKey("Teachers.teacher_id", ondelete="CASCADE"), nullable=False
    )
    course_id = Column(
        Integer, ForeignKey("Courses.course_id", ondelete="CASCADE"), nullable=False
    )
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    __table_args__ = (UniqueConstraint("teacher_id", "course_id"),)


# ClassAssignments table
class ClassAssignment(Base):
    __tablename__ = "ClassAssignments"
    assignment_id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(
        Integer, ForeignKey("Teachers.teacher_id", ondelete="CASCADE"), nullable=False
    )
    course_id = Column(
        Integer, ForeignKey("Courses.course_id", ondelete="CASCADE"), nullable=False
    )
    group_id = Column(
        Integer,
        ForeignKey("StudentGroups.group_id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    __table_args__ = (UniqueConstraint("teacher_id", "course_id", "group_id"),)


# For testing purposes, create the SQLite engine and tables.
if __name__ == "__main__":
    engine = create_engine("sqlite:///timetable.db", echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.create_all(engine)
