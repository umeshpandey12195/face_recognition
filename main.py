import os.path
import datetime
import pickle
import requests

import tkinter as tk
import cv2
from PIL import Image, ImageTk
import face_recognition

import util
from test import test


class App:
    def __init__(self):
        self.main_window = tk.Tk()
        self.main_window.geometry("1200x520+350+100")

        self.login_button_main_window = util.get_button(self.main_window, 'login', 'green', self.login)
        self.login_button_main_window.place(x=750, y=200)

        self.logout_button_main_window = util.get_button(self.main_window, 'logout', 'red', self.logout)
        self.logout_button_main_window.place(x=750, y=300)

        self.register_new_user_button_main_window = util.get_button(self.main_window, 'register new user', 'gray',
                                                                    self.register_new_user, fg='black')
        self.register_new_user_button_main_window.place(x=750, y=400)

        self.webcam_label = util.get_img_label(self.main_window)
        self.webcam_label.place(x=10, y=0, width=700, height=500)

        self.add_webcam(self.webcam_label)

        self.db_dir = './db'
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)

        self.log_path = './log.txt'

    def add_webcam(self, label):
        if 'cap' not in self.__dict__:
            self.cap = cv2.VideoCapture(0)

        self._label = label
        self.process_webcam()

    def process_webcam(self):
        ret, frame = self.cap.read()
        face_locations = face_recognition.face_locations(frame)
        # Draw bounding boxes around the detected faces
        for face_location in face_locations:
            top, right, bottom, left = face_location
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        self.most_recent_capture_arr = frame
        img_ = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)
        self.most_recent_capture_pil = Image.fromarray(img_)
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        self._label.imgtk = imgtk
        self._label.configure(image=imgtk)

        self._label.after(20, self.process_webcam)

    def login(self):
        # Capture frame from the webcam
        ret, frame = self.cap.read()

        # Send frame to the login API on EC2
        api_url = 'http://your-ec2-public-ip:5000/login'  # Replace with your EC2 public IP
        response = requests.post(api_url, json={'frame': frame.tolist()})
        result = response.json()

        # Handle the response from the API as needed
        if result['status'] == 'success':
            name = util.recognize(frame, self.db_dir)
            if name in ['unknown_person', 'no_persons_found']:
                util.msg_box('Ups...', 'Unknown user. Please register a new user or try again.')
            else:
                util.msg_box('Welcome back!', 'Welcome, {}.'.format(name))
        else:
            util.msg_box('Login Failed!', 'Login unsuccessful. {}'.format(result['message']))
    
    def logout(self):
        _, img_encoded = cv2.imencode('.jpg', self.most_recent_capture_arr)
        files = {'image': ('image.jpg', img_encoded.tostring(), 'image/jpeg')}
        response = requests.post('http://your-ec2-public-ip:5000/logout', files=files)

        result = response.json()
        if result['status'] == 'success':
            util.msg_box('Goodbye!', result['message'])
            with open(self.log_path, 'a') as f:
                f.write('{},{},out\n'.format(result['name'], datetime.datetime.now()))
        else:
            util.msg_box('Logout Failed!', result['message'])


    def register_new_user(self):
        self.register_new_user_window = tk.Toplevel(self.main_window)
        self.register_new_user_window.geometry("1200x520+370+120")

        self.accept_button_register_new_user_window = util.get_button(self.register_new_user_window, 'Accept', 'green', self.accept_register_new_user)
        self.accept_button_register_new_user_window.place(x=750, y=300)

        self.try_again_button_register_new_user_window = util.get_button(self.register_new_user_window, 'Try again', 'red', self.try_again_register_new_user)
        self.try_again_button_register_new_user_window.place(x=750, y=400)

        self.capture_label = util.get_img_label(self.register_new_user_window)
        self.capture_label.place(x=10, y=0, width=700, height=500)

        ret, frame = self.cap.read()
        face_locations = face_recognition.face_locations(frame)

        if face_locations:
            top, right, bottom, left = face_locations[0]
            self.register_new_user_capture = frame[top:bottom, left:right]
            img_ = cv2.cvtColor(self.register_new_user_capture, cv2.COLOR_BGR2RGB)
            self.most_recent_capture_pil = Image.fromarray(img_)
            imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
            self.capture_label.imgtk = imgtk
            self.capture_label.configure(image=imgtk)

        self.capture_label.after(20, self.capture_register_new_user)


    def try_again_register_new_user(self):
        self.register_new_user_window.destroy()

    def add_img_to_label(self, label):
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        label.imgtk = imgtk
        label.configure(image=imgtk)

        self.register_new_user_capture = self.most_recent_capture_arr.copy()

    def start(self):
        self.main_window.mainloop()

    def accept_register_new_user(self):
        _, img_encoded = cv2.imencode('.jpg', self.register_new_user_capture)
        files = {'image': ('image.jpg', img_encoded.tostring(), 'image/jpeg')}
        response = requests.post('http://your-ec2-public-ip:5000/register', files=files)

        result = response.json()
        if result['status'] == 'success':
            util.msg_box('Success!', result['message'])
            self.register_new_user_window.destroy()
        else:
            util.msg_box('Registration Failed!', result['message'])

if __name__ == "__main__":
    app = App()
    app.start()