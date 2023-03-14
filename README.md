# pascalvoc2ls

A Pascal VOC to Label Studio annotation converter.

## 安裝

```shell
# Prod
pip install -r requirements.txt

# Dev
pip install -r requirements-dev.txt
```

## 使用

直接執行 `convert.py` 就會直接開始轉換

```shell
python convert.py
```

| 參數名稱            | 型態 | 必填 | 預設值  | 說明                |
| ------------------- | ---- | ---- | ------- | ------------------- |
| `-fd`, `--file_dir` | str  | \*   |         | Pascal VOC xml 目錄 |
| `-sd`, `--save_dir` | str  |      | output/ | 輸出目錄            |
