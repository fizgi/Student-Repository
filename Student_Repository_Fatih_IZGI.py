""" A data repository of courses, students, and instructors.

    author: Fatih IZGI
    date: 10-Apr-2020
    python: v3.8.2
"""

import os
import sqlite3
from typing import Dict, List, Iterator, Tuple, Union, Set
from collections import defaultdict
from prettytable import PrettyTable


class Student:
    """ stores information about a single student """

    def __init__(self, cwid: str, name: str, major: str) -> None:
        """ store the Student info """
        self.cwid: str = cwid
        self.name: str = name
        self.major: str = major
        self.courses: Dict[str, str] = {}  # course {course_code: grade}
        self.remaining_req: List[str] = []  # container for remaining required courses
        self.remaining_elc: List[str] = []  # container for remaining elective courses

    def enroll_or_update(self, course: Dict[str, str]) -> None:
        """ enroll student to a course """
        self.courses.update(zip(course.keys(), course.values()))  # multiple courses can be added

    def add_remaining_req(self, course: str) -> None:
        """ add remaining required course to the container """
        self.remaining_req.append(course)

    def add_remaining_elc(self, course: str) -> None:
        """ add remaining elective course to the container """
        self.remaining_elc.append(course)

    def gpa(self) -> float:
        """ calculates and return the GPA of the student """
        grades: Dict[str, float] = {"A": 4.00, "A-": 3.75, "B+": 3.25, "B": 3.00,
                                    "B-": 2.75, "C+": 2.25, "C": 2.00, "C-": 0.00,
                                    "D+": 0.00, "D": 0.00, "D-": 0.00, "F": 0.00}

        try:
            avg: float = sum([grades[grade] for grade in self.courses.values()]) / len(
                self.courses.values())
            return round(avg, 2)
        except ZeroDivisionError:
            return 0

    def info(self) -> List[Union[str, str, str, List[str], List[str], List[str], float]]:
        """ returns the summary data about a single student """
        std_passed_elc_set: List[str] = [c for c, g in self.courses.items() if g in ["A", "A-", "B+", "B", "B-", "C+", "C"]]

        return [self.cwid, self.name, self.major, sorted(std_passed_elc_set),
                sorted(self.remaining_req), sorted(self.remaining_elc), self.gpa()]


class Instructor:
    """ stores information about a single Instructor """

    def __init__(self, cwid: str, name: str, department: str) -> None:
        """ store the Instructor info """
        self.cwid: str = cwid
        self.name: str = name
        self.department: str = department
        self.courses: Dict[str, int] = defaultdict(int)  # course {course_code: number}

    def add_or_update(self, course_name: str) -> None:
        """ add or update a course information """
        self.courses[course_name] += 1  # add a new key and/or update a value

    def info(self) -> Iterator[Tuple[str, str, str, int]]:
        """ a generator which yields the summary data about instructor and their courses """
        for course, number in self.courses.items():
            yield [self.cwid, self.name, self.department, course, number]


class Major:
    """ a class to store the Major data """

    def __init__(self):
        """ store the Major info """
        self.courses: Dict[str, Set[str]] = defaultdict(set)  # {"R" or "E": (courses)}


