# app.py

import cv2
import layoutparser as lp

def main():

    image = cv2.imread("example_table.jpg")
    image = image[..., ::-1]

    model = lp.Detectron2LayoutModel(
        'lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config',
        extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.65],
        label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"}
    )

    layout = model.detect(image)
    lp.draw_box(image, layout,)


if __name__=="__main__":
    main()