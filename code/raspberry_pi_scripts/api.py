import os
# import cv2
# import time
import psycopg2
# import threading
from flask import Flask, jsonify, send_file, Response, render_template
# from datetime import datetime
from dotenv import load_dotenv

from ip import get_current_ip
from msg_arduino import msg_arduino
from record_video import record_video
from live_stream import video_stream

# load the environment variables from the .env file
load_dotenv()
MAX_ATTEMPTS = 5    # maximum number of attempts to connect to the database
RECORDING = False
# video = cv2.VideoCapture(0)
api = Flask(__name__)
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


# test connection with API
@api.route('/api', methods=['GET'])
def test_connection() :
    return jsonify({'message': 'API is working'}), 200


@api.route('/camera')
def camera() :
    return render_template('camera.html')


@api.route('/video_feed')
def video_feed() : 
    return Response(video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


# needed multicore raspberry pi
@api.route('/api/bell', methods=['GET'])
def start_recording() :
    global RECORDING
    # global RECORDING, recording_thread
    
    if not RECORDING : 
        RECORDING = True
        # recording_thread = threading.Thread(target=record_video)
        # recording_thread.start()
        record_video()
        RECORDING = False

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
