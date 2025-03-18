import random
from typing import List, Tuple

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import ORM models from the same package so they all use the same Base.
from models.models import (
    StudentGroup,
    Course,
    Teacher,
    Room,
    TimeSlot,
    TeacherCourseAssignment,
)

from models.course import Course as CourseDC
from models.room import Room as RoomDC
from models.student_group import StudentGroup as StudentGroupDC
from models.teacher import Teacher as TeacherDC
from models.timeslot import TimeSlot as TimeSlotDC

# Import conversion functions.
from utils.converters import (
    student_group_db_to_dc,
    course_db_to_dc,
    teacher_db_to_dc,
    room_db_to_dc,
    timeslot_db_to_dc,
)


from faker import Faker


class DataGenerator:
    """
    Utility class for generating and loading data for timetable scheduling.
    Uses Faker for generating realistic fake data while ensuring logical consistency.
    """

    fake = Faker()

    @staticmethod
    def create_student_groups_fake(num_groups: int = 5) -> List[StudentGroup]:
        return [
            StudentGroup(
                group_id=i + 1,
                name=f"{DataGenerator.fake.word().capitalize()} Group {i + 1}",
                academic_year=random.choice(["2023", "2024"]),
                capacity=random.randint(20, 50),
                group_type=random.choice(["section", "elective_group"]),
            )
            for i in range(num_groups)
        ]

    @staticmethod
    def create_courses_fake(num_courses: int = 8) -> List[Course]:
        course_names = [
            DataGenerator.fake.word().capitalize() for _ in range(num_courses)
        ]
        return [
            Course(
                course_id=i + 1,
                code=f"C{i + 1:03d}",
                name=course_names[i],
                type=random.choice(["theory", "lab"]),
                hours_per_week=random.randint(2, 4),
            )
            for i in range(num_courses)
        ]

    @staticmethod
    def create_teachers_fake(num_teachers: int = 10) -> List[Teacher]:
        teachers = []
        for i in range(num_teachers):
            teachers.append(
                Teacher(
                    teacher_id=i + 1,
                    employee_id=f"EMP{i + 1:03d}",
                    name=DataGenerator.fake.name(),
                    status="active",
                )
            )
        return teachers

    @staticmethod
    def create_rooms_fake(num_rooms: int = 5) -> List[Room]:
        return [
            Room(
                room_id=i + 1,
                name=f"Room {DataGenerator.fake.word().capitalize()} {i + 1}",
                capacity=random.randint(30, 80),
                room_type=random.choice(["classroom", "lab", "lecture hall"]),
                status="active",
            )
            for i in range(num_rooms)
        ]

    @staticmethod
    def create_timeslots_fake() -> List[TimeSlot]:
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        periods = list(range(1, 7))
        timeslots = []
        slot_id = 1
        for day in days:
            for period in periods:
                timeslots.append(TimeSlot(slot_id=slot_id, day=day, period=period))
                slot_id += 1
        return timeslots

    @classmethod
    def populate_db(
        cls, session, num_groups=5, num_courses=8, num_teachers=10, num_rooms=5
    ):
        groups = cls.create_student_groups_fake(num_groups)
        courses = cls.create_courses_fake(num_courses)
        teachers = cls.create_teachers_fake(num_teachers)
        rooms = cls.create_rooms_fake(num_rooms)
        timeslots = cls.create_timeslots_fake()

        session.add_all(groups + courses + teachers + rooms + timeslots)
        session.commit()

        # Assign teachers to courses logically
        for course in courses:
            assigned_teacher = random.choice(teachers)
            assignment = TeacherCourseAssignment(
                course_id=course.course_id, teacher_id=assigned_teacher.teacher_id
            )
            session.add(assignment)

        session.commit()

        # Assign student groups to courses logically
        for group in groups:
            assigned_courses = random.sample(courses, k=random.randint(2, 4))
            for course in assigned_courses:
                session.add(
                    TeacherCourseAssignment(
                        course_id=course.course_id, student_group_id=group.group_id
                    )
                )

        session.commit()

        # Assign home rooms to student groups
        for i, group in enumerate(groups):
            group.home_room = rooms[i % len(rooms)].room_id
        session.commit()

    @classmethod
    def create_complete_dataset(
        cls, num_groups=5, num_courses=8, num_teachers=10, num_rooms=5
    ):
        """
        Fetch a complete dataset from the database, populating it if empty.
        """
        engine = create_engine("sqlite:///timetable.db", echo=False)
        Session = sessionmaker(bind=engine)
        session = Session()

        if session.query(StudentGroup).count() == 0:
            cls.populate_db(session, num_groups, num_courses, num_teachers, num_rooms)

        groups = session.query(StudentGroup).all()
        courses = session.query(Course).all()
        teachers = session.query(Teacher).all()
        rooms = session.query(Room).all()
        timeslots = session.query(TimeSlot).all()

        session.close()
        return groups, courses, teachers, rooms, timeslots

    @classmethod
    def create_complete_dataset_dc(
        cls,
        num_groups: int = 2,
        num_courses: int = 6,
        num_teachers: int = 20,
        num_rooms: int = 2,
    ) -> Tuple[
        List[StudentGroupDC],  # Dataclass versions
        List[CourseDC],
        List[TeacherDC],
        List[RoomDC],
        List[TimeSlotDC],
    ]:
        """
        Returns a complete dataset from the database, converting the ORM objects to your dataclasses.
        """
        groups_orm, courses_orm, teachers_orm, rooms_orm, timeslots_orm = (
            cls.create_complete_dataset(
                num_groups, num_courses, num_teachers, num_rooms
            )
        )

        groups_dc = [student_group_db_to_dc(g) for g in groups_orm]
        courses_dc = [course_db_to_dc(c) for c in courses_orm]
        teachers_dc = [teacher_db_to_dc(t) for t in teachers_orm]
        rooms_dc = [room_db_to_dc(r) for r in rooms_orm]
        timeslots_dc = [timeslot_db_to_dc(ts) for ts in timeslots_orm]

        return groups_dc, courses_dc, teachers_dc, rooms_dc, timeslots_dc
