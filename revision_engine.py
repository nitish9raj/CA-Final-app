from datetime import datetime, timedelta
import database as db

def calculate_spaced_repetition(completion_date_str):
    d = datetime.strptime(completion_date_str, "%Y-%m-%d")
    return tuple((d + timedelta(days=n)).strftime("%Y-%m-%d") for n in [3,7,15,30])

def schedule_chapter_revision(chapter_id, completion_date_str):
    r1,r2,r3,r4 = calculate_spaced_repetition(completion_date_str)
    db.execute_query(
        'INSERT INTO revisions (chapter_id,rev1_date,rev2_date,rev3_date,rev4_date) VALUES (?,?,?,?,?)',
        (chapter_id,r1,r2,r3,r4))
