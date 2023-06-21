import tkinter as tk
import tkinter as ttk
from tkinter import filedialog
import subprocess
from sklearn.neighbors import KNeighborsClassifier
import cv2
import pickle
import numpy as np
import os
import csv
import time
from datetime import datetime

from win32com.client import Dispatch


def register_script(name):
    video = cv2.VideoCapture(0)
    facedetect = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')

    faces_data = []
    i = 0

    while True:
        ret, frame = video.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = facedetect.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            crop_img = frame[y:y+h, x:x+w, :]
            resized_img = cv2.resize(crop_img, (50, 50))
            if len(faces_data) <= 100 and i % 10 == 0:
                faces_data.append(resized_img)
            i = i+1
            cv2.putText(frame, str(len(faces_data)), (50, 50),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (50, 50, 255), 1)
        cv2.imshow("Frame", frame)
        k = cv2.waitKey(1)
        if k == ord('q') or len(faces_data) == 100:
            break
    video.release()
    cv2.destroyAllWindows()

    faces_data = np.asarray(faces_data)
    faces_data = faces_data.reshape(100, -1)

    if 'names.pkl' not in os.listdir('data/'):
        names = [name]*100
        with open('data/names.pkl', 'wb') as f:
            pickle.dump(names, f)
    else:
        with open('data/names.pkl', 'rb') as f:
            names = pickle.load(f)
        names = names+[name]*100
        with open('data/names.pkl', 'wb') as f:
            pickle.dump(names, f)

    if 'faces_data.pkl' not in os.listdir('data/'):
        with open('data/faces_data.pkl', 'wb') as f:
            pickle.dump(faces_data, f)
    else:
        with open('data/faces_data.pkl', 'rb') as f:
            faces = pickle.load(f)
        faces = np.append(faces, faces_data, axis=0)
        with open('data/faces_data.pkl', 'wb') as f:
            pickle.dump(faces, f)

def login():
    def speak(str1):
        speak = Dispatch(("SAPI.SpVoice"))
        speak.Speak(str1)

    video = cv2.VideoCapture(0)
    facedetect = cv2.CascadeClassifier("data/haarcascade_frontalface_default.xml")

    with open("data/names.pkl", "rb") as w:
        LABELS = pickle.load(w)
    with open("data/faces_data.pkl", "rb") as f:
        FACES = pickle.load(f)

    print("Shape of Faces matrix --> ", FACES.shape)

    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(FACES, LABELS)

    imgBackground = cv2.imread("background.png")

    COL_NAMES = ["NAME", "TIME"]

    while True:
        ret, frame = video.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = facedetect.detectMultiScale(gray, 1.3, 5)
        for x, y, w, h in faces:
            crop_img = frame[y : y + h, x : x + w, :]
            resized_img = cv2.resize(crop_img, (50, 50)).flatten().reshape(1, -1)
            output = knn.predict(resized_img)
            ts = time.time()
            date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
            timestamp = datetime.fromtimestamp(ts).strftime("%H:%M-%S")
            exist = os.path.isfile("Attendance/Attendance_" + date + ".csv")
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (50, 50, 255), 2)
            cv2.rectangle(frame, (x, y - 40), (x + w, y), (50, 50, 255), -1)
            cv2.putText(
                frame,
                str(output[0]),
                (x, y - 15),
                cv2.FONT_HERSHEY_COMPLEX,
                1,
                (255, 255, 255),
                1,
            )
            cv2.rectangle(frame, (x, y), (x + w, y + h), (50, 50, 255), 1)
            attendance = [str(output[0]), str(timestamp)]
        imgBackground[162 : 162 + 480, 55 : 55 + 640] = frame
        cv2.imshow("Frame", imgBackground)
        k = cv2.waitKey(1)
        if k == ord("o"):
            speak("Attendance Taken Successfully")
            time.sleep(2)
            if exist:
                with open("Attendance/Attendance_" + date + ".csv", "+a") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(attendance)
                csvfile.close()
            else:
                with open("Attendance/Attendance_" + date + ".csv", "+a") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(COL_NAMES)
                    writer.writerow(attendance)
                csvfile.close()
        if k == ord("q"):
            break
    video.release()
    cv2.destroyAllWindows()


def open_get_name_window():
    name_window = tk.Toplevel(root)
    name_window.title("Register")
    name_window.geometry("300x100")

    def get_name():
        name = entry.get()
        register_script(name)
        name_window.destroy()

    name_label = tk.Label(name_window, text="Name:", font=("Arial", 14))
    name_label.pack()
    entry = tk.Entry(name_window, font=("Arial", 14))
    entry.pack()

    register_button = tk.Button(name_window, text="Register", font=("Arial", 14), command=get_name)
    register_button.pack()

def generate_report():
    filename = filedialog.askopenfilename(
        initialdir=".",
        title="Select Attendance File",
        filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*"))
    )
    if filename:
        report_window = tk.Toplevel(root)
        report_window.title("Attendance Report")
        
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            report_data = list(reader)
        
       
        for row_idx, row_data in enumerate(report_data):
            for col_idx, cell_data in enumerate(row_data):
                label = tk.Label(report_window, text=cell_data)
                label.grid(row=row_idx, column=col_idx)
        
       
        close_button = tk.Button(report_window, text="Close", font=("Arial", 14), command=report_window.destroy)
        close_button.grid(row=len(report_data), column=0, columnspan=len(report_data[0]))



root = tk.Tk()
root.title("Face Attendance Recognition System")

window_width = 400
window_height = 200
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = int((screen_width/2) - (window_width/2))
y = int((screen_height/2) - (window_height/2))
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

title_label = tk.Label(root, text="FACE ATTENDANCE RECOGNITION", font=("Arial", 16, "bold"))
title_label.pack(pady=20)

register_button = tk.Button(root, text="Register", font=("Arial", 14), command=open_get_name_window)
register_button.pack()

login_button = tk.Button(root, text="Login", font=("Arial", 14), command=login)
login_button.pack()

generate_report_button = tk.Button(root, text="Generate Report", font=("Arial", 14), command=generate_report)
generate_report_button.pack()

root.mainloop()
