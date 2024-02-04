import uuid
import os
import falcon
from PIL import Image
from mimetypes import guess_type

IMAGE_STORAGE_PATH = '/Users/krishna/Desktop/Projects/ragathon2024-FE/rag-a-thon-2024/frontend/public'
IMAGE_STORAGE_ABS_PATH = '/Users/krishna/Desktop/Projects/ragathon2024-FE/rag-a-thon-2024/frontend/public'

class ImageOps():
    def __init__(self):
        pass

    def load_image_from_disk_for_processing(self, image_filename):
        if not image_filename or not image_filename.endswith(('.jpg', '.png', '.jpeg')):
            raise ValueError("Image path is invalid")
        image_path = os.path.join(IMAGE_STORAGE_PATH, image_filename)
        print(image_path)
        return Image.open(image_path)

    def save_imagebytes_to_disk(self, image_bytes, image_id, image_filename):
        image_filename = image_filename.replace('/', '_')
        filename = f"{image_id}_{image_filename}"
        image_path = os.path.join(IMAGE_STORAGE_PATH, filename)
        with open(image_path, 'wb') as out_file:
            while True:
                chunk = image_bytes.read(4096)
                if not chunk:
                    break
                out_file.write(chunk)
        return filename

    def save_pil_image_to_disk(self, pil_image):
        id = str(uuid.uuid4())
        filename = f"{id}.jpg"
        image_path = os.path.join(IMAGE_STORAGE_PATH, filename)
        pil_image.save(image_path)
        return filename


    def delete_image_from_disk(self, image_filename):
        file_path = os.path.join(IMAGE_STORAGE_PATH, image_filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        return True

    def load_image_from_disk_to_falcon_response(self, image_filename, falcon_resp):
        if not image_filename or image_filename.endswith(('.jpg', '.png', '.jpeg')):
            raise ValueError("Image path is invalid")
        image_path = os.path.join(IMAGE_STORAGE_PATH, image_filename)

        if not os.path.exists(image_path):
            raise falcon.HTTPNotFound()

        falcon_resp.content_type = guess_type(image_path)[0]
        falcon_resp.stream = open(image_path, 'rb')
        falcon_resp.stream_len = os.path.getsize(image_path)
        return


