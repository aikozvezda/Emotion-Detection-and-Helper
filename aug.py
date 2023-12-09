from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.preprocessing import image
import os
import numpy as np
import random

# 이미지에 무작위 색상 변화를 적용하는 함수
def random_color_shift(img):
    img = np.array(img, dtype=float)
    shift_values = [random.uniform(0.8, 1.2) for _ in range(3)]
    img *= shift_values  # 색상 변화 적용
    img = np.clip(img, 0, 255)
    return img.astype(np.uint8)

# 데이터 생성기 설정
datagen = ImageDataGenerator(
    preprocessing_function=random_color_shift,  # Use the correct function name
    horizontal_flip=True  # 수평 플립 활성화
)

# 이미지 증강 함수
def augment_images(image_directory, save_directory, augment_per_image):
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    total = 0
    file_list = os.listdir(image_directory)

    for filename in file_list:
        image_path = os.path.join(image_directory, filename)
        img = image.load_img(image_path)
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)

        i = 0
        for _ in datagen.flow(x, batch_size=1, save_to_dir=save_directory, save_prefix='aug', save_format='jpg'):
            i += 1
            if i >= augment_per_image:
                break
        total += i

    return total

# Set the number of augmented images per original image
augment_per_image = 6  # You want 300 additional images for 50 original images

# The directory where your original images are located
image_directory = './surprise'

# The directory where you want to save the augmented images
save_directory = './surprise_aug'

# Call the augment_images function with the defined parameters
augmented_images_count = augment_images(image_directory, save_directory, augment_per_image)

# Print out the total number of images after augmentation
print("Total augmented images:", augmented_images_count)
