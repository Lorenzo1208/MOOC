import datetime
from script_load_data import add_course
from script_load_data import get_date
from script_load_data import add_thread
import pytest
import mysql.connector

@pytest.fixture(scope='session')
def db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='g4'
    )
    yield connection
    connection.close()

@pytest.mark.parametrize("created_at, expected_date", [
    ("2022-03-08T10:00:00Z", datetime.datetime(2022, 3, 8, 10, 0)),
    ("2022-03-08 10:00:00", datetime.datetime(2022, 3, 8, 10, 0))
])

def test_get_date(created_at, expected_date):
    msg = {
        'created_at': created_at
    }
    assert get_date(msg) == expected_date

@pytest.mark.parametrize("id, course_id, created_at", [
    (123,"ABC123", "2022-03-08T10:00:00Z"),
    (456, "DEF456", "2022-03-08 10:00:00")
])

def test_add_course(id, course_id, created_at):
    msg = {
        'id': id,
        'course_id': course_id,
        'created_at': created_at
    }
    
    opening_dates = {}
    add_course(msg['course_id'], opening_dates, msg)
    assert opening_dates[msg['course_id']] == get_date(msg)
    
''' Dans ce code, nous appelons la fonction add_course et lui passons trois arguments : msg['course_id'], opening_dates et msg. 
msg['course_id'] et msg sont les clés du dictionnaire qui contiennent respectivement l'identifiant du cours et d'autres informations pertinentes. 
opening_dates est un dictionnaire vide qui sera utilisé pour stocker la date d'ouverture du cours. Après avoir appelé la fonction add_course, nous vérifions que la date 
d'ouverture du cours dans le dictionnaire opening_dates pour l'ID de cours correspondant correspond à la date attendue, qui est obtenue en appelant la fonction get_date 
avec le dictionnaire msg comme argument. Ce test garantit que la fonction add_course ajoute correctement le cours à la base de données et extrait et stocke la date 
d'ouverture dans le dictionnaire opening_dates.'''  

def test_add_thread(db_connection):
    thread_id = "123"
    title = "Titre du thread"
    course_id = "ABC123"
    add_thread(thread_id, title, course_id)

    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM thread WHERE _id=%s", (thread_id,))
    result = cursor.fetchone()

    assert result[0] == thread_id
    assert result[1] == title
    assert result[2] == course_id