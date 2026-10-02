"""多模态相关测试：图片预处理、图片 chunk、视觉描述器状态。"""

from __future__ import annotations

import base64
import io
import shutil
import tempfile
import unittest
from pathlib import Path

from src.ingest.image import (
    collect_image_chunks,
    describe_image_basic,
    image_to_chunk,
    iter_image_files,
)
from src.vision import VisionCaptioner, prepare_data_url


def make_image(path: Path, size=(200, 120), color=(20, 30, 50)) -> Path:
    from PIL import Image

    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, color).save(path)
    return path


class TestPrepareDataUrl(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="rag_vision_test_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_produces_png_data_url(self) -> None:
        path = make_image(self.tmp / "a.png")
        url = prepare_data_url(path)

        self.assertTrue(url.startswith("data:image/png;base64,"))
        base64.b64decode(url.split("base64,", 1)[1])

    def test_accepts_raw_bytes(self) -> None:
        path = make_image(self.tmp / "b.png")
        url = prepare_data_url(path.read_bytes())
        self.assertTrue(url.startswith("data:image/png;base64,"))

    def test_downscales_large_image(self) -> None:
        """大图必须被缩放，否则会产生海量 image token。"""
        from PIL import Image

        path = make_image(self.tmp / "big.png", size=(3000, 1500))
        url = prepare_data_url(path, max_edge=1024)

        raw = base64.b64decode(url.split("base64,", 1)[1])
        with Image.open(io.BytesIO(raw)) as img:
            self.assertLessEqual(max(img.size), 1024)
            # 保持宽高比
            self.assertAlmostEqual(img.size[0] / img.size[1], 2.0, places=1)

    def test_small_image_not_upscaled(self) -> None:
        from PIL import Image

        path = make_image(self.tmp / "small.png", size=(64, 48))
        url = prepare_data_url(path)
        raw = base64.b64decode(url.split("base64,", 1)[1])

        with Image.open(io.BytesIO(raw)) as img:
            self.assertEqual(img.size, (64, 48))

    def test_jpeg_converted(self) -> None:
        from PIL import Image

        path = self.tmp / "c.jpg"
        Image.new("RGB", (80, 60), (200, 10, 10)).save(path, format="JPEG")

        url = prepare_data_url(path)
        self.assertTrue(url.startswith("data:image/png;base64,"))

    def test_invalid_file_raises(self) -> None:
        path = self.tmp / "bad.png"
        path.write_bytes(b"not an image")

        with self.assertRaises(ValueError):
            prepare_data_url(path)


class TestIterImageFiles(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="rag_vision_test_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_finds_supported_formats(self) -> None:
        for name in ("a.png", "b.jpg", "c.jpeg", "d.webp", "e.bmp"):
            make_image(self.tmp / name)
        (self.tmp / "note.txt").write_text("x", encoding="utf-8")

        found = {p.name for p in iter_image_files(self.tmp)}

        self.assertEqual(
            found, {"a.png", "b.jpg", "c.jpeg", "d.webp", "e.bmp"}
        )

    def test_recursive(self) -> None:
        make_image(self.tmp / "sub" / "deep.png")
        self.assertEqual(len(list(iter_image_files(self.tmp))), 1)

    def test_missing_directory(self) -> None:
        self.assertEqual(list(iter_image_files(self.tmp / "nope")), [])


class TestImageChunk(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="rag_vision_test_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_metadata_marks_modality(self) -> None:
        path = make_image(self.tmp / "pic.png")
        chunk = image_to_chunk(path, description="一张测试图", relative_to=self.tmp)

        self.assertEqual(chunk.metadata["modality"], "image")
        self.assertEqual(chunk.metadata["image_path"], "pic.png")
        self.assertEqual(chunk.metadata["caption_source"], "vlm")
        self.assertEqual(chunk.metadata["width"], 200)
        self.assertEqual(chunk.metadata["height"], 120)

    def test_content_includes_file_name_and_caption(self) -> None:
        path = make_image(self.tmp / "pic.png")
        chunk = image_to_chunk(path, description="描述内容", relative_to=self.tmp)

        self.assertIn("pic.png", chunk.content)
        self.assertIn("描述内容", chunk.content)

    def test_fallback_description_flagged(self) -> None:
        path = make_image(self.tmp / "pic.png")
        chunk = image_to_chunk(path, description=None, relative_to=self.tmp)

        self.assertEqual(chunk.metadata["caption_source"], "metadata")
        self.assertIn("尺寸", chunk.content)

    def test_nested_relative_path(self) -> None:
        path = make_image(self.tmp / "sub" / "dir" / "pic.png")
        chunk = image_to_chunk(path, description="x", relative_to=self.tmp)
        self.assertEqual(chunk.metadata["image_path"], "sub/dir/pic.png")

    def test_doc_id_is_prefixed(self) -> None:
        path = make_image(self.tmp / "pic.png")
        chunk = image_to_chunk(path, description="x", relative_to=self.tmp)
        self.assertTrue(chunk.doc_id.startswith("image::"))

    def test_chunk_id_is_stable(self) -> None:
        path = make_image(self.tmp / "pic.png")
        a = image_to_chunk(path, description="x", relative_to=self.tmp)
        b = image_to_chunk(path, description="y", relative_to=self.tmp)
        self.assertEqual(a.chunk_id, b.chunk_id)

    def test_basic_description_reports_dimensions(self) -> None:
        path = make_image(self.tmp / "pic.png", size=(321, 123))
        text = describe_image_basic(path)
        self.assertIn("321x123", text)

    def test_chunk_id_carries_image_marker(self) -> None:
        """摄取管线靠这个标记识别图片 chunk，避免 include_images=false 时误删。"""
        from src.ingest.image import IMAGE_CHUNK_MARKER

        path = make_image(self.tmp / "pic.png")
        chunk = image_to_chunk(path, description="x", relative_to=self.tmp)

        self.assertIn(IMAGE_CHUNK_MARKER, chunk.chunk_id)

    def test_all_image_chunks_carry_marker(self) -> None:
        from src.ingest.image import IMAGE_CHUNK_MARKER

        for name in ("a.png", "b.jpg", "c.webp"):
            make_image(self.tmp / name)

        chunks = collect_image_chunks(self.tmp, describe=False)

        self.assertTrue(chunks)
        for chunk in chunks:
            self.assertIn(IMAGE_CHUNK_MARKER, chunk.chunk_id)


class TestCollectImageChunks(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="rag_vision_test_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_without_captioner_uses_fallback(self) -> None:
        make_image(self.tmp / "a.png")
        make_image(self.tmp / "b.png")

        chunks = collect_image_chunks(self.tmp, describe=False)

        self.assertEqual(len(chunks), 2)
        for chunk in chunks:
            self.assertEqual(chunk.metadata["caption_source"], "metadata")

    def test_empty_directory(self) -> None:
        self.assertEqual(collect_image_chunks(self.tmp), [])

    def test_missing_directory(self) -> None:
        self.assertEqual(collect_image_chunks(self.tmp / "nope"), [])

    def test_uses_provided_captioner(self) -> None:
        make_image(self.tmp / "a.png")

        class FakeCaptioner:
            model_path = Path("fake.gguf")

            def available(self):
                return True, "ok"

            def caption_many(self, files, on_progress=None):
                return ["视觉模型生成的描述" for _ in files]

        chunks = collect_image_chunks(
            self.tmp, captioner=FakeCaptioner(), describe=True
        )

        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].metadata["caption_source"], "vlm")
        self.assertIn("视觉模型生成的描述", chunks[0].content)


class TestVisionCaptionerStatus(unittest.TestCase):
    def test_disabled_reports_reason(self) -> None:
        from src.config import VisionConfig

        captioner = VisionCaptioner(VisionConfig(enabled=False))
        ok, reason = captioner.available()

        self.assertFalse(ok)
        self.assertIn("禁用", reason)

    def test_status_shape(self) -> None:
        status = VisionCaptioner().status()

        for key in (
            "available", "reason", "model", "mmproj", "port", "started",
        ):
            self.assertIn(key, status)

    def test_missing_mmproj_is_reported(self) -> None:
        from src.config import VisionConfig

        captioner = VisionCaptioner(
            VisionConfig(
                model_path=Path("C:/nope/model.gguf"),
                mmproj_path=None,
            )
        )
        # 无 mmproj 时不能声称可用（图片理解必须有投影器）
        ok, reason = captioner.available()
        self.assertFalse(ok)
        self.assertTrue(reason)


if __name__ == "__main__":
    unittest.main()
