import duckdb
from tt.data_types.duckdb_types import Range1D, Range2D
import numpy
from PIL import Image
import tempfile
import time
import pytest
import cv2

@pytest.fixture
def setup_duckdb_setting():
    conn = duckdb.connect(database=":memory:")
    conn.execute("SET memory_limit='1GB'")
    conn.execute("SET temp_directory='./test/test.db'")

# @pytest.fixture
# def check_duckdb():
#     conn = duckdb.connect(database=":memory:")

#     yield conn
#     print(conn.execute("FROM duckdb_memory();"))
#     print(conn.execute("FROM duckdb_temporary_files();"))
    

def test_range1d_roundtrip():
    conn = duckdb.connect(database=":memory:")
    
    conn.execute(Range1D.__create_type__())
    conn.execute(f"CREATE TABLE ranges (r RANGE1D)")

    r = Range1D(1, 2)
    conn.execute("INSERT INTO ranges VALUES (?)", [r.__sql_literal_insert__()])

    res = conn.execute("SELECT r FROM ranges").fetchone()
    print(conn.sql("SELECT r FROM ranges").show())
    type_name = conn.sql("SELECT typeof(r) FROM ranges").fetchone()[0]
    # assert type_name == Range1D.__sql_name__
    assert res is not None



def test_range2d_roundtrip():
    conn = duckdb.connect(database=":memory:")
    
    conn.execute(Range2D.__create_type__())
    conn.execute(f"CREATE TABLE ranges (r RANGE2D)")

    r = Range2D(x_range=Range1D(1.0,2.0), y_range=Range1D(2.0, 3.0))
    
    conn.execute("INSERT INTO ranges VALUES (?)", [r.__sql_literal_insert__()])

    res = conn.execute("SELECT r FROM ranges").fetchone()
    print(conn.sql("SELECT r FROM ranges").show())

    type_name = conn.sql("SELECT typeof(r) FROM ranges").fetchone()[0]

    conn.execute('''ATTACH 'my_database.db';
# COPY FROM DATABASE memory TO my_database;
# DETACH my_database;''')
    # assert type_name == Range2D.__name__
    assert res is not None


def _test_insert_images():
    conn = duckdb.connect(database=":memory:")
    conn.execute("SET memory_limit='1GB'")
    conn.execute("SET temp_directory='./test'") 

    conn.execute(f"CREATE TABLE ranges (r BLOB)")
    img = Image.open('img.png')
    img_arr = numpy.array(img)
    print(img_arr.size, img_arr.shape)

    start_time = time.time()

    for _ in range(30 * 10):
        img_arr = numpy.array(img)
        conn.execute("INSERT INTO ranges VALUES (?)", [img_arr.tobytes()])

    end_time = time.time()
    
    print(f"Memory: {end_time - start_time}")

    
    start_time = time.time()
    for _ in range(30 * 10):
        img_arr = numpy.array(img)
        with tempfile.TemporaryFile() as temp_file:
            temp_file.write(img_arr)
    end_time = time.time()
    
    print(f"Disk: {end_time - start_time}")
                
    # conn.execute("EXPORT DATABASE 'target'")
    res = conn.execute("SELECT r FROM ranges").fetchone()
    # print(conn.sql("SELECT r FROM ranges").show())

    type_name = conn.sql("SELECT typeof(r) FROM ranges").fetchone()[0]
    # print(conn.sql("FROM duckdb_memory();").show())
    # print(conn.sql("FROM duckdb_temporary_files();").show())
    # assert type_name == Range2D.__name__
    assert res is not None


def _test_video():
    cap = cv2.VideoCapture(0)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('output.mp4', fourcc, 25.0, (640,480))

    ret, frame = cap.read()
    print(frame)
    print(ret)
    print(type(frame)) 
    print(frame.shape)
    out.write(frame)

    cap.release()
    out.release()
    cv2.destroyAllWindows()
