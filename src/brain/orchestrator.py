import uuid
from PIL import Image
import base64
from io import BytesIO

from src.utils.artifact_manager import ArtifactManager
from src.brain.image_ops import IMAGE_STORAGE_ABS_PATH

class BrainOrchestrator:
    def __init__(self, artifact_manager: ArtifactManager):
        self.image_vector_repository = artifact_manager.image_vector_repository
        self.model_manager = artifact_manager.model_manager
        self.image_ops = artifact_manager.image_ops
        self.local_images_db = {}

    def upload_image(self, image_bytes, image_filename, description):
        image_id = str(uuid.uuid4())

        saved_filename = self.image_ops.save_imagebytes_to_disk(image_bytes, image_id, image_filename)
        image_obj = self.image_ops.load_image_from_disk_for_processing(saved_filename)

        image_vector = self.model_manager.get_image_embeddings(image_obj)

        self.image_vector_repository.add_document(
            {"_id": image_id, "filename": saved_filename, "$vector": image_vector, "description": description})
        self.local_images_db[image_id] = {"id": image_id, "filename": image_filename}
        return image_id

    def get_image_by_id(self, image_id):
        image_meta = self.local_images_db.get(image_id)
        if image_meta is None:
            return None
        return self.image_ops.load_image_from_disk_to_bytes(image_meta['filename'])

    def get_images_from_inspiration_text(self, text_prompt, k):
        text_vector = self.model_manager.get_text_embeddings(text_prompt)
        similar_image_docs = self.image_vector_repository.get_top_k_similar(text_vector.cpu().numpy()[0], k)
        # for doc in similar_image_docs:
        #     doc['filename'] = f"{IMAGE_STORAGE_ABS_PATH}/{doc['filename']}"
        return similar_image_docs

    def generate_images_from_inspiration_images_and_prompt(self, image_file_paths, text_prompt, k):
        def encode_image(image):
            if isinstance(image, Image.Image):
                buffered = BytesIO()
                image.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
                return img_str
            else:
                raise TypeError("The function requires a PIL.Image.Image object")
        images = [self.image_ops.load_image_from_disk_for_processing(image_file) for image_file in image_file_paths]
        rgb_images = []
        for image in images:
            image = image.resize((image.width // 2, image.height // 2))
            image = image.convert('RGB')
            image = encode_image(image)
            rgb_images.append(image)
        generated_images = self.model_manager.generate_images_from_inspiration(rgb_images, text_prompt, k)
        generated_image_paths = [self.image_ops.save_pil_image_to_disk(image) for image in generated_images]
        output = []
        for image_path in generated_image_paths:
            item_dict = {"filename": image_path, "_id": image_path.split('.')[0], "description": "$19.99"}
            output.append(item_dict)
        return output




    def generate_text_elaboration_of_image(self, image_file_path):
        def encode_image(image):
            if isinstance(image, Image.Image):
                buffered = BytesIO()
                image.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
                return img_str
            else:
                raise TypeError("The function requires a PIL.Image.Image object")
        image = self.image_ops.load_image_from_disk_for_processing(image_file_path)
        image = image.resize((image.width // 2, image.height // 2))
        image = image.convert('RGB')
        image = encode_image(image)

        prompt = "Describe this image in detail so that people with disability can understand it. Respond in sections and only markdown so that it can directly be put on html directly. Focus only on the main object in the image and not on background or surface."
        return self.model_manager.generate_text_from_image(image, prompt)
