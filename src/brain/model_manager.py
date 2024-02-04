from transformers import AutoModel, AutoProcessor, AutoImageProcessor
import torch
from openai import OpenAI, AsyncClient
import bentoml
from PIL import Image

import ftfy, html, re


class ModelManager():
    def __init__(self):
        try:
            self.device = "cpu"
            self.image_model = AutoModel.from_pretrained(
                "google/siglip-base-patch16-256-multilingual",
                trust_remote_code=True,
            ).to(self.device)

            self.image_processor = AutoImageProcessor.from_pretrained(
                "google/siglip-base-patch16-256-multilingual"
            )

            self.text_processor = AutoProcessor.from_pretrained(
                "google/siglip-base-patch16-256-multilingual"
            )
            # make async
            self.openai_client = OpenAI()
            self.image_description_model = "gpt-4-vision-preview"

            self.ops_llm = "gpt-4"

            self.image_generation_model = bentoml.SyncHTTPClient("https://sdxl-turbo-j9zy-0217b70f.mt-guc1.bentoml.ai")

            self.image_generation_finetuning_model = "dall-e-2"

        except Exception as e:
            print(f"Error in ModelManager init: {e}")
            raise e

    def get_image_embeddings(self, image):
        image = self.image_processor(images=image, return_tensors="pt").to("cpu")
        with torch.no_grad():
            embedding = self.image_model.get_image_features(**image)
            embedding = embedding / embedding.norm(dim=-1, keepdim=True)
            embedding = embedding.cpu().numpy()[0].tolist()
        return embedding

    def get_text_embeddings(self, text):
        def basic_clean(text):
            text = ftfy.fix_text(text)
            text = html.unescape(html.unescape(text))
            return text.strip()

        def whitespace_clean(text):
            text = re.sub(r"\s+", " ", text)
            text = text.strip()
            return text

        text = whitespace_clean(basic_clean(text))
        inputs = self.text_processor(text, return_tensors="pt", padding="max_length", truncation=True,
                                     max_length=64).to("cpu")
        with torch.no_grad():
            embedding = self.image_model.get_text_features(**inputs)
            embedding = embedding / embedding.norm(dim=-1, keepdim=True)
        return embedding

    def generate_image_from_inspiration_text(self, inspiration_text):
        with self.image_generation_model as client:
            result = client.txt2img(
                guidance_scale=0,
                num_inference_steps=1,
                prompt=inspiration_text,
            )
        image = Image.open(result)
        return image

    def generate_text_from_image(self, image, prompt):
        return (self.openai_client.chat.completions.create(
            model=self.image_description_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image}"},
                        },
                    ],
                }
            ],
            max_tokens=400,
        )).choices[0].message.content

    def llm_prompt_apply(self, prompt):
        return (self.openai_client.chat.completions.create(
            model=self.ops_llm,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
            max_tokens=400,
        )).choices[0].message.content

    def generate_image_from_inspiration_images(self, inspiration_images):
        pass

    def generate_images_from_inspiration(self, inspiration_images, inspiration_text, images_to_generate=2):
        # Prompt engineer this
        image_descriptions = [
            self.generate_text_from_image(image,
                            "Describe the focus object in the image in detail in approximately 150 tokens. "
                            "The goal is to enable a creator to make the main object in this image. "
                            "Don't mention the background or the photograph specifics but focus on the main object.")
            for
            image in inspiration_images]
        image_prompt_info = ""
        for i, image_description in enumerate(image_descriptions):
            image_prompt_info += f"Photo-{i + 1} is {image_description} \n"

        print(image_descriptions)

        if inspiration_text:
            prompt = f'''
                    Create one picture by mixing the image descriptions listed below based on the user instructions.
                    {image_prompt_info}
                    Addtional important requirement from the user is : {inspiration_text}
                '''
        else:
            prompt = f'''
                    Create one picture by imaging a realistic product based on different image descriptions detailed below.
                    {image_prompt_info}
                '''
        print(prompt)
        concise_prompt_template = f'''I want to give the below prompt to a stable diffusion model to generate object images for designing. But the prompt is fairly long and complex. Summarize it to 2-3 self-sufficient sentences for me so that stable diffusion can easily be applied on the prompt. Do not reference first and second images, if needed elaborate on the details without referencing. The most important part of the prompt is the last additional important user rerquirement if mentioned. The output style should be sketch-like and not too realistic. \n {prompt}'''
        concise_prompt = self.llm_prompt_apply(concise_prompt_template)
        print(concise_prompt)
        images = [self.generate_image_from_inspiration_text(concise_prompt) for _ in range(images_to_generate)]
        return images
