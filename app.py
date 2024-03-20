# app.py

import cv2
import layoutparser as lp
import numpy as np

def main():

    image = cv2.imread("example_table.jpg")
    image = image[..., ::-1]

    model = lp.Detectron2LayoutModel(
        'lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config',
        extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.65],
        label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"}
    )

    layout = model.detect(image)

    lp.draw_box(image, layout, box_width=3)

    tables = []
    figures = []

    for element in layout:
        if element.type == "Table":
            tables.append(element)
        if element.type == "Figure":
            figures.append(element)

    layout_tables = lp.Layout(tables)
    layout_figures = lp.Layout(figures)

    not_overlapped_tables = []

    for table in layout_tables:
        is_overlapping = False

        for figure in layout_figures:
            if table.is_in(figure):
                is_overlapping = True
                break

        if not is_overlapping:
            not_overlapped_tables.append(table)

    not_overlapped_tables = lp.Layout(not_overlapped_tables)

    # height, width = image.shape[:2]
    # left_interval = lp.Interval(0, width / 2 * 1.05, axis='x').put_on_canvas(image)
    # left_blocks = text_blocks.filter_by(left_interval, center=True)
    # left_blocks.sort(key=lambda element: element.coordinates[1])
    #
    # right_blocks = [element for element in text_blocks if element not in left_blocks]
    # right_blocks.sort(key=lambda element: element.coordinates[1])
    #
    # text_blocks = lp.Layout([element.set(id=idx) for idx, element in enumerate(left_blocks + right_blocks)])

    image_with_boxes = lp.draw_box(image, not_overlapped_tables, box_width=3, show_element_id=True)
    image_with_boxes_np = np.array(image_with_boxes)
    image_with_boxes_np = cv2.cvtColor(image_with_boxes_np, cv2.COLOR_RGB2BGR)
    cv2.imwrite('processed_image.jpg', image_with_boxes_np)

    ocr_agent = lp.TesseractAgent(languages='eng')

    for table in not_overlapped_tables:
        segment_image = (
            table
            # .pad(left=5, right=5, top=5, bottom=5)
            .crop_image(image)
        )

        text = ocr_agent.detect(segment_image)
        table.set(text=text, inplace=True)

    for text in not_overlapped_tables.get_texts():
        print(text, end='\n---\n')


if __name__=="__main__":
    main()