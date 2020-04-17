""" Student Repository Endpoints

    author: fizgi
    date: 16-Apr-2020
    python: v3.8.2
"""

import sqlite3
from typing import Dict, List

from flask import Flask, render_template, redirect, url_for


db_file: str = "810_startup.db"

app: Flask = Flask(__name__)


@app.route('/', methods=['GET'])
def main():
    """ Student Repository main page """
    # A Student Repository main page which shows all the available repositories (Stevens, NJIT...)
    # could be rendered here but we do not need it now. Redirecting to the only one, Stevens!
    return redirect(url_for('stevens'))


@app.route('/stevens', methods=['GET'])
def stevens():
    """ Stevens template """
    query: str = "select s.Name as 'Student', s.CWID, g.Course, g.Grade, i.Name as 'Instructor' " \
                 "from students s join grades g on s.CWID=g.StudentCWID " \
                 "join instructors i on g.InstructorCWID=i.CWID order by s.Name"
    conn: sqlite3.Connection = sqlite3.connect(db_file)
    headers: List[str] = conn.execute(query).description
    table: List[Dict[str, str]] = [{'student': student, 'cwid': cwid, 'course': course,
                                    'grade': grade, 'instructor': inst}
                                   for student, cwid, course, grade, inst in conn.execute(query)]
    conn.close()

    return render_template('stevens.html', title="Stevens Repository", headers=headers, table=table)


app.run(debug=True)
