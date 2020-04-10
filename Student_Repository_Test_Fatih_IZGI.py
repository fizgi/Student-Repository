""" Test implementation class of the Course Registration System
    author: Fatih IZGI
    date: 26-Mar-2020
    python: v3.8.2
"""

import unittest
from typing import List, Tuple, Union
from Student_Repository_Fatih_IZGI import \
    Student, Instructor, Repository, student_grade_table_db, instructor_table_db


class TestCourseRegistration(unittest.TestCase):
    """ Test class of the methods """

    def test_student(self):
        """ testing Student class methods """
        student: Student = Student("123", "IZGI, F", "SFEN")
        student.enroll_or_update({"SSW 810": "F", "SSW 540": "A", "CS 501": "A"})

        self.assertTrue([student.cwid, student.name, student.major] == ["123", "IZGI, F", "SFEN"])
        self.assertTrue(student.courses == {"CS 501": "A", "SSW 540": "A", "SSW 810": "F"})
        self.assertTrue(student.info() == ["123", 'IZGI, F', "SFEN", ['CS 501', 'SSW 540'],
                                           [], [], 2.67])

    def test_instructor(self):
        """ testing Instructor class methods """
        inst: Instructor = Instructor(cwid="123456", name="ROWLAND, J", department="SFEN")
        inst.add_or_update(course_name="ABC123")
        inst.add_or_update(course_name="XYZ123")
        inst.add_or_update(course_name="ABC123")

        self.assertTrue([inst.cwid, inst.name, inst.department] == ["123456", "ROWLAND, J", "SFEN"])
        self.assertTrue(inst.courses == {"ABC123": 2, "XYZ123": 1})

        result: List[Tuple[str, str, str, int]] = list(inst.info())
        expect: List[list] = [["123456", 'ROWLAND, J', 'SFEN', 'ABC123', 2],
                              ["123456", 'ROWLAND, J', 'SFEN', 'XYZ123', 1]]
        self.assertEqual(result, expect)

    def test_repository(self):
        """ testing Repository class methods """
        with self.assertRaises(FileNotFoundError):
            Repository("bad_directory")

        stevens = Repository("stevens")

        result: List[list] = [student.info() for student in stevens.students.values()]
        expect: List[list] = [['10103', 'Jobs, S', 'SFEN',
                               ['CS 501', 'SSW 810'], ['SSW 540', 'SSW 555'], [], 3.38],
                              ['10115', 'Bezos, J', 'SFEN',
                               ['SSW 810'], ['SSW 540', 'SSW 555'], ['CS 501', 'CS 546'], 2.0],
                              ['10183', 'Musk, E', 'SFEN',
                               ['SSW 555', 'SSW 810'], ['SSW 540'], ['CS 501', 'CS 546'], 4.0],
                              ['11714', 'Gates, B', 'CS',
                               ['CS 546', 'CS 570', 'SSW 810'], [], [], 3.5]]
        self.assertEqual(result, expect)

        result: List[Tuple[str, str, str, int]] = [info for inst in stevens.instructors.values()
                                                   for info in inst.info()]
        expect: List[list] = [['98764', 'Cohen, R', 'SFEN', 'CS 546', 1],
                              ['98763', 'Rowland, J', 'SFEN', 'SSW 810', 4],
                              ['98763', 'Rowland, J', 'SFEN', 'SSW 555', 1],
                              ['98762', 'Hawking, S', 'CS', 'CS 501', 1],
                              ['98762', 'Hawking, S', 'CS', 'CS 546', 1],
                              ['98762', 'Hawking, S', 'CS', 'CS 570', 1]]
        self.assertEqual(result, expect)

    def test_database(self):
        """ testing data from database """
        result: List[str] = list(instructor_table_db("810_startup.db"))
        expect: List[List[Union[str, int]]] = [['98764', 'Cohen, R', 'SFEN', 'CS 546', 1],
                                               ['98763', 'Rowland, J', 'SFEN', 'SSW 810', 4],
                                               ['98763', 'Rowland, J', 'SFEN', 'SSW 555', 1],
                                               ['98762', 'Hawking, S', 'CS', 'CS 570', 1],
                                               ['98762', 'Hawking, S', 'CS', 'CS 546', 1],
                                               ['98762', 'Hawking, S', 'CS', 'CS 501', 1]]
        self.assertEqual(result, expect)

        result: List[str] = list(student_grade_table_db("810_startup.db"))
        expect: List[List[Union[str, int]]] = [['Bezos, J', '10115', 'SSW 810', 'A', 'Rowland, J'],
                                               ['Bezos, J', '10115', 'CS 546', 'F', 'Hawking, S'],
                                               ['Gates, B', '11714', 'SSW 810', 'B-', 'Rowland, J'],
                                               ['Gates, B', '11714', 'CS 546', 'A', 'Cohen, R'],
                                               ['Gates, B', '11714', 'CS 570', 'A-', 'Hawking, S'],
                                               ['Jobs, S', '10103', 'SSW 810', 'A-', 'Rowland, J'],
                                               ['Jobs, S', '10103', 'CS 501', 'B', 'Hawking, S'],
                                               ['Musk, E', '10183', 'SSW 555', 'A', 'Rowland, J'],
                                               ['Musk, E', '10183', 'SSW 810', 'A', 'Rowland, J']]
        self.assertEqual(result, expect)


if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
