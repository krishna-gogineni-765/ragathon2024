import json

import falcon
from src.utils.artifact_manager import ArtifactManager


class HealthResource(object):
    def on_get(self, req, resp):
        if ArtifactManager.are_all_artifacts_loaded:
            doc = {"status": "up"}
            resp.text = json.dumps(doc, ensure_ascii=False)
            resp.status = falcon.HTTP_200
            return resp
        else:
            doc = {"status": "down"}
            resp.text = json.dumps(doc, ensure_ascii=False)
            resp.status = falcon.HTTP_503
            return resp
