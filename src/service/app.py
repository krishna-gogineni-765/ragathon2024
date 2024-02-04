import falcon

from src.service.catalog_management import ImageLibraryResource

from src.service.health import HealthResource
from src.service.image_rag import ImageRagResource
from src.utils.artifact_manager import ArtifactManager

from falcon_multipart.middleware import MultipartMiddleware


def create_app():
    artifact_manager = ArtifactManager()

    # app_auth_id = artifact_manager.toolkit_config.get(Constants.APP_AUTH_ID, "")
    # app_auth_secret = artifact_manager.toolkit_config.get(Constants.APP_AUTH_SECRET, "")
    api = falcon.API(middleware=[MultipartMiddleware(), CORSMiddleware()])

    health_resource = HealthResource()
    api.add_route('/health', health_resource)

    image_resource = ImageLibraryResource(artifact_manager)
    api.add_route('/images', image_resource)
    api.add_route('/images/{image_id}', image_resource)

    image_rag_resource = ImageRagResource(artifact_manager)
    api.add_route('/image-rag', image_rag_resource)

    return api

class CORSMiddleware:
    def process_request(self, req, resp):
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.set_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        resp.set_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, user-id, account-id')
        resp.set_header('Access-Control-Allow-Credentials', 'true')

    def process_response(self, req, resp, resource, req_succeeded):
        if req.method == 'OPTIONS':
            resp.set_header('Access-Control-Allow-Origin', '*')
            resp.set_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            resp.set_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, user-id, account-id')
            resp.set_header('Access-Control-Max-Age', 1728000)  # 20 days
            resp.status = falcon.HTTP_200

if __name__ == "__main__":
    create_app()