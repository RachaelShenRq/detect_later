import cv2
import time
import smtplib
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from playsound import playsound  # Import playsound for sound playback

# Set the cutoff time for lateness
LATE_TIME = "09:00"

# Initialize the camera
cap = cv2.VideoCapture(0)

# Load the face detection model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def check_late_time():
    """Check if the current time is past 9:00 AM"""
    current_time = datetime.now().strftime("%H:%M")
    return current_time > LATE_TIME

def capture_and_save_photo():
    """Capture a photo and save it locally"""
    ret, frame = cap.read()
    if ret:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"latecomer_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        play_camera_shutter_sound()  # Play the shutter sound after saving the photo
        return filename
    return None

def play_camera_shutter_sound():
    """Play the camera shutter sound"""
    playsound("Camera_sound.mp3")  # Use playsound to play the MP3 file

def send_email_with_attachment(to_email, subject, body, filename):
    """Send an email with an attachment"""
    from_email = "your_email@gmail.com"
    password = "your_password"

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))
    attachment = open(filename, "rb")
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f"attachment; filename= {filename}")
    msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, password)
    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()

def detect_and_capture():
    """Detects if a person enters the room and takes a photo"""
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) > 0 and check_late_time():
            photo_filename = capture_and_save_photo()
            if photo_filename:
                send_email_with_attachment("shen_liege@hotmail.com", "Late Arrival Notice", "Latecomer detected, please see attached photo.", photo_filename)

        # Display the window showing the detection
        cv2.imshow("Late Detection", frame)
        
        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    detect_and_capture()
