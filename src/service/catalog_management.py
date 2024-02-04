import uuid
import falcon

from src.brain.orchestrator import BrainOrchestrator

images_db = {}

class ImageLibraryResource:
    def __init__(self, artifact_manager):
        self.brain = BrainOrchestrator(artifact_manager)

    def on_post(self, req, resp):
        """Handles image uploads with descriptions."""
        description = req.get_param('description') or 'No description'
        image = req.get_param('image')

        if image is None:
            raise falcon.HTTPBadRequest('Missing Image', 'An image file is required.')

        image_id = self.brain.upload_image(image.file, image.filename, description)

        resp.media = {'id': image_id, 'message': 'Image uploaded successfully'}
        resp.status = falcon.HTTP_201
        return resp

    # def on_get(self, req, resp, image_id):
    #     """Retrieves an image by ID."""
    #     image_meta = images_db.get(image_id)
    #
    #     if image_meta is None:
    #         raise falcon.HTTPNotFound()
    #
    #     self.image_ops.load_image_from_disk_to_falcon_response(image_meta['filename'], resp)
    #     return resp
    #
    # def on_delete(self, req, resp, image_id):
    #     """Deletes an image by ID."""
    #     image_meta = images_db.pop(image_id, None)
    #
    #     if image_meta is None:
    #         raise falcon.HTTPNotFound()
    #
    #     self.image_ops.delete_image_from_disk(image_meta['filename'])
    #
    #     resp.media = {'message': 'Image deleted successfully'}
    #     resp.status = falcon.HTTP_200

