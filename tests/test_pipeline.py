import sys
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch
import types

import cv2
import numpy as np
from PIL import Image

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
TESTS_DIR = Path(__file__).resolve().parent

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))


class _QtObject:
    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        def _noop(*args, **kwargs):
            return None

        return _noop


def _install_test_stubs():
    qt_module = types.ModuleType("PyQt5")
    qt_widgets = types.ModuleType("PyQt5.QtWidgets")
    qt_gui = types.ModuleType("PyQt5.QtGui")
    qt_core = types.ModuleType("PyQt5.QtCore")

    for module in (qt_widgets, qt_gui, qt_core):
        module.QApplication = _QtObject
        module.QMainWindow = _QtObject
        module.QWidget = _QtObject
        module.QVBoxLayout = _QtObject
        module.QHBoxLayout = _QtObject
        module.QPushButton = _QtObject
        module.QLabel = _QtObject
        module.QTextEdit = _QtObject
        module.QFileDialog = _QtObject
        module.QMessageBox = _QtObject
        module.QSplitter = _QtObject
        module.QSlider = _QtObject
        module.QFrame = _QtObject
        module.QGroupBox = _QtObject
        module.QCheckBox = _QtObject
        module.QComboBox = _QtObject
        module.QTabWidget = _QtObject
        module.QTabBar = _QtObject
        module.QDialog = _QtObject
        module.QStyle = _QtObject
        module.QToolBar = _QtObject
        module.QAction = _QtObject
        module.QPixmap = _QtObject
        module.QImage = _QtObject
        module.QIcon = _QtObject
        module.QFont = _QtObject
        module.QPalette = _QtObject
        module.QColor = _QtObject

    qt_core.Qt = types.SimpleNamespace(
        Horizontal=1,
        Vertical=2,
        AlignCenter=4,
        KeepAspectRatio=8,
        SmoothTransformation=16,
        RightSide=32,
    )
    qt_core.pyqtSlot = lambda *args, **kwargs: (lambda func: func)
    qt_core.QSize = lambda *args, **kwargs: None
    qt_core.QTimer = _QtObject

    pytesseract_stub = types.ModuleType("pytesseract")
    pytesseract_stub.pytesseract = types.SimpleNamespace(
        tesseract_cmd="",
        get_tesseract_version=lambda: "stub",
    )
    pytesseract_stub.Output = types.SimpleNamespace(DICT="DICT")
    pytesseract_stub.image_to_string = lambda *args, **kwargs: ""
    pytesseract_stub.image_to_data = lambda *args, **kwargs: {"text": [], "conf": []}
    pytesseract_stub.get_tesseract_version = lambda: "stub"

    sys.modules.setdefault("PyQt5", qt_module)
    sys.modules.setdefault("PyQt5.QtWidgets", qt_widgets)
    sys.modules.setdefault("PyQt5.QtGui", qt_gui)
    sys.modules.setdefault("PyQt5.QtCore", qt_core)
    sys.modules.setdefault("pytesseract", pytesseract_stub)


_install_test_stubs()

from main import OCRTextExtractor
from fixtures import FIXTURE_DIR, ensure_fixtures


class DummyCombo:
    def __init__(self, index):
        self._index = index

    def currentIndex(self):
        return self._index


class DummyTextEdit:
    def __init__(self):
        self.value = ""

    def setText(self, text):
        self.value = text

    def toPlainText(self):
        return self.value


class DummyButton:
    def __init__(self):
        self.enabled = None

    def setEnabled(self, value):
        self.enabled = value


class PipelineTests(TestCase):
    @classmethod
    def setUpClass(cls):
        ensure_fixtures()
        cls.low_contrast_path = FIXTURE_DIR / "low_contrast_scan.png"
        cls.two_column_path = FIXTURE_DIR / "two_columns.png"
        cls.single_block_path = FIXTURE_DIR / "single_block.png"
        cls.low_contrast = cv2.imread(str(cls.low_contrast_path))
        cls.two_columns = cv2.imread(str(cls.two_column_path))
        cls.single_block = cv2.imread(str(cls.single_block_path))

        if cls.low_contrast is None or cls.two_columns is None or cls.single_block is None:
            raise RuntimeError("Failed to load generated test fixtures")

    def _make_extractor(self):
        return OCRTextExtractor.__new__(OCRTextExtractor)

    def test_preprocess_improves_low_contrast_variance(self):
        extractor = self._make_extractor()
        original_gray = cv2.cvtColor(self.low_contrast, cv2.COLOR_BGR2GRAY)
        processed = extractor.preprocess_image(
            self.low_contrast,
            deskew=False,
            use_adaptive_threshold=True,
        )
        processed_gray = np.array(processed.convert("L"))

        self.assertGreater(processed_gray.std(), original_gray.std())

    def test_extract_layout_regions_detects_multiple_columns(self):
        extractor = self._make_extractor()
        regions = extractor.extract_layout_regions(self.two_columns)

        self.assertGreaterEqual(len(regions), 2)
        self.assertLess(regions[0][0], regions[-1][0])

    def test_process_ocr_reorders_regions_in_reading_order(self):
        extractor = self._make_extractor()
        text_edit = DummyTextEdit()
        tab_data = {
            "cv_image": self.single_block,
            "contrast_value": 1.0,
            "brightness_value": 1.0,
            "sharpness_value": 1.0,
            "deskew_check": False,
            "use_adaptive_threshold": False,
            "font_combo": DummyCombo(0),
            "psm_mode": 6,
            "oem_mode": 3,
            "text_edit": text_edit,
        }

        extractor.tabs = {0: tab_data}
        extractor.current_tab = 0
        extractor.save_btn = DummyButton()
        extractor.update_save_all_button = lambda: None

        region_outputs = ["LEFT BLOCK", "RIGHT BLOCK"]

        with patch.object(extractor, "preprocess_image", return_value=Image.new("RGB", (200, 100), "white")), \
             patch.object(extractor, "extract_layout_regions", return_value=[(0, 0, 50, 50), (60, 0, 50, 50)]), \
             patch.object(extractor, "deskew_region", side_effect=lambda image: image), \
             patch.object(extractor, "score_psm_candidate", side_effect=lambda image, psm, oem: (float(psm), 1)), \
             patch.object(extractor, "reconstruct_text_from_data", side_effect=lambda image, psm, oem: region_outputs.pop(0)):
            extractor.process_ocr(tab_data)

        self.assertEqual(text_edit.value, "LEFT BLOCK\n\nRIGHT BLOCK")
        self.assertTrue(extractor.save_btn.enabled)
