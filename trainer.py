import os
import cv2
import numpy as np
from PIL import Image

recognizer = cv2.face.LBPHFaceRecognizer.create()
path = "dataset"

def get_image_with_id(path):
    if not os.path.exists(path):
        print("Error: Dataset directory does not exist")
        exit()
    images_paths = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.jpg')]
    if not images_paths:
        print("Error: No images found in dataset")
        exit()
    faces = []
    ids = []
    for single_image_path in images_paths:
        try:
            faceImg = Image.open(single_image_path).convert('L')
            faceNp = np.array(faceImg, np.uint8)
            id = int(os.path.split(single_image_path)[-1].split(".")[1])
            faces.append(faceNp)
            ids.append(id)
            cv2.imshow("Training", faceNp)
            cv2.waitKey(10)
        except Exception as e:
            print(f"Error processing {single_image_path}: {e}")
    return np.array(ids), faces

ids, faces = get_image_with_id(path)
if len(ids) == 0:
    print("Error: No valid images to train")
    exit()
recognizer.train(faces, ids)
if not os.path.exists("recognizer"):
    os.makedirs("recognizer")
recognizer.save("recognizer/trainingdata.yml")
print("Training completed successfully")
cv2.destroyAllWindows()
