from keras.models import load_model
from PIL import Image, ImageOps
import numpy as np

# 모델 파일과 레이블 파일의 경로를 지정
MODEL_PATH = "./keras_model.h5" #epoch = 2000, batch = 16, lr = 0.0005
LABELS_PATH = "./labels.txt"

# 모델을 로드
model = load_model(MODEL_PATH, compile=False)

# 레이블을 로드
with open(LABELS_PATH, "r") as file:
    class_names = file.readlines()

# 데이터 배열을 초기화
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

def analyze_emotion(image_path):
    # 이미지를 로드하고 전처리
    image = Image.open(image_path).convert("RGB")
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    image_array = np.asarray(image)
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
    data[0] = normalized_image_array

    # 모델을 사용하여 예측하고 결과를 반환
    prediction = model.predict(data)
    index = np.argmax(prediction)
    class_name = class_names[index].strip()
    confidence_score = prediction[0][index]

    return class_name, confidence_score

def analyze_emotions(test_data_folder, num_images=10):
    emotion_count = {}

    for i in range(num_images):
        image_path = f'{test_data_folder}/test_data{i}.jpg'
        emotion, _ = analyze_emotion(image_path)

        if emotion not in emotion_count:
            emotion_count[emotion] = 0
        emotion_count[emotion] += 1

    most_common_emotion = max(emotion_count, key=emotion_count.get)
    return most_common_emotion
