import multiprocessing
import layoutparser as lp

class AIModelHandler:
    def __init__(self):
        self.detectron2_model = lp.Detectron2LayoutModel(
            config_path='config.yaml',
            extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.65],
            label_map={
                0: "Text",
                1: "Title",
                2: "List",
                3: "Table",
                4: "Figure"
            }
        )
        self.tesseract_model = lp.TesseractAgent(languages='eng')

        self.detectron2_lock = multiprocessing.Lock()
        self.tesseract_lock = multiprocessing.Lock()

    def use_detectron2(self, image):
        with self.detectron2_lock:
            return self.detectron2_model.detect(image)

    def use_tesseract(self, image):
        with self.tesseract_lock:
            return self.tesseract_model.detect(image)