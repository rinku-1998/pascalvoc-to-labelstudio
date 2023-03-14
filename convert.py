import xmltodict
from loguru import logger
from pathlib import Path
from typing import List, Optional, Tuple
from util.json_tool import JSONTool
from util.object_tool import ObjectTool


def gen_annotation(
        fname: str, img_size: Tuple[int, int],
        boxes: List[Tuple[float, float, float, float, str]]) -> dict:
    """產生新的標記資料

    Args:
        fname (str): 檔案名稱
        img_size (Tuple[int, int]): 圖片尺寸
        boxes (List[Tuple[float, float, float, float, str]]): 標記框資料列表

    Returns:
        dict: 新標記檔字典
    """

    # 1. 標記框資料
    results: List[dict] = list()
    for i, box in enumerate(boxes):

        # 解包
        img_height, img_width = img_size
        x, y, box_height, box_width, label = box

        # 整理資料
        r = {
            'original_width': img_width,
            'original_height': img_height,
            'image_rotation': 0,
            'value': {
                'x': x,
                'y': y,
                'width': box_width,
                'height': box_height,
                'rotation': 0,
                'rectanglelabels': [label]
            },
            'id': f'box_{i+1}',
            'from_name': 'label',
            'to_name': 'image',
            'type': 'rectanglelabels',
            'origin': 'manual'
        }
        results.append(r)

    annotation = {'result': results}
    annotations = list()
    annotations.append(annotation)

    # 2. Data(影像資料)
    data = {'image': fname}

    # 3. 整理資料(最上層)
    root = {'predictions': list(), 'data': data, 'annotations': annotations}

    return root


def extract(
    xml_dict: dict
) -> Tuple[Optional[str], Optional[Tuple[int, int]], List[Tuple[
        float, float, float, float, str]]]:
    '''擷取標記檔資料

    Args:
        xml_dict (dict): Pascal VOC 標記檔字典

    Returns:
        Tuple[Optional[str], Optional[Tuple[int, int]], List[Tuple[float, float, float, float, str]]]: 檔案名稱、圖片尺寸、標記框資料列表
    '''

    # 1. 取得最上層的資料
    annotation = xml_dict.get('annotation')

    # 2. 檔名
    fname = annotation.get('filename')

    # 3. 圖片尺寸
    size = annotation.get('size')
    if not size:
        return fname, None, None
    img_height = int(size.get('height'))
    img_width = int(size.get('width'))

    # 4. 標記框
    objs = annotation.get('object')
    if not objs:
        return fname, (img_height, img_width), None
    if not isinstance(objs, list):
        objs = [objs]

    boxes: List[Tuple[float, float, float, float, str]] = list()
    for obj in objs:

        # 標記名稱
        label = obj.get('name')

        # 標記框座標
        bnd_box = obj.get('bndbox')
        x_min = int(bnd_box.get('xmin'))
        y_min = int(bnd_box.get('ymin'))
        x_max = int(bnd_box.get('xmax'))
        y_max = int(bnd_box.get('ymax'))

        # 計算新格式尺寸(百分比)
        x = x_min / img_width * 100
        y = y_min / img_height * 100
        box_width = (x_max - x_min) / img_width * 100
        box_height = (y_max - y_min) / img_height * 100

        # 整理資料
        box = (x, y, box_height, box_width, label)
        boxes.append(box)

    return fname, (img_height, img_width), boxes


def convert(f_dir: str, save_dir: str):

    logger.info('轉換作業開始')

    # 1. 遍歷資料夾下的檔案
    fps = list(Path(f_dir).rglob('*.xml'))
    logger.info(f'已搜尋到 {len(fps)} 個檔案')

    success_count = 0
    for fp in fps:

        # 讀取檔案
        xml_str = None
        with open(fp, 'r', encoding='utf-8') as f:
            xml_str = f.read()

        if not xml_str:
            continue

        # 轉為字典
        xml_dict = xmltodict.parse(xml_str)

        # 擷取資料
        fname, img_size, boxes = extract(xml_dict)
        if ObjectTool.any_none(fname, img_size, boxes):
            continue

        # 產生新的標記資料
        annotation_dict = gen_annotation(fname, img_size, boxes)

        # 存檔
        save_fn = f'{fp.stem}.json'
        save_p = Path(save_dir, save_fn)
        JSONTool.save_json(annotation_dict, save_p)
        success_count += 1

    logger.success(f'轉換作業成功，已處理 {success_count} 個檔案')


if __name__ == '__main__':

    # 1. 設定參數
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-fd',
                        '--file_dir',
                        type=str,
                        required=True,
                        help='Directory to annotation xmls')
    parser.add_argument('-sd',
                        '--save_dir',
                        type=str,
                        default='output/',
                        help='Directory to output jsons.')

    args = parser.parse_args()

    # 2. 設定日誌
    log_fp = Path(r'log/', 'success.log')
    logger.add(log_fp)

    # 3. 執行
    convert(args.file_dir, args.save_dir)