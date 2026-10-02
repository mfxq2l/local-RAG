"""多模态能力：图片理解与视觉描述。

模块结构：

    captioner.VisionCaptioner   用「主模型 + mmproj」为图片生成语义描述
    captioner.prepare_data_url  图片预处理（缩放 + base64）

背景：llama.cpp 的 ``/v1/embeddings`` 不接受图片输入，因此图片必须先由
视觉模型转成文本描述，才能进入向量库参与检索。
"""

from src.vision.captioner import VisionCaptioner, prepare_data_url

__all__ = ["VisionCaptioner", "prepare_data_url"]
