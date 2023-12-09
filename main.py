import os
import sys
import cv2
import tkinter as tk
from tkinter import ttk
from tkinter import Label
from PIL import Image, ImageTk
import model
import pygame

class CameraApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.color1 = "#caf0f8" #연한파랑
        self.color2 = "#48cae4" #연한파랑2
        self.color3 = "#03045e" #진한파랑

        '''youtube_links = {
            'happy': 'https://youtu.be/WdBVXXNRRBc?si=FKbyUB1a0FNZRAQZ',
            'sad': 'https://youtu.be/LlDSMktrlwE?si=phxEPKstJXsIPSV8',
            'expressionless': 'https://youtu.be/YGX-Y4XngXc?si=VeNar3IpjWhtNB_I',
            'angry': 'https://youtu.be/Tc0Z6A7xl7Y?si=O3GQAjW9F-lJGsHI',
            'surprise': 'https://youtu.be/eaqVX9IMACQ?si=Z9i9C4mAsnw2_HMZ' 
        }'''

        # 창 설정
        self.title("Emotion Detection")
        self.geometry("800x700")

        # 카메라 설정
        self.cap = cv2.VideoCapture(0)

        # 배경색 설정
        self.configure(bg = self.color1)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # language_dicts를 초기화
        self.language_dicts = {
            "English": {"welcome_text": "Welcome~!", "emotion_label": "Your mood today is ...", "emotion_res": "Your mood today is "},
            "Korean": {"welcome_text": "환영합니다~!", "emotion_label": "오늘의 당신 기분은 ...", "emotion_res": "오늘의 당신 기분은 "},
            "Kazakh": {"welcome_text": "Қош келдіңіз~!", "emotion_label": "Бүгінгі сіздің көңіл-күйіңіз ...", "emotion_res": "Бүгінгі сіздің көңіл-күйіңіз "},
            "Russian": {"welcome_text": "Добро пожаловать~!", "emotion_label": "Сегодняшное ваше настроение ...", "emotion_res": "Сегодняшное ваше настроение "}
        }

        # 현재 언어를 기본값으로 설정
        current_language = "Korean"

        # 텍스트 라벨 생성 및 추가
        self.text_label = Label(self, text=self.language_dicts[current_language]["welcome_text"], bg=self.color1, fg=self.color3, font=("Times New Roman", 30))
        self.text_label.grid(row=0, column=0, sticky="ew", pady=(30, 25))

        # 이미지 라벨(카메라 출력) 생성 및 추가
        self.emotion_image = Label(self, bg=self.color1)
        self.emotion_image.grid(row=1, column=0, sticky="nsew")

        # 감정 분석 결과 라벨 생성 및 추가
        self.emotion_label = Label(self, text=self.language_dicts[current_language]["emotion_label"], bg=self.color1, fg=self.color3, font=("Times New Roman", 30))
        self.emotion_label.grid(row=2, column=0, sticky="ew", pady=(20, 40))

        # emotion_res 라벨 생성 및 추가
        self.emotion_res = Label(self, text="", bg=self.color1, fg=self.color3, font=("Times New Roman", 20))
        self.emotion_res.grid(row=2, column=0, sticky="ew", pady=(20, 40))
        self.emotion_res.grid_remove()  # 초기에는 이 라벨을 숨김.

        self.is_music_playing = False
        
        # 상단 오른쪽 이미지 라벨 생성 및 추가
        self.top_right_image = Label(self, bg=self.color1)
        self.top_right_image.grid(row=0, column=1, sticky="ne")
        
        # 음악 제어 및 이미지 변경 이벤트 바인딩
        self.top_right_image.bind("<Button-1>", self.toggle_music)

        # 'test_data' 폴더 생성
        if not os.path.exists('test_data'):
            os.makedirs('test_data')

        self.after(5000, self.start_photo_sequence)

        style = ttk.Style(self)
        style.configure('TCombobox', fieldbackground=self.color2, foreground=self.color3)
        style.map('TCombobox',
                fieldbackground=[('readonly', self.color3)],
                selectforeground=[('readonly', self.color1)])

        # 언어 선택 드롭다운 생성
        self.language_var = tk.StringVar(self)
        self.language_combo = ttk.Combobox(self, textvariable=self.language_var, values=["English", "Korean", "Kazakh", "Russian"], state="readonly", width=7)
        self.language_combo.set("Korean")  # 기본값 설정
        self.language_combo.grid(row=0, column=0, sticky="nw")
        self.language_combo.bind("<<ComboboxSelected>>", self.change_language)

        self.emotions_texts = {
            "English": {
                'happy': "happy",
                'sad': "sad",
                'expressionless': "expressionless",
                'angry': "angry",
                'surprise': "surprised"
            },
            "Korean" : {
                'happy': "행복합니다",
                'sad': "슬픕니다",
                'expressionless': "편안한 상태입니다",
                'angry': "화나 있습니다",
                'surprise': "놀랐습니다"
            },
            "Kazakh": {
                'happy': "бақытты",
                'sad': "қайғылы",
                'expressionless': "әсерсіз",
                'angry': "ашулы",
                'surprise': "таңғалған"
            },
            "Russian": {
                'happy': "счастливый",
                'sad': "грустный",
                'expressionless': "без выражения",
                'angry': "сердитый",
                'surprise': "удивленный"
            }
        }

    def change_language(self, _):
        # 선택된 언어에 따라 UI 텍스트 업데이트
        lang_dict = self.language_dicts[self.language_var.get()]
        self.text_label.config(text=lang_dict["welcome_text"])
        self.emotion_label.config(text=lang_dict["emotion_label"])

        # 현재 활성화된 감정 텍스트가 있으면, 그것도 업데이트
        if hasattr(self, 'current_emotion'):
            emotion_key = self.current_emotion.split()[-1]
            emotion_text = self.emotions_texts[self.language_var.get()].get(emotion_key, "")
            if emotion_text:
                self.emotion_res.config(text=f"{lang_dict['emotion_res']} {emotion_text}")

    def start_photo_sequence(self):
        self.photo_counter = 0
        self.take_photo()

    def take_photo(self):
        if self.photo_counter < 10:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                filename = f'test_data/test_data{self.photo_counter}.jpg'
                cv2.imwrite(filename, frame)
                self.photo_counter += 1
                self.after(1000, self.take_photo)
        else:
            self.analyze_and_display_emotion()  # 사진 촬영 완료 후 감정 분석

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (600, 440))
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.emotion_image.imgtk = imgtk
            self.emotion_image.configure(image=imgtk)
            self.emotion_image.after(10, self.update_frame)

    def analyze_and_display_emotion(self):
        most_common_emotion = model.analyze_emotions('test_data', 10)
        self.display_emotion(most_common_emotion)

    def toggle_music(self, event):
        if self.is_music_playing:
            pygame.mixer.music.pause()  # 음악을 일시 정지
            self.is_music_playing = False
            off_image = ImageTk.PhotoImage(Image.open('./off_image.png').resize((50, 50), Image.Resampling.LANCZOS))
            self.top_right_image.config(image=off_image)
            self.top_right_image.image = off_image  # 음악이 꺼졌을 때의 이미지로 변경
        else:
            pygame.mixer.music.unpause()
            self.is_music_playing = True
            on_image = ImageTk.PhotoImage(Image.open('./on_image.png').resize((50, 50), Image.Resampling.LANCZOS))
            self.top_right_image.config(image=on_image)
            self.top_right_image.image = on_image   # 음악이 켜졌을 때의 이미지로 변경

    def set_top_right_image(self, image_path):
        if os.path.exists(image_path):
            img = Image.open(image_path)
            img_resized = img.resize((50, 50), Image.Resampling.LANCZOS)  # 사이즈는 예시
            photo = ImageTk.PhotoImage(img_resized)
            self.top_right_image.config(image=photo)
            self.top_right_image.image = photo  # 참조 유지

    def display_emotion(self, emotion):
        # 현재 언어 가져오기
        current_language = self.language_var.get()

        # 현재 언어에 맞는 감정 설명을 찾기
        emotion_key = emotion.split()[-1]  # 예: 'happy'에서 감정 키를 추출
        emotion_text = self.emotions_texts[current_language].get(emotion_key)

        # 현재 언어에 맞는 결과 라벨 포맷 텍스트 찾기
        label_text = self.language_dicts[current_language]["emotion_res"]

        if emotion_text:
            # 감정 결과 라벨 업데이트
            self.emotion_res.config(text=f"{label_text} {emotion_text}")
            # 기존 감정 라벨 숨기기 및 결과 라벨 표시r
            self.emotion_label.grid_remove()
            self.emotion_res.grid()

            # 카메라 끄기
            self.cap.release()
            self.emotion_image.pack_forget()  # 기존 카메라 라벨 삭제

            # 결과에 따른 이미지와 음악 재생
            image_path = f'./감정.png/{emotion_key}.png'
            music_path = f'./감정.mp3/{emotion_key}.mp3'

            if os.path.exists(image_path):
                img = Image.open(image_path)
                img_resized = img.resize((600, 440), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img_resized)
                self.emotion_image.config(image=photo)
                self.emotion_image.image = photo

            if os.path.exists(music_path):
                pygame.mixer.init()
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.play(-1)
                self.is_music_playing = True
                self.set_top_right_image('./on_image.png')

            # 현재 감정 상태 저장
            self.current_emotion = emotion

if __name__ == '__main__':
    app = CameraApp()
    app.update_frame()  
    app.mainloop()