import json
import os
from pathlib import Path
from typing import Dict, List, Union


class SmartJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if hasattr(obj, '__jsonencode__'):
            return obj.__jsonencode__()

        if hasattr(obj, '__dict__'):
            return obj.__dict__

        if isinstance(obj, set):
            return list(obj)

        return json.JSONEncoder.default(self, obj)


class JSONTool:

    @staticmethod
    def save_json(data: Union[List, Dict], save_path: Union[str,
                                                            Path]) -> None:

        # 1. 檢查上層資料夾是否存在，若不存在就新建一個
        if not Path(save_path).parent.exists():
            os.makedirs(save_path.parent)

        # 2. 寫入檔案
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(data,
                      f,
                      ensure_ascii=False,
                      cls=SmartJSONEncoder,
                      sort_keys=True,
                      indent=4)
