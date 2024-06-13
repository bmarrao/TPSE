import os
import cv2
import time
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

from msg_arduino import msg_arduino

# load the environment variables from the .env file
load_dotenv()
MAX_ATTEMPTS = 5    # maximum number of attempts to connect to the database
# video = cv2.VideoCapture(0)
HOST=os.getenv('HOST')
DATABASE=os.getenv('DATABASE')
USERNAME=os.getenv('USERNAME')
PASSWORD=os.getenv('PASSWORD')
PORT=os.getenv('PORT')
MAIN_DIRECTORY=os.getenv('MAIN_DIRECTORY')


def create_db_connection() :
    return psycopg2.connect(
        host=HOST,
        database=DATABASE,
        user=USERNAME,
        password=PASSWORD,
        port=PORT
    )


def record_video() :
    video = cv2.VideoCapture(0)
    print('start recording')
    # timestamp format: 'YYYY-MM-DD HH:MM:SS'
    current_timestamp = datetime.now()
    timestamp = current_timestamp.strftime('%Y-%m-%d %H:%M:%S')
    video_id = current_timestamp.strftime('%Y%m%d%H%M%S')
    video_name = current_timestamp.strftime('%Y%m%d_%H%M%S')
    video_filename = f'storage/{video_name}.mp4'
    file_path = os.path.join(MAIN_DIRECTORY, video_filename)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(file_path, fourcc, 20.0, (640, 480))

    if not out.isOpened() :
        print('Error: failed to open video file')
        return
    
    if not video.isOpened() :
        print('Error: failed to open video stream')
        return
    
    start_time = time.time()
    # msg_arduino('turnLightOn')

    # record video for 30 seconds or until the recording flag is set to False
    while (time.time() - start_time) < 15 :
        ret, frame = video.read()

        if ret :
            frame = cv2.resize(frame, (640, 480))
            out.write(frame)
        else :
            print('Error: failed to read video frame')

    print('stop recording')
    # msg_arduino('turnLightOff')
    out.release()

    connection = create_db_connection()
    cursor = connection.cursor()

    try :
        cursor.execute(
            "INSERT INTO videos (video_id, url, created_at) VALUES (%s, %s, %s);",
            (video_id, video_filename, timestamp)
        )
        connection.commit()
    except Exception as e :
        print(e)
        # rollback the transaction
        connection.rollback()
        # commit to reset the connection state
        connection.commit()
    finally :
        cursor.close()
        connection.close()


# record_video()