class Repository:
    """ holds all of the data for a specific organization """

    def __init__(self, dir_path) -> None:
        """ store the organization info """
        if not os.path.exists(dir_path):  # if the specified directory does not exist
            raise FileNotFoundError(f"The specified directory ‘{dir_path}’ is not found")

        self.students: Dict[str, Student] = dict()  # container {cwid: StudentObject}
        self.instructors: Dict[str, Instructor] = dict()  # container {cwid: InstructorObject}
        self.departments: Dict[str, Major] = dict()
        self.dir_path: str = dir_path

        try:
            self.process_files()  # process the data in students, instructors and grades files
        except ValueError as ve:
            print(ve)
        except FileNotFoundError as fnfe:
            print(fnfe)

    def department_info(self) -> Iterator[Tuple[str, List[str], List[str]]]:
        """ a generator which yields the summary data about department """
        for dep_name, details in self.departments.items():
            req_list: List[str] = list(details.courses["R"])
            elc_list: List[str] = list(details.courses["E"])

            yield [dep_name, sorted(req_list), sorted(elc_list)]

    def process_files(self) -> None:
        """ process the data in students, instructors and grades files """
        for cwid, name, major in \
                file_reader(os.path.join(self.dir_path, "students.txt"), 3, header=True):
            student: Student = Student(cwid, name, major)
            self.students[cwid] = student  # add the new student to the container

        for cwid, name, department in \
                file_reader(os.path.join(self.dir_path, "instructors.txt"), 3, header=True):
            instructor: Instructor = Instructor(cwid, name, department)
            self.instructors[cwid] = instructor

        for std_cwid, course, letter_grade, inst_cwid in \
                file_reader(os.path.join(self.dir_path, "grades.txt"), 4, header=True):
            if std_cwid not in self.students.keys():
                raise ValueError(f"A grade for an unknown student with cwid: {std_cwid}")

            if inst_cwid not in self.instructors.keys():
                raise ValueError(f"A grade for an unknown instructor with cwid: {inst_cwid}")

            # find the student and instructor by cwid and update their course list
            self.students[std_cwid].enroll_or_update({course: letter_grade})
            self.instructors[inst_cwid].add_or_update(course)

        major: Major = Major()
        for dep_name, req_elc, course in \
                file_reader(os.path.join(self.dir_path, "majors.txt"), 3, header=True):
            if dep_name not in self.departments:
                major = Major()

            major.courses[req_elc].add(course)
            self.departments[dep_name] = major

        passing_grades: List[str] = ["A", "A-", "B+", "B", "B-", "C+", "C"]
        for student in self.students.values():
            for r_e, courses in self.departments[student.major].courses.items():
                for course in courses:
                    dept_req: Set[str] = self.departments[student.major].courses["R"]
                    std_passed_req: List[str] = [c for c, g in student.courses.items()
                                                 if c in dept_req and g in passing_grades]
                    if course not in std_passed_req:
                        dept_elc: Set[str] = self.departments[student.major].courses["E"]
                        std_passed_elc: List[str] = [c for c, g in student.courses.items()
                                                     if c in dept_elc and g in passing_grades]
                        if r_e == "R":
                            student.add_remaining_req(course)
                        elif r_e == "E" and len(std_passed_elc) < 1:
                            student.add_remaining_elc(course)

        self.pretty_print()

    def pretty_print(self) -> None:
        """ prettify the data """
        department_table: PrettyTable = PrettyTable()
        department_table.field_names = ["Major", "Required Courses", "Electives"]
        for info in self.department_info():
            department_table.add_row(info)  # add department info to the table

        student_table: PrettyTable = PrettyTable()
        student_table.field_names = ["CWID", "Name", "Major", "Completed Courses",
                                     "Remaining Required", "Remaining Electives", "GPA"]
        for student in self.students.values():
            student_table.add_row(student.info())  # add student info to the table

        instructor_table: PrettyTable = PrettyTable()
        instructor_table.field_names = ["CWID", "Name", "Dept", "Course", "Student"]
        # for instructor in self.instructors.values():
        #     for info in instructor.info():
        #         instructor_table.add_row(info)  # add instructor info to the table
        for info in instructor_table_db("810_startup.db"):
            instructor_table.add_row(info)

        student_grade_table: PrettyTable = PrettyTable()
        student_grade_table.field_names = ["Name", "CWID", "Course", "Grade", "Instructor"]
        for info in student_grade_table_db("810_startup.db"):
            student_grade_table.add_row(info)

        print(department_table, sep="")
        print("Student Summary (FROM LOCAL FILES)\n", student_table, sep="")
        print("Instructor Summary (FROM DB)\n", instructor_table, sep="")
        print("Student Grade Summary (FROM DB)\n", student_grade_table, sep="")


def file_reader(path: str, fields: int, sep: str = "\t", header: bool = False) \
        -> Iterator[List[str]]:
    """ a generator function to read field-separated text files
        and yield a tuple with all of the values from a single line """
    if not os.path.exists(path):
        raise FileNotFoundError(f"The specified directory"
                                f"‘{path}’ is not found")

    file = open(path, "r")

    with file:  # close file after opening
        for line_number, line in enumerate(file, 1):
            row_fields: List[str] = line.rstrip("\n").split(sep)
            row_field_count: int = len(row_fields)

            if row_field_count != fields:
                raise ValueError(f"‘{path}’ has {row_field_count} fields "
                                 f"on line {line_number} but expected {fields}")

            if not header or line_number != 1:
                yield row_fields


def instructor_table_db(db_file: str):
    """ yields information about a single instructor from database """
    db: sqlite3.Connection = sqlite3.connect(db_file)
    query: str = "select i.CWID, i.Name, i.Dept, g.Course, count(*) " \
                 "from grades g join instructors i on g.InstructorCWID = i.CWID " \
                 "group by i.CWID, g.Course order by i.CWID desc, g.Course desc"
    for cwid, name, department, course, count in db.execute(query):
        yield [cwid, name, department, course, count]


def student_grade_table_db(db_file: str):
    """ yields student grade table from database """
    db: sqlite3.Connection = sqlite3.connect(db_file)
    query: str = "select s.Name, s.CWID, g.Course, g.Grade, i.Name as 'Instructor' " \
                 "from grades g join students s on g.StudentCWID = s.CWID " \
                 "join instructors i on g.InstructorCWID = i.CWID order by s.Name"
    for name, cwid, course, grade, instructor in db.execute(query):
        yield [name, cwid, course, grade, instructor]


def main():
    """ the main class to get the data for each organization """
    stevens: Repository = Repository("stevens")  # read files and generate prettytables


if __name__ == '__main__':
    main()
