import cv2

from msg_arduino import msg_arduino


def video_stream() :
    video = cv2.VideoCapture(0)
    
    msg_arduino('turnLightOn')

    while True : 
        ret, frame = video.read()

        if not ret :
            break
        else :
            ret, buffer = cv2.imencode('.jpeg', frame)
            frame = buffer.tobytes()
            yield (b' --frame\r\n' b'Content-type: imgae/jpeg\r\n\r\n' + frame +b'\r\n')

    msg_arduino('turnLightOff')



# import cv2
# import numpy as np
# from flask import Flask, render_template, Response, stream_with_context, request

# from ip import get_current_ip


# video = cv2.VideoCapture(0)
# app = Flask(__name__)


# def video_stream() :
#     while True : 
#         ret, frame = video.read()

#         if not ret :
#             break
#         else :
#             ret, buffer = cv2.imencode('.jpeg', frame)
#             frame = buffer.tobytes()
#             yield (b' --frame\r\n' b'Content-type: imgae/jpeg\r\n\r\n' + frame +b'\r\n')


# @app.route('/camera')
# def camera() :
#     return render_template('camera.html')


# @app.route('/video_feed')
# def video_feed() : 
#     return Response(video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


# if __name__ == '__main__' :
#     ip_address = get_current_ip()
#     app.run(host=ip_address, port='9999', debug=False)
