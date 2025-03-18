# converters.py

# Import your dataclasses
from models.course import Course as CourseDC
from models.room import Room as RoomDC
from models.student_group import StudentGroup as StudentGroupDC
from models.teacher import Teacher as TeacherDC
from models.timeslot import TimeSlot as TimeSlotDC

# Import your ORM models (make sure they come from the same Base)
from models.models import (
    Course as CourseORM,
    Room as RoomORM,
    StudentGroup as StudentGroupORM,
    Teacher as TeacherORM,
    TimeSlot as TimeSlotORM,
)

# ------------------------------
# Converters: Database -> Dataclass
# ------------------------------


def course_db_to_dc(db_obj: CourseORM) -> CourseDC:
    """
    Convert a SQLAlchemy Course (ORM) instance to a dataclass Course.
    """
    return CourseDC(course_id=db_obj.course_id, name=db_obj.name)


def room_db_to_dc(db_obj: RoomORM) -> RoomDC:
    """
    Convert a SQLAlchemy Room (ORM) instance to a dataclass Room.
    """
    return RoomDC(room_id=db_obj.room_id, name=db_obj.name)


def student_group_db_to_dc(db_obj: StudentGroupORM) -> StudentGroupDC:
    """
    Convert a SQLAlchemy StudentGroup (ORM) instance to a dataclass StudentGroup.
    """
    return StudentGroupDC(
        group_id=db_obj.group_id, name=db_obj.name
    )


def teacher_db_to_dc(db_obj: TeacherORM) -> TeacherDC:
    """
    Convert a SQLAlchemy Teacher (ORM) instance to a dataclass Teacher.
    Assumes that the 'preferences' column stores a list of (day, period) tuples.
    """
    return TeacherDC(
        teacher_id=db_obj.teacher_id,
        name=db_obj.name,
        preferred_times=db_obj.preferences if db_obj.preferences else [],
    )


def timeslot_db_to_dc(db_obj: TimeSlotORM) -> TimeSlotDC:
    """
    Convert a SQLAlchemy TimeSlot (ORM) instance to a dataclass TimeSlot.
    """
    return TimeSlotDC(slot_id=db_obj.slot_id, day=db_obj.day, period=db_obj.period)


# ------------------------------
# Converters: Dataclass -> Database
# ------------------------------


def course_dc_to_db(dc_obj: CourseDC) -> CourseORM:
    """
    Convert a dataclass Course to a SQLAlchemy Course (ORM) instance.
    You may need to supply additional fields (e.g. code, type, hours_per_week) as defaults.
    """
    return CourseORM(
        course_id=dc_obj.course_id,
        name=dc_obj.name,
        code=f"COURSE{dc_obj.course_id}",  # Default code if needed
        type="theory",  # Default type
        hours_per_week=3,  # Default hours per week
    )


def room_dc_to_db(dc_obj: RoomDC) -> RoomORM:
    """
    Convert a dataclass Room to a SQLAlchemy Room (ORM) instance.
    """
    return RoomORM(
        room_id=dc_obj.room_id,
        name=dc_obj.name,
        capacity=50,  # Default capacity; adjust as needed.
        room_type="classroom",  # Default room type.
        status="active",  # Default status.
    )


def student_group_dc_to_db(dc_obj: StudentGroupDC) -> StudentGroupORM:
    """
    Convert a dataclass StudentGroup to a SQLAlchemy StudentGroup (ORM) instance.
    """
    return StudentGroupORM(
        group_id=dc_obj.group_id,
        name=dc_obj.name,
        academic_year="2023",  # Default academic year; adjust as needed.
        capacity=30,  # Default capacity.
        group_type="section",  # Default group type.
        home_room=dc_obj.home_room,
    )


def teacher_dc_to_db(dc_obj: TeacherDC) -> TeacherORM:
    """
    Convert a dataclass Teacher to a SQLAlchemy Teacher (ORM) instance.
    """
    return TeacherORM(
        teacher_id=dc_obj.teacher_id,
        employee_id=f"EMP{dc_obj.teacher_id:03d}",  # Generate a default employee_id.
        name=dc_obj.name,
        preferences=dc_obj.preferred_times,
        status="active",  # Default status.
    )


def timeslot_dc_to_db(dc_obj: TimeSlotDC) -> TimeSlotORM:
    """
    Convert a dataclass TimeSlot to a SQLAlchemy TimeSlot (ORM) instance.
    """
    return TimeSlotORM(slot_id=dc_obj.slot_id, day=dc_obj.day, period=dc_obj.period)
