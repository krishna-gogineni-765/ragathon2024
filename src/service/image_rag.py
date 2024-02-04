from src.brain.orchestrator import BrainOrchestrator
import falcon
import json


class ImageRagResource:
    def __init__(self, artifact_manager):
        self.brain = BrainOrchestrator(artifact_manager)

    def on_post(self, req, resp):
        search_query = req.get_param('search_query') or ""
        iteration = req.get_param('iteration') or "mid"
        fine_tuning_prompt = req.get_param('fine_tuning_prompt') or ""
        inspiration_image_filenames = req.get_param('inspiration_image_filenames', default="")
        try:
            if inspiration_image_filenames:
                inspiration_image_filenames = inspiration_image_filenames.split('&')
        except json.JSONDecodeError:
            raise falcon.HTTPBadRequest('Invalid JSON', 'Inspiration image IDs should be a valid list separated with &')


        if iteration == "first":
            relevant_images_dict = self.brain.get_images_from_inspiration_text(search_query, 5)
            resp.media = relevant_images_dict

        elif iteration == "mid":
            if not inspiration_image_filenames:
                raise falcon.HTTPBadRequest('Missing Data', 'Mid iteration requires at least one inspiration image ID.')
            generated_images_dict = self.brain.generate_images_from_inspiration_images_and_prompt(inspiration_image_filenames,
                                                                                                  fine_tuning_prompt, 3)
            resp.media = generated_images_dict

        elif iteration == "final":
            if not inspiration_image_filenames or len(inspiration_image_filenames) != 1:
                raise falcon.HTTPBadRequest('Invalid Request',
                                            'Final iteration requires exactly one inspiration image ID.')
            text_description_of_image = self.brain.generate_text_elaboration_of_image(inspiration_image_filenames[0])
            resp.media = {'description': text_description_of_image}
        else:
            raise falcon.HTTPBadRequest('Invalid Iteration', 'Iteration must be one of [first, mid, final].')

        resp.status = falcon.HTTP_200
