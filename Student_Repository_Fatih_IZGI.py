""" A data repository of courses, students, and instructors.

    author: Fatih IZGI
    date: 04-Apr-2020
    version: python 3.8.2
"""

import os
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
        return [self.cwid, self.name, self.major, sorted(self.courses.keys()),
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

        self.process_files()  # process the data in students, instructors and grades files

    def department_info(self) -> Iterator[Tuple[str, List[str], List[str]]]:
        """ a generator which yields the summary data about department """
        for dep_name, details in self.departments.items():
            req_list: List[str] = list(details.courses["R"])
            elc_list: List[str] = list(details.courses["E"])

            yield [dep_name, sorted(req_list), sorted(elc_list)]

    def process_files(self) -> None:
        """ process the data in students, instructors and grades files """
        for cwid, name, major in \
                file_reader(os.path.join(self.dir_path, "students.txt"), 3, sep=";", header=True):
            student: Student = Student(cwid, name, major)
            self.students[cwid] = student  # add the new student to the container

        for cwid, name, department in \
                file_reader(os.path.join(self.dir_path, "instructors.txt"), 3, "|", True):
            instructor: Instructor = Instructor(cwid, name, department)
            self.instructors[cwid] = instructor

        for std_cwid, course, letter_grade, inst_cwid in \
                file_reader(os.path.join(self.dir_path, "grades.txt"), 4, sep="|", header=True):
            if std_cwid not in self.students.keys():
                raise ValueError(f"A grade for an unknown student with cwid: {std_cwid}")

            if inst_cwid not in self.instructors.keys():
                raise ValueError(f"A grade for an unknown instructor with cwid: {inst_cwid}")

            # find the student and instructor by cwid and update their course list
            if letter_grade in ["A", "A-", "B+", "B", "B-", "C+", "C"]:
                self.students[std_cwid].enroll_or_update({course: letter_grade})
            self.instructors[inst_cwid].add_or_update(course)

        major: Major = Major()
        for dep_name, req_elc, course in \
                file_reader(os.path.join(self.dir_path, "majors.txt"), 3, sep="\t", header=True):
            if dep_name not in self.departments:
                major = Major()

            major.courses[req_elc].add(course)
            self.departments[dep_name] = major

        for student in self.students.values():
            for r_e, courses in self.departments[student.major].courses.items():
                for course in courses:
                    if course not in student.courses:
                        (student.add_remaining_req if r_e == "R"
                         else student.add_remaining_elc)(course)

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
        for instructor in self.instructors.values():
            for info in instructor.info():
                instructor_table.add_row(info)  # add instructor info to the table

        print(department_table)
        print("Student Summary\n", student_table, sep="")
        print("Instructor Summary\n", instructor_table, sep="")


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


def main():
    """ the main class to get the data for each organization """
    stevens = Repository("stevens")  # read files and generate prettytables
    stevens.department_info()
    # njit = Repository("njit")
    # test = Repository("test")


if __name__ == '__main__':
    main()
