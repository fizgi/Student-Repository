""" A data repository of courses, students, and instructors.

    author: Fatih IZGI
    date: 26-Mar-2020
    version: python 3.8.2
"""

import os
from typing import Dict, List, Iterator, Tuple, Union
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

    def enroll_or_update(self, course: Dict[str, str]) -> None:
        """ enroll student to a course """
        self.courses.update(zip(course.keys(), course.values()))  # multiple courses can be added

    def info(self) -> List[Union[str, List[str]]]:
        """ returns the summary data about a single student """
        return [self.cwid, self.name, sorted(self.courses.keys())]  # return student info as a list


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


class Repository:
    """ holds all of the data for a specific organization """
    def __init__(self, dir_path) -> None:
        """ store the organization info """
        if not os.path.exists(dir_path):  # if the specified directory does not exist
            raise FileNotFoundError(f"The specified directory ‘{dir_path}’ is not found")

        self.students: Dict[str, Student] = dict()  # container {cwid: StudentObject}
        self.instructors: Dict[str, Instructor] = dict()  # container {cwid: InstructorObject}
        self.dir_path: str = dir_path

        self.process_files()  # process the data in students, instructors and grades files

    def process_files(self) -> None:
        """ process the data in students, instructors and grades files """
        for cwid, name, major in self.file_reader("students.txt", 3, sep=";", header=True):
            student: Student = Student(cwid, name, major)
            self.students[cwid] = student  # add the new student to the container

        for cwid, name, department in self.file_reader("instructors.txt", 3, sep="|", header=True):
            instructor: Instructor = Instructor(cwid, name, department)
            self.instructors[cwid] = instructor

        for cwid, name, department in self.file_reader("majors.txt", 3, sep="\t", header=True):
            instructor: Instructor = Instructor(cwid, name, department)
            self.instructors[cwid] = instructor

        for std_cwid, course, letter_grade, inst_cwid in self.file_reader("grades.txt", 4, sep="|", header=True):
            if std_cwid not in self.students.keys():
                raise ValueError(f"A grade for an unknown student with cwid: {std_cwid}")

            if inst_cwid not in self.instructors.keys():
                raise ValueError(f"A grade for an unknown instructor with cwid: {inst_cwid}")

            # find the student and instructor by cwid and update their course list
            self.students[std_cwid].enroll_or_update({course: letter_grade})
            self.instructors[inst_cwid].add_or_update(course)

        self.pretty_print()

    def file_reader(self, path: str, fields: int, sep: str = "\t", header: bool = False) \
            -> Iterator[List[str]]:
        """ a generator function to read field-separated text files
            and yield a tuple with all of the values from a single line """
        if not os.path.exists(os.path.join(self.dir_path, path)):
            raise FileNotFoundError(f"The specified directory"
                                    f"‘{os.path.join(self.dir_path, path)}’ is not found")

        file = open(os.path.join(self.dir_path, path), "r")

        with file:  # close file after opening
            for line_number, line in enumerate(file, 1):
                row_fields: List[str] = line.rstrip("\n").split(sep)
                row_field_count: int = len(row_fields)

                if row_field_count != fields:
                    raise ValueError(f"‘{path}’ has {row_field_count} fields "
                                     f"on line {line_number} but expected {fields}")

                if not header or line_number != 1:
                    yield row_fields

    def pretty_print(self) -> None:
        """ prettify the data """
        student_table: PrettyTable = PrettyTable()
        student_table.field_names = ["CWID", "Name", "Completed Courses"]
        for student in self.students.values():
            student_table.add_row(student.info())  # add student info to the table

        instructor_table: PrettyTable = PrettyTable()
        instructor_table.field_names = ["CWID", "Name", "Dept", "Course", "Student"]
        for instructor in self.instructors.values():
            for info in instructor.info():
                instructor_table.add_row(info)  # add instructor info to the table

        print("Student Summary\n", student_table, sep="")
        print("Instructor Summary\n", instructor_table, sep="")


def main():
    """ the main class to get the data for each organization """
    stevens = Repository("stevens") # read files and generate prettytables
    # njit = Repository("njit")
    # test = Repository("test")


if __name__ == '__main__':
    main()
