from src.brain.image_ops import ImageOps
from src.brain.model_manager import ModelManager
from src.brain.vector_store import AstraDBVectorStore
from src.utils.config_utils import load_config_object


class ArtifactManager():
    are_all_artifacts_loaded = False

    def __init__(self):

        self.config = load_config_object()
        self.image_vector_repository = AstraDBVectorStore(self.config.db_config_astra.endpoint_url,
                                                          self.config.db_config_astra.token,
                                                          self.config.db_config_astra.image_collection_name)
        self.model_manager = ModelManager()
        self.image_ops = ImageOps()

        ArtifactManager.are_all_artifacts_loaded = True
