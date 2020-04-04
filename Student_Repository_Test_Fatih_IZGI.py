""" Test implementation class of the Course Registration System
    author: Fatih IZGI
    date: 26-Mar-2020
    version: python 3.8.2
"""

import unittest
from typing import List
from Student_Repository_Fatih_IZGI import Student, Instructor, Repository


class TestCourseRegistration(unittest.TestCase):
    """ Test class of the methods """

    def test_student(self):
        """ testing Student class methods """
        student: Student = Student(123, "IZGI, F", "SFEN")
        student.enroll_or_update({"XYZ123": "BB", "ABC123": "AA"})

        self.assertTrue([student.cwid, student.name, student.major] == [123, "IZGI, F", "SFEN"])
        self.assertTrue(student.courses == {"ABC123": "AA", "XYZ123": "BB"})
        self.assertTrue(student.info() == [123, 'IZGI, F', ['ABC123', 'XYZ123']])

    def test_instructor(self):
        """ testing Instructor class methods """
        inst: Instructor = Instructor(cwid=123456, name="ROWLAND, J", department="SFEN")
        inst.add_or_update(course_name="ABC123")
        inst.add_or_update(course_name="XYZ123")
        inst.add_or_update(course_name="ABC123")

        self.assertTrue([inst.cwid, inst.name, inst.department] == [123456, "ROWLAND, J", "SFEN"])
        self.assertTrue(inst.courses == {"ABC123": 2, "XYZ123": 1})

        result: List[list] = list(inst.info())
        expect: List[list] = [[123456, 'ROWLAND, J', 'SFEN', 'ABC123', 2],
                              [123456, 'ROWLAND, J', 'SFEN', 'XYZ123', 1]]
        self.assertEqual(result, expect)

    def test_repository(self):
        """ testing Repository class methods """
        with self.assertRaises(FileNotFoundError):
            Repository("bad_directory")

        stevens = Repository("stevens")

        result: List[list] = [student.info() for student in stevens.students.values()]
        expect: List[list] = [['10103', 'Baldwin, C', ['CS 501', 'SSW 564', 'SSW 567', 'SSW 687']],
                              ['10115', 'Wyatt, X', ['CS 545', 'SSW 564', 'SSW 567', 'SSW 687']],
                              ['10172', 'Forbes, I', ['SSW 555', 'SSW 567']],
                              ['10175', 'Erickson, D', ['SSW 564', 'SSW 567', 'SSW 687']],
                              ['10183', 'Chapman, O', ['SSW 689']],
                              ['11399', 'Cordova, I', ['SSW 540']],
                              ['11461', 'Wright, U', ['SYS 611', 'SYS 750', 'SYS 800']],
                              ['11658', 'Kelly, P', ['SSW 540']],
                              ['11714', 'Morton, A', ['SYS 611', 'SYS 645']],
                              ['11788', 'Fuller, E', ['SSW 540']]]
        self.assertEqual(result, expect)

        result: List[list] = [info for inst in stevens.instructors.values() for info in inst.info()]
        expect: List[list] = [['98765', 'Einstein, A', 'SFEN', 'SSW 567', 4],
                              ['98765', 'Einstein, A', 'SFEN', 'SSW 540', 3],
                              ['98764', 'Feynman, R', 'SFEN', 'SSW 564', 3],
                              ['98764', 'Feynman, R', 'SFEN', 'SSW 687', 3],
                              ['98764', 'Feynman, R', 'SFEN', 'CS 501', 1],
                              ['98764', 'Feynman, R', 'SFEN', 'CS 545', 1],
                              ['98763', 'Newton, I', 'SFEN', 'SSW 555', 1],
                              ['98763', 'Newton, I', 'SFEN', 'SSW 689', 1],
                              ['98760', 'Darwin, C', 'SYEN', 'SYS 800', 1],
                              ['98760', 'Darwin, C', 'SYEN', 'SYS 750', 1],
                              ['98760', 'Darwin, C', 'SYEN', 'SYS 611', 2],
                              ['98760', 'Darwin, C', 'SYEN', 'SYS 645', 1]]
        self.assertEqual(result, expect)


if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
