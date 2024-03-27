import layoutparser as lp
from multiprocessing import Lock
from multiprocessing.managers import BaseManager

class Detectron2Wrapper:
    def __init__(self, config_path, extra_config, label_map):
        self.model = lp.Detectron2LayoutModel(config_path=config_path,
                                              extra_config=extra_config,
                                              label_map=label_map)
        self.lock = Lock()

    def process(self, image):
        with self.lock:
            return self.model.detect(image)

class TesseractWrapper:
    def __init__(self, languages):
        self.model = lp.TesseractAgent(languages=languages)
        self.lock = Lock()

    def process(self, image):
        with self.lock:
            return self.model.detect(image)

class ModelManager(BaseManager):
    pass

def manager_server():
    m = ModelManager()
    m.start()
    return m

# Definizione delle classi manager per i modelli
ModelManager.register('Detectron2Wrapper', Detectron2Wrapper)
ModelManager.register('TesseractWrapper', TesseractWrapper)