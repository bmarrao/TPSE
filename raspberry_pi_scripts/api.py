import os
import cv2
import time
import psycopg2
import threading
from flask_cors import CORS
from flask import Flask, jsonify, send_file, Response
from datetime import datetime
from dotenv import load_dotenv

from ip import get_current_ip
from msg_arduino import msg_arduino

# load the environment variables from the .env file
load_dotenv()
MAX_ATTEMPTS = 5    # maximum number of attempts to connect to the database
RECORDING = False
video = cv2.VideoCapture(0)
api = Flask(__name__)
CORS(api)
HOST=os.getenv('HOST')
DATABASE=os.getenv('DATABASE')
USERNAME=os.getenv('USERNAME')
PASSWORD=os.getenv('PASSWORD')
PORT=os.getenv('PORT')
MAIN_DIRECTORY=os.getenv('MAIN_DIRECTORY')
recording_thread = None


def create_db_connection() :
    return psycopg2.connect(
        host=HOST,
        database=DATABASE,
        user=USERNAME,
        password=PASSWORD,
        port=PORT
    )


# TODO: test
# generator function to stream video frames
def video_stream() :
    while True :
        ret, frame = video.read()

        if not ret :
            break
        else :
            ret, buffer = cv2.imencode('.jpeg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n' b'Content-type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def record_video() :
    print('start recording')
    global RECORDING
    # timestamp format: 'YYYY-MM-DD HH:MM:SS'
    current_timestamp = datetime.now()
    timestamp = current_timestamp.strftime('%Y-%m-%d %H:%M:%S')
    video_id = current_timestamp.strftime('%Y%m%d%H%M%S')
    video_name = current_timestamp.strftime('%Y%m%d_%H%M%S')
    video_filename = f'storage/{video_name}.mp4'
    file_path = os.path.join(MAIN_DIRECTORY, video_filename)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(file_path, fourcc, 30.0, (640, 480))

    if not out.isOpened() :
        print('Error: failed to open video file')
        return
    
    if not video.isOpened() :
        print('Error: failed to open video stream')
        return
    
    start_time = time.time()
    msg_arduino('turnLightOn')

    # record video for 30 seconds or until the recording flag is set to False
    while RECORDING and (time.time() - start_time) < 30 :
        ret, frame = video.read()

        if ret :
            frame = cv2.resize(frame, (640, 480))
            out.write(frame)
        else :
            print('Error: failed to read video frame')

    print('stop recording')
    msg_arduino('turnLightOff')
    RECORDING = False
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


# test connection with API
@api.route('/api', methods=['GET'])
def test_connection() :
    return jsonify({'message': 'API is working'}), 200


# TODO: test
# send the live stream from the camera with type multipart/x-mixed-replace
@api.route('/api/live_stream', methods=['GET'])
def get_live_stream() :
    return Response(video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


# needed multicore raspberry pi
@api.route('/api/bell', methods=['GET'])
def start_recording() :
    global RECORDING, recording_thread

    if not RECORDING : 
        RECORDING = True
        recording_thread = threading.Thread(target=record_video)
        recording_thread.start()

    return jsonify({'message': 'Started recording for 30 seconds'}), 200


@api.route('/api/video_url/<timestamp>', methods=['GET'])
def get_url(timestamp) :
    connection = create_db_connection()
    cursor = connection.cursor()
    attempts = 0
    # replace '-', ':' and ' ' by '' (timestamp format: 'YYYY-MM-DD HH:MM:SS')
    video_id = timestamp.replace('-', '').replace(':', '').replace(' ', '')

    while attempts < MAX_ATTEMPTS :
        try :
            cursor.execute(
                "SELECT url FROM videos WHERE video_id = %s;",
                (video_id,)
            )
            url = cursor.fetchone()

            if url :
                return jsonify({'url': url[0]}), 200
            else :
                return jsonify({'error': 'Video not found'}), 404
        except Exception as e :
            attempts += 1
            print(e)
        finally :
            cursor.close()
            connection.close()

    # 500 Internal Server Error
    return jsonify({'error': 'Failed to retrieve video URL'}), 500


@api.route('/api/video_timestamps', methods=['GET'])
def get_timestamps() :
    connection = create_db_connection()
    cursor = connection.cursor()
    attempts = 0

    while attempts < MAX_ATTEMPTS :
        try :
            cursor.execute("SELECT created_at FROM videos;")
            timestamps = cursor.fetchall()

            if timestamps :
                return jsonify({'timestamps': [str(timestamp[0]) for timestamp in timestamps]}), 200
            else :
                return jsonify({'error': 'No videos found'}), 404
        except Exception as e :
            attempts += 1
            print(e)
        finally :
            cursor.close()
            connection.close()

    # 500 Internal Server Error
    return jsonify({'error': 'Failed to retrieve timestamps'}), 500


@api.route('/api/video_stream/<timestamp>', methods=['GET'])
def get_video(timestamp) :
    connection = create_db_connection()
    cursor = connection.cursor()
    attempts = 0
    # replace '-', ':' and ' ' by '' (timestamp format: 'YYYY-MM-DD HH:MM:SS')
    video_id = timestamp.replace('-', '').replace(':', '').replace(' ', '')

    while attempts < MAX_ATTEMPTS :
        try :
            cursor.execute(
                "SELECT url FROM videos WHERE video_id = %s;",
                (video_id,)
            )
            url = cursor.fetchone()

            if url :
                relative_path = url[0]
                file_path = os.path.join(MAIN_DIRECTORY, relative_path)

                if not os.path.exists(file_path) :
                    return jsonify({'error': 'Video file not found in the specified directory'}), 404
                
                return send_file(file_path, mimetype='video/mp4'), 200
            else :
                return jsonify({'error': 'Video not found'}), 404
        except Exception as e :
            attempts += 1
            print(e)
        finally :
            cursor.close()
            connection.close()

    # 500 Internal Server Error
    return jsonify({'error': 'Failed to retrieve video'}), 500


@api.route('/api/video_delete/<int:video_id>', methods=['DELETE'])
def delete_video(video_id) :
    connection = create_db_connection()
    cursor = connection.cursor()
    attempts = 0

    while attempts < MAX_ATTEMPTS :
        try :
            cursor.execute(
                "SELECT url FROM videos WHERE video_id = %s;",
                (video_id,)
            )
            url = cursor.fetchone()

            if not url :
                return jsonify({'error': 'Video not found'}), 404

            file_path = os.path.join(MAIN_DIRECTORY, url[0])

            if not os.path.exists(file_path) :
                return jsonify({'error': 'Video file not found in the specified directory'}), 404

            cursor.execute(
                "DELETE FROM videos WHERE video_id = %s;",
                (video_id,)
            )
            connection.commit()
            os.remove(file_path)

            return jsonify({'message': 'Video deleted successfully'}), 200
        except Exception as e :
            attempts += 1
            print(e)
        finally :
            cursor.close()
            connection.close()

    # 500 Internal Server Error
    return jsonify({'error': 'Failed to delete video'}), 500


if __name__ == '__main__' :
    # this API will be accessible from the local network
    ip_address = get_current_ip()
    api.run(host=ip_address, port=8888)
