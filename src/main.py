import sys
import os
import cv2
import numpy as np
import pytesseract
import traceback
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                            QFileDialog, QMessageBox, QSplitter, QSlider,
                            QFrame, QGroupBox, QCheckBox, QComboBox, 
                            QTabWidget, QTabBar, QDialog, QStyle)
from PyQt5.QtGui import QPixmap, QImage, QIcon, QFont, QPalette, QColor
from PyQt5.QtCore import Qt, pyqtSlot, QSize
import time
from PyQt5.QtCore import QTimer

# Try to set the path to the Tesseract executable
tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
if os.path.exists(tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
else:
    # Look for Tesseract in common locations
    common_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        r'C:\Tesseract-OCR\tesseract.exe'
    ]
    
    found = False
    for path in common_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            found = True
            break
    
    if not found:
        print("Warning: Tesseract OCR not found. Please install it and set the correct path.")

class ModernStyle:
    """Class to define modern styling for the application"""
    PRIMARY_COLOR = "#3f51b5"  # Indigo
    SECONDARY_COLOR = "#757de8"  # Lighter indigo
    BACKGROUND_COLOR = "#f5f5f5"
    CARD_COLOR = "#ffffff"
    TEXT_COLOR = "#212121"
    ACCENT_COLOR = "#ff4081"  # Pink accent
    LIGHT_TEXT_COLOR = "#757575"  # Gray
    HOVER_COLOR = "#E3F2FD"  # Material Blue 50
    
    BUTTON_STYLE = f"""
        QPushButton {{
            background-color: {PRIMARY_COLOR};
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background-color: {SECONDARY_COLOR};
        }}
        QPushButton:pressed {{
            background-color: #0D47A1;
        }}
        QPushButton:disabled {{
            background-color: #BDBDBD;
            color: #757575;
        }}
    """
    
    HELP_BUTTON_STYLE = f"""
        QPushButton {{
            background-color: {PRIMARY_COLOR};
            color: white;
            border: none;
            border-radius: 4px;
            padding: 2px;
            font-size: 14px;
            font-weight: bold;
            min-width: 24px;
            max-width: 24px;
            min-height: 24px;
            max-height: 24px;
        }}
        QPushButton:hover {{
            background-color: {SECONDARY_COLOR};
        }}
        QPushButton:pressed {{
            background-color: #0D47A1;
        }}
    """
    
    SLIDER_STYLE = f"""
        QSlider::groove:horizontal {{
            border: none;
            height: 4px;
            background: #e0e0e0;
            margin: 2px 0;
            border-radius: 2px;
        }}
        QSlider::handle:horizontal {{
            background: {PRIMARY_COLOR};
            border: none;
            width: 18px;
            height: 18px;
            margin: -7px 0;
            border-radius: 9px;
        }}
        QSlider::handle:horizontal:hover {{
            background: {SECONDARY_COLOR};
        }}
        QSlider::sub-page:horizontal {{
            background: {PRIMARY_COLOR};
            border-radius: 2px;
        }}
    """
    
    TEXTEDIT_STYLE = """
        QTextEdit {
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            padding: 8px;
            background-color: white;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
    """
    
    COMBOBOX_STYLE = f"""
        QComboBox {{
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            padding: 4px 8px;
            background-color: white;
            color: {TEXT_COLOR};
            min-height: 24px;
        }}
        QComboBox:hover {{
            border: 1px solid {PRIMARY_COLOR};
        }}
        QComboBox:focus {{
            border: 1px solid {PRIMARY_COLOR};
        }}
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 24px;
            border-left: 1px solid #e0e0e0;
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
        }}
        QComboBox::down-arrow {{
            image: url(:/icons/dropdown.png);
            width: 16px;
            height: 16px;
        }}
        QComboBox QAbstractItemView {{
            border: 1px solid #e0e0e0;
            selection-background-color: {HOVER_COLOR};
            selection-color: {TEXT_COLOR};
            background-color: white;
            color: {TEXT_COLOR};
        }}
    """
    
    CHECKBOX_STYLE = f"""
        QCheckBox {{
            spacing: 5px;
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
        }}
        QCheckBox::indicator:unchecked {{
            border: 2px solid #e0e0e0;
            background-color: white;
            border-radius: 3px;
        }}
        QCheckBox::indicator:checked {{
            border: 2px solid {PRIMARY_COLOR};
            background-color: {PRIMARY_COLOR};
            border-radius: 3px;
        }}
    """
    
    GROUPBOX_STYLE = """
        QGroupBox {
            font-weight: bold;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            margin-top: 16px;
            padding-top: 16px;
            background-color: white;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 8px;
            padding: 0 5px;
            background-color: white;
        }
    """
    
    FRAME_STYLE = """
        QFrame {
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background-color: white;
        }
    """
    
    MAIN_STYLE = f"""
        QMainWindow, QDialog {{
            background-color: {BACKGROUND_COLOR}; 
            color: {TEXT_COLOR};
        }}
        QLabel {{
            color: {TEXT_COLOR};
            font-family: 'Segoe UI', Arial, sans-serif;
        }}
        QSplitter::handle {{
            background-color: #e0e0e0;
        }}
        QMenuBar {{
            background-color: {BACKGROUND_COLOR};
            color: {TEXT_COLOR};
            border-bottom: 1px solid #e0e0e0;
        }}
        QMenuBar::item {{
            background-color: transparent;
            padding: 8px 12px;
        }}
        QMenuBar::item:selected {{
            background-color: {HOVER_COLOR};
        }}
        QMenu {{
            background-color: {BACKGROUND_COLOR};
            color: {TEXT_COLOR};
            border: 1px solid #e0e0e0;
        }}
        QMenu::item {{
            padding: 6px 24px 6px 12px;
        }}
        QMenu::item:selected {{
            background-color: {HOVER_COLOR};
        }}
    """
    
    TAB_STYLE = """
        QTabWidget::pane {
            border: 1px solid #e0e0e0;
            background: white;
            border-radius: 4px;
        }
        QTabBar::tab {
            background: #f5f5f5;
            color: #424242;
            padding: 8px 12px;
            border: 1px solid #e0e0e0;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background: white;
            border-bottom-color: white;
        }
        QTabBar::tab:hover:!selected {
            background: #eeeeee;
        }
        QTabBar::close-button {
            image: none;
            background-color: transparent;
            color: #757575;
            border: none;
            padding: 4px;
            margin-right: 2px;
            margin-left: 4px;
            border-radius: 2px;
        }
        QTabBar::close-button:hover {
            background-color: #ffcdd2;
        }
    """

class OCRTextExtractor(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize variables
        self.tabs = {}  # Dictionary to store tab data
        self.current_tab = 0
        self.next_tab_id = 0
        
        # Initialize UI
        self.initUI()
        
        # Check if Tesseract is installed
        self.check_tesseract()
        
    def close_tab(self, index):
        """Close a tab and remove its data"""
        if len(self.tabs) <= 1:
            # Don't close the last tab
            return
            
        # Check if the index is valid and not the plus tab
        if index < 0 or index >= self.tab_widget.count() - 1:  # Skip the plus tab
            return
            
        # Get the tab key to remove
        tab_keys = list(self.tabs.keys())
        if index >= len(tab_keys):
            # Index out of range for the tabs dictionary
            return
            
        tab_idx = tab_keys[index]
        
        # Remove the tab
        self.tab_widget.removeTab(index)
        del self.tabs[tab_idx]
        
        # Update current tab index
        self.current_tab = self.tab_widget.currentIndex()
        
        # Update UI for the current tab
        self.update_ui_from_tab()
            
    def tab_changed(self, index):
        """Handle tab change event"""
        # Check if the index is valid
        if index < 0 or index >= self.tab_widget.count():
            return
            
        # Check if the tab is the plus tab (last tab)
        if index == self.tab_widget.count() - 1:
            # If it's the plus tab, don't update the current tab
            return
            
        # Update current tab index
        self.current_tab = index
        
        # Update UI based on current tab
        self.update_ui_from_tab()
            
    def update_ui_from_tab(self):
        """Update UI elements based on current tab"""
        # Check if there are any tabs
        if not self.tabs:
            return
            
        # Check if current_tab is valid
        if self.current_tab < 0 or self.current_tab >= self.tab_widget.count():
            return
            
        # Check if the current tab is the plus tab (last tab)
        if self.current_tab == self.tab_widget.count() - 1:
            return
            
        # Get the tab data for the current tab
        tab_keys = list(self.tabs.keys())
        if self.current_tab >= len(tab_keys):
            return
            
        tab_idx = tab_keys[self.current_tab]
        tab_data = self.tabs[tab_idx]
        
        # Update button states
        has_image = tab_data['cv_image'] is not None
        self.process_btn.setEnabled(has_image)
        
        has_text = bool(tab_data['text_edit'].toPlainText().strip())
        self.save_btn.setEnabled(has_text)
        
        # Update save all button
        self.update_save_all_button()
        
    def update_save_all_button(self):
        """Update the state of the save all button"""
        # Enable save all button if any tab has text
        has_any_text = False
        for tab_data in self.tabs.values():
            if tab_data['text_edit'].toPlainText().strip():
                has_any_text = True
                break
                
        self.save_all_btn.setEnabled(has_any_text)
        
    def load_image(self):
        """Load an image from file"""
        # Get current tab index
        tab_idx = list(self.tabs.keys())[self.current_tab]
        tab_data = self.tabs[tab_idx]
        
        # Open file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Open Image", 
            "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)"
        )
        
        if file_path:
            try:
                # Load image
                cv_image = cv2.imread(file_path)
                if cv_image is None:
                    raise Exception("Failed to load image")
                    
                # Store image in tab data
                tab_data['cv_image'] = cv_image
                
                # Display image
                self.display_image(tab_data)
                
                # Enable process button
                self.process_btn.setEnabled(True)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
                
    def capture_screenshot(self):
        """Capture a screenshot and load it into the current tab"""
        # Minimize the window to avoid capturing it
        self.showMinimized()
        
        # Wait a moment for the window to minimize
        QTimer.singleShot(500, self._take_screenshot)
        
    def _take_screenshot(self):
        """Take the actual screenshot after minimizing the window"""
        try:
            # Capture the full screen
            screen = QApplication.primaryScreen()
            screenshot = screen.grabWindow(0)
            
            # Convert QPixmap to QImage
            image = screenshot.toImage()
            
            # Convert QImage to numpy array
            width, height = image.width(), image.height()
            ptr = image.constBits()
            ptr.setsize(image.byteCount())
            arr = np.array(ptr).reshape(height, width, 4)  # RGBA
            
            # Convert RGBA to BGR (OpenCV format)
            cv_image = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
            
            # Get current tab data
            tab_idx = list(self.tabs.keys())[self.current_tab]
            tab_data = self.tabs[tab_idx]
            
            # Store the image
            tab_data['cv_image'] = cv_image
            
            # Display the image
            self.display_image(tab_data)
            
            # Enable process button
            self.process_btn.setEnabled(True)
            
            # Restore and maximize the window
            self.showNormal()
            self.showMaximized()
            self.activateWindow()  # Ensure window gets focus
            self.raise_()  # Bring window to front
            
        except Exception as e:
            self.showNormal()  # Make sure window is restored even if there's an error
            self.activateWindow()  # Ensure window gets focus even after error
            QMessageBox.critical(self, "Error", f"Failed to capture screenshot: {str(e)}")
            
    def display_image(self, tab_data=None):
        """Display the image in the current tab"""
        if isinstance(tab_data, np.ndarray):
            # If tab_data is actually a cv_image
            cv_image = tab_data
            
            # Get current tab data
            tab_idx = list(self.tabs.keys())[self.current_tab]
            tab_data = self.tabs[tab_idx]
            
            # Store the image
            tab_data['cv_image'] = cv_image
        
        if tab_data is None:
            # Get current tab data
            tab_idx = list(self.tabs.keys())[self.current_tab]
            tab_data = self.tabs[tab_idx]
            
        if tab_data['cv_image'] is None:
            return
            
        # Convert OpenCV image to QPixmap
        height, width, channel = tab_data['cv_image'].shape
        bytes_per_line = 3 * width
        q_image = QImage(tab_data['cv_image'].data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(q_image)
        
        # Scale pixmap to fit in the label while maintaining aspect ratio
        label_size = tab_data['image_label'].size()
        scaled_pixmap = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        tab_data['image_label'].setPixmap(scaled_pixmap)
        
    def preprocess_image(self, image):
        """Simple image preprocessing to improve OCR results"""
        if image is None:
            return None
            
        # Convert to PIL image for better processing
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        # Convert to grayscale
        gray_image = ImageOps.grayscale(pil_image)
        
        # Increase contrast
        contrast_image = ImageEnhance.Contrast(gray_image).enhance(2.0)
        
        # Increase sharpness
        sharp_image = ImageEnhance.Sharpness(contrast_image).enhance(2.0)
        
        # Apply a slight blur to reduce noise
        blurred_image = sharp_image.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        return blurred_image
        
    def process_ocr(self, tab_data=None):
        """Process OCR on the current image"""
        if tab_data is None:
            # Get current tab data
            tab_idx = list(self.tabs.keys())[self.current_tab]
            tab_data = self.tabs[tab_idx]
            
        # Ensure tab_data is a dictionary before proceeding
        if not isinstance(tab_data, dict):
            QMessageBox.warning(self, "Warning", "Invalid tab data")
            return
            
        if tab_data['cv_image'] is None:
            QMessageBox.warning(self, "Warning", "No image loaded")
            return
            
        try:
            # Preprocess the image
            preprocessed_image = self.preprocess_image(tab_data['cv_image'])
            
            # Get font type for specialized configurations
            font_index = tab_data['font_combo'].currentIndex()
            
            # Get PSM mode from the UI
            psm_mode = tab_data['psm_mode']
            
            # Try different configurations to get the best results
            text = ""
            
            # First try with the selected PSM mode and default OEM
            config = f'--psm {psm_mode} --oem 3'
            text = pytesseract.image_to_string(preprocessed_image, config=config)
            
            # If text is empty or very short, try with PSM mode 6 (single block of text)
            if not text.strip() or len(text.strip()) < 5:
                config = '--psm 6 --oem 3'
                text = pytesseract.image_to_string(preprocessed_image, config=config)
                
                # If still no good results, try with PSM mode 4 (single column of text)
                if not text.strip() or len(text.strip()) < 5:
                    config = '--psm 4 --oem 3'
                    text = pytesseract.image_to_string(preprocessed_image, config=config)
                    
                    # Last resort, try with PSM mode 3 (fully automatic page segmentation)
                    if not text.strip() or len(text.strip()) < 5:
                        config = '--psm 3 --oem 3'
                        text = pytesseract.image_to_string(preprocessed_image, config=config)
            
            # Store text in tab data
            tab_data['ocr_text'] = text
            
            # Display text
            tab_data['text_edit'].setText(text)
            
            # Enable save button
            self.save_btn.setEnabled(bool(text.strip()))
            
            # Update save all button
            self.update_save_all_button()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"OCR processing failed: {str(e)}")
            traceback.print_exc()  # Print the full traceback for debugging
            
    def save_current_text(self):
        """Save the current tab's text to a file"""
        # Get current tab data
        tab_idx = list(self.tabs.keys())[self.current_tab]
        tab_data = self.tabs[tab_idx]
        
        text = tab_data['text_edit'].toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Warning", "No text to save")
            return
            
        # Open file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Text", 
            f"ocr_text_{int(time.time())}.txt", 
            "Text Files (*.txt);;CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                QMessageBox.information(self, "Success", f"Text saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")
                
    def save_all_tabs(self):
        """Save all tabs' text to files"""
        # Get timestamp for filename
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        
        # Create a default filename
        default_filename = f"ocr_all_tabs_{timestamp}.txt"
        
        # Get save path
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save All Tabs",
            default_filename,
            "Text Files (*.txt);;All Files (*)"
        )
        
        if not save_path:
            return
            
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                for tab_idx, tab_data in self.tabs.items():
                    tab_name = self.tab_widget.tabText(list(self.tabs.keys()).index(tab_idx))
                    text = tab_data['text_edit'].toPlainText()
                    
                    if text.strip():
                        f.write(f"--- {tab_name} ---\n\n")
                        f.write(text)
                        f.write("\n\n")
                        
            QMessageBox.information(self, "Success", f"All tabs saved to {save_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")
                
    def check_tesseract(self):
        """Check if Tesseract is installed and configured"""
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False
        
    def initUI(self):
        self.setWindowTitle('OCR Text Extractor')
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(ModernStyle.MAIN_STYLE)
        
        # Set application icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons', 'camera_icon.svg')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Create main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.setStyleSheet(ModernStyle.TAB_STYLE)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.tab_changed)
        
        # Add tab widget to main layout
        main_layout.addWidget(self.tab_widget)
        
        # Create button layout
        button_layout = QHBoxLayout()
        
        # Create buttons
        self.load_btn = QPushButton("Load Image")
        self.load_btn.setStyleSheet(ModernStyle.BUTTON_STYLE)
        self.load_btn.setMinimumHeight(40)
        self.load_btn.clicked.connect(self.load_image)
        
        self.capture_btn = QPushButton("Capture Screenshot")
        self.capture_btn.setStyleSheet(ModernStyle.BUTTON_STYLE)
        self.capture_btn.setMinimumHeight(40)
        self.capture_btn.clicked.connect(self.capture_screenshot)
        
        self.process_btn = QPushButton("Process OCR")
        self.process_btn.setStyleSheet(ModernStyle.BUTTON_STYLE)
        self.process_btn.setMinimumHeight(40)
        self.process_btn.clicked.connect(lambda: self.process_ocr())
        self.process_btn.setEnabled(False)
        
        self.save_btn = QPushButton("Save Current Text")
        self.save_btn.setStyleSheet(ModernStyle.BUTTON_STYLE)
        self.save_btn.setMinimumHeight(40)
        self.save_btn.clicked.connect(self.save_current_text)
        self.save_btn.setEnabled(False)
        
        self.save_all_btn = QPushButton("Save All Tabs")
        self.save_all_btn.setStyleSheet(ModernStyle.BUTTON_STYLE)
        self.save_all_btn.setMinimumHeight(40)
        self.save_all_btn.clicked.connect(self.save_all_tabs)
        self.save_all_btn.setEnabled(False)
        
        # Add buttons to button layout
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.capture_btn)
        button_layout.addWidget(self.process_btn)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.save_all_btn)
        
        # Add button layout to main layout
        main_layout.addLayout(button_layout)
        
        # Set main layout to main widget
        main_widget.setLayout(main_layout)
        
        # Set main widget as central widget
        self.setCentralWidget(main_widget)
        
        # Add first tab
        self.add_new_tab()
        
        # Add the plus tab for adding new tabs
        self.add_plus_tab()
        
        # Show the window maximized by default
        self.showMaximized()
        
    def add_plus_tab(self):
        """Add a plus tab at the end for adding new tabs"""
        # Add a tab with just a plus sign as the text
        plus_tab_index = self.tab_widget.addTab(QWidget(), "+")
        
        # Get the tab bar
        tab_bar = self.tab_widget.tabBar()
        
        # Make the plus tab not closable by hiding its close button
        if tab_bar.tabButton(plus_tab_index, QTabBar.RightSide):
            tab_bar.tabButton(plus_tab_index, QTabBar.RightSide).hide()
        
        # Style the plus tab to look more like a button
        tab_bar.setTabTextColor(plus_tab_index, QColor("#2196F3"))  # Material blue
        
        # Connect the tab button clicked signal to add a new tab
        self.tab_widget.tabBarClicked.connect(self.handle_tab_click)
        
    def handle_tab_click(self, index):
        """Handle clicks on tabs, specifically the plus tab"""
        # Check if the clicked tab is the plus tab (last tab)
        if index == self.tab_widget.count() - 1:
            # Remove the plus tab
            self.tab_widget.removeTab(index)
            
            # Add a new content tab
            self.add_new_tab()
            
            # Add the plus tab back at the end
            self.add_plus_tab()
            
            # Select the newly added content tab
            self.tab_widget.setCurrentIndex(self.tab_widget.count() - 2)
            
    def add_new_tab(self):
        """Add a new tab with OCR content"""
        # Create a new tab content widget
        tab_content = QWidget()
        tab_layout = QVBoxLayout(tab_content)
        tab_layout.setContentsMargins(8, 8, 8, 8)
        
        # Create tab data dictionary to store tab-specific data
        tab_data = {
            'cv_image': None,
            'ocr_text': "",
            'contrast_value': 1.0,
            'brightness_value': 1.0,
            'sharpness_value': 1.0,
            'psm_mode': 3,  # Default PSM mode
            'oem_mode': 3   # Default to auto-select best engine
        }
        
        # Create horizontal splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel (image and controls)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Image frame
        image_frame = QFrame()
        image_frame.setFrameShape(QFrame.StyledPanel)
        image_frame.setStyleSheet(ModernStyle.FRAME_STYLE)
        image_frame.setMinimumHeight(300)
        image_layout = QVBoxLayout(image_frame)
        
        # Image label
        image_label = QLabel("No image loaded")
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setStyleSheet("background-color: #f0f0f0;")
        image_label.setMinimumSize(400, 300)
        image_layout.addWidget(image_label)
        tab_data['image_label'] = image_label
        
        # Add image frame to left layout
        left_layout.addWidget(image_frame, 3)
        
        # Controls frame
        controls_frame = QFrame()
        controls_frame.setFrameShape(QFrame.StyledPanel)
        controls_frame.setStyleSheet(ModernStyle.FRAME_STYLE)
        controls_layout = QVBoxLayout(controls_frame)
        
        # Image processing controls
        processing_group = QGroupBox("Image Processing")
        processing_group.setStyleSheet(ModernStyle.GROUPBOX_STYLE)
        processing_layout = QVBoxLayout(processing_group)
        
        # Contrast slider
        contrast_layout = QHBoxLayout()
        contrast_label = QLabel("Contrast:")
        contrast_slider = QSlider(Qt.Horizontal)
        contrast_slider.setRange(50, 150)
        contrast_slider.setValue(100)
        contrast_slider.setStyleSheet(ModernStyle.SLIDER_STYLE)
        contrast_value_label = QLabel("1.0")
        contrast_layout.addWidget(contrast_label)
        contrast_layout.addWidget(contrast_slider)
        contrast_layout.addWidget(contrast_value_label)
        processing_layout.addLayout(contrast_layout)
        
        # Brightness slider
        brightness_layout = QHBoxLayout()
        brightness_label = QLabel("Brightness:")
        brightness_slider = QSlider(Qt.Horizontal)
        brightness_slider.setRange(50, 150)
        brightness_slider.setValue(100)
        brightness_slider.setStyleSheet(ModernStyle.SLIDER_STYLE)
        brightness_value_label = QLabel("1.0")
        brightness_layout.addWidget(brightness_label)
        brightness_layout.addWidget(brightness_slider)
        brightness_layout.addWidget(brightness_value_label)
        processing_layout.addLayout(brightness_layout)
        
        # Sharpness slider
        sharpness_layout = QHBoxLayout()
        sharpness_label = QLabel("Sharpness:")
        sharpness_slider = QSlider(Qt.Horizontal)
        sharpness_slider.setRange(50, 150)
        sharpness_slider.setValue(100)
        sharpness_slider.setStyleSheet(ModernStyle.SLIDER_STYLE)
        sharpness_value_label = QLabel("1.0")
        sharpness_layout.addWidget(sharpness_label)
        sharpness_layout.addWidget(sharpness_slider)
        sharpness_layout.addWidget(sharpness_value_label)
        processing_layout.addLayout(sharpness_layout)
        
        # Deskew checkbox
        deskew_layout = QHBoxLayout()
        deskew_check = QCheckBox("Auto-deskew image")
        deskew_check.setChecked(True)
        deskew_check.setStyleSheet(ModernStyle.CHECKBOX_STYLE)
        deskew_layout.addWidget(deskew_check)
        processing_layout.addLayout(deskew_layout)
        
        # Add processing group to controls layout
        controls_layout.addWidget(processing_group)
        
        # OCR Settings
        ocr_group = QGroupBox("OCR Settings")
        ocr_group.setStyleSheet(ModernStyle.GROUPBOX_STYLE)
        ocr_layout = QVBoxLayout(ocr_group)
        
        # Font type
        font_layout = QHBoxLayout()
        font_label = QLabel("Font Type:")
        font_combo = QComboBox()
        font_combo.addItems(["Standard", "Legacy", "Custom"])
        font_combo.setStyleSheet(ModernStyle.COMBOBOX_STYLE)
        font_help_btn = QPushButton("?")
        font_help_btn.setFixedSize(24, 24)
        font_help_btn.setStyleSheet(ModernStyle.HELP_BUTTON_STYLE)
        font_layout.addWidget(font_label)
        font_layout.addWidget(font_combo)
        font_layout.addWidget(font_help_btn)
        ocr_layout.addLayout(font_layout)
        
        # PSM mode
        psm_layout = QHBoxLayout()
        psm_label = QLabel("PSM Mode:")
        psm_combo = QComboBox()
        psm_combo.addItems([
            "0 - Orientation and script detection only",
            "1 - Automatic page segmentation with OSD",
            "2 - Automatic page segmentation, but no OSD or OCR",
            "3 - Fully automatic page segmentation, but no OSD (Default)",
            "4 - Assume a single column of text of variable sizes",
            "5 - Assume a single uniform block of vertically aligned text",
            "6 - Assume a single uniform block of text",
            "7 - Treat the image as a single text line",
            "8 - Treat the image as a single word",
            "9 - Treat the image as a single word in a circle",
            "10 - Treat the image as a single character",
            "11 - Sparse text. Find as much text as possible in no particular order",
            "12 - Sparse text with OSD",
            "13 - Raw line. Treat the image as a single text line"
        ])
        psm_combo.setCurrentIndex(3)  # Default to PSM mode 3
        psm_combo.setStyleSheet(ModernStyle.COMBOBOX_STYLE)
        psm_help_btn = QPushButton("?")
        psm_help_btn.setFixedSize(24, 24)
        psm_help_btn.setStyleSheet(ModernStyle.HELP_BUTTON_STYLE)
        psm_layout.addWidget(psm_label)
        psm_layout.addWidget(psm_combo)
        psm_layout.addWidget(psm_help_btn)
        ocr_layout.addLayout(psm_layout)
        
        # OEM mode
        oem_layout = QHBoxLayout()
        oem_label = QLabel("OCR Engine Mode:")
        oem_combo = QComboBox()
        oem_combo.addItems([
            "0 - Legacy engine only",
            "1 - Neural nets LSTM engine only",
            "2 - Legacy + LSTM engines",
            "3 - Default, based on what is available"
        ])
        oem_combo.setCurrentIndex(3)  # Default to OEM mode 3
        oem_combo.setStyleSheet(ModernStyle.COMBOBOX_STYLE)
        oem_help_btn = QPushButton("?")
        oem_help_btn.setFixedSize(24, 24)
        oem_help_btn.setStyleSheet(ModernStyle.HELP_BUTTON_STYLE)
        oem_layout.addWidget(oem_label)
        oem_layout.addWidget(oem_combo)
        oem_layout.addWidget(oem_help_btn)
        ocr_layout.addLayout(oem_layout)
        
        # Add OCR settings to controls layout
        controls_layout.addWidget(ocr_group)
        
        # Add controls frame to left layout
        left_layout.addWidget(controls_frame, 2)
        
        # Right panel (text)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Text frame
        text_frame = QFrame()
        text_frame.setFrameShape(QFrame.StyledPanel)
        text_frame.setStyleSheet(ModernStyle.FRAME_STYLE)
        text_layout = QVBoxLayout(text_frame)
        
        # Text label
        text_label = QLabel("Extracted Text")
        text_label.setAlignment(Qt.AlignCenter)
        text_layout.addWidget(text_label)
        
        text_edit = QTextEdit()
        text_edit.setStyleSheet(ModernStyle.TEXTEDIT_STYLE)
        text_edit.setReadOnly(False)  # Allow editing
        text_edit.setPlaceholderText("OCR text will appear here. You can edit it before saving.")
        text_layout.addWidget(text_edit)
        
        # Add text frame to right layout
        right_layout.addWidget(text_frame)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([600, 600])  # Equal initial sizes
        
        # Add splitter to tab layout
        tab_layout.addWidget(splitter)
        
        # Store widgets in tab data
        tab_data['text_edit'] = text_edit
        tab_data['contrast_slider'] = contrast_slider
        tab_data['contrast_value_label'] = contrast_value_label
        tab_data['brightness_slider'] = brightness_slider
        tab_data['brightness_value_label'] = brightness_value_label
        tab_data['sharpness_slider'] = sharpness_slider
        tab_data['sharpness_value_label'] = sharpness_value_label
        tab_data['deskew_check'] = deskew_check
        tab_data['font_combo'] = font_combo
        tab_data['psm_combo'] = psm_combo
        tab_data['oem_combo'] = oem_combo
        
        # Connect signals
        contrast_slider.valueChanged.connect(lambda value, tab_idx=self.next_tab_id: self.update_contrast(value, tab_idx))
        brightness_slider.valueChanged.connect(lambda value, tab_idx=self.next_tab_id: self.update_brightness(value, tab_idx))
        sharpness_slider.valueChanged.connect(lambda value, tab_idx=self.next_tab_id: self.update_sharpness(value, tab_idx))
        psm_combo.currentIndexChanged.connect(lambda index, tab_idx=self.next_tab_id: self.update_psm(index, tab_idx))
        oem_combo.currentIndexChanged.connect(lambda index, tab_idx=self.next_tab_id: self.update_oem(index, tab_idx))
        font_help_btn.clicked.connect(self.show_font_help)
        psm_help_btn.clicked.connect(self.show_psm_help)
        oem_help_btn.clicked.connect(self.show_oem_help)
        
        # Add the tab data to the tabs dictionary
        self.tabs[self.next_tab_id] = tab_data
        self.next_tab_id += 1
        
        # Add the tab to the tab widget
        tab_index = self.tab_widget.addTab(tab_content, f"Scan {self.next_tab_id - 1}")
        
        # Set the current tab to the new tab
        self.tab_widget.setCurrentIndex(tab_index)
        
    def update_contrast(self, value, tab_idx=None):
        """Update contrast value for a tab"""
        if tab_idx is None:
            tab_idx = self.current_tab
            
        if tab_idx in self.tabs:
            contrast_value = value / 100.0
            self.tabs[tab_idx]['contrast_value'] = contrast_value
            self.tabs[tab_idx]['contrast_value_label'].setText(f"{contrast_value:.1f}")
            
            # Process OCR if image is loaded
            if self.tabs[tab_idx]['cv_image'] is not None:
                self.process_ocr(self.tabs[tab_idx])
                
    def update_brightness(self, value, tab_idx=None):
        """Update brightness value for a tab"""
        if tab_idx is None:
            tab_idx = self.current_tab
            
        if tab_idx in self.tabs:
            brightness_value = value / 100.0
            self.tabs[tab_idx]['brightness_value'] = brightness_value
            self.tabs[tab_idx]['brightness_value_label'].setText(f"{brightness_value:.1f}")
            
            # Process OCR if image is loaded
            if self.tabs[tab_idx]['cv_image'] is not None:
                self.process_ocr(self.tabs[tab_idx])
                
    def update_sharpness(self, value, tab_idx=None):
        """Update sharpness value for a tab"""
        if tab_idx is None:
            tab_idx = self.current_tab
            
        if tab_idx in self.tabs:
            sharpness_value = value / 100.0
            self.tabs[tab_idx]['sharpness_value'] = sharpness_value
            self.tabs[tab_idx]['sharpness_value_label'].setText(f"{sharpness_value:.1f}")
            
            # Process OCR if image is loaded
            if self.tabs[tab_idx]['cv_image'] is not None:
                self.process_ocr(self.tabs[tab_idx])
                
    def update_psm(self, index, tab_idx=None):
        """Update PSM mode for a tab"""
        if tab_idx is None:
            tab_idx = self.current_tab
            
        if tab_idx in self.tabs:
            self.tabs[tab_idx]['psm_mode'] = index
            
            # Process OCR if image is loaded
            if self.tabs[tab_idx]['cv_image'] is not None:
                self.process_ocr(self.tabs[tab_idx])
                
    def update_oem(self, index, tab_idx=None):
        """Update OEM mode for a tab"""
        if tab_idx is None:
            tab_idx = self.current_tab
            
        if tab_idx in self.tabs:
            self.tabs[tab_idx]['oem_mode'] = index
            
            # Process OCR if image is loaded
            if self.tabs[tab_idx]['cv_image'] is not None:
                self.process_ocr(self.tabs[tab_idx])
                
    def show_psm_help(self):
        """Show help for Page Segmentation Modes"""
        help_text = """
        <h3>Page Segmentation Modes</h3>
        <p>These modes control how Tesseract analyzes the layout of the image:</p>
        <ul>
            <li><b>Auto (Default)</b>: Fully automatic page segmentation, but no orientation detection</li>
            <li><b>Orientation Detection Only</b>: Only detect the orientation and script</li>
            <li><b>Auto with Orientation Detection</b>: Automatic page segmentation with orientation detection</li>
            <li><b>Auto without OSD</b>: Automatic page segmentation, but no OCR or orientation detection</li>
            <li><b>Single Column Variable Size</b>: Assume a single column of text of variable sizes</li>
            <li><b>Single Uniform Block</b>: Assume a single uniform block of vertically aligned text</li>
            <li><b>Single Uniform Text Block</b>: Assume a single uniform block of text</li>
            <li><b>Single Text Line</b>: Treat the image as a single text line</li>
            <li><b>Single Word</b>: Treat the image as a single word</li>
            <li><b>Single Word in Circle</b>: Treat the image as a single word in a circle</li>
            <li><b>Single Character</b>: Treat the image as a single character</li>
            <li><b>Sparse Text</b>: Find as much text as possible in no particular order</li>
            <li><b>Sparse Text with OSD</b>: Sparse text with orientation and script detection</li>
            <li><b>Raw Line</b>: Treat the image as a single text line, bypassing hacks that are Tesseract-specific</li>
        </ul>
        <p>Choose the mode that best matches your image content for optimal results.</p>
        """
        
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Page Segmentation Modes Help")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(help_text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        
        # Set application icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons', 'camera_icon.svg')
        if os.path.exists(icon_path):
            msg_box.setWindowIcon(QIcon(icon_path))
            
        msg_box.exec_()
        
    def show_oem_help(self):
        """Show help for OCR Engine Modes"""
        help_text = """
        <h3>OCR Engine Modes</h3>
        <p>These modes control which OCR engine Tesseract uses:</p>
        <ul>
            <li><b>Legacy Engine Only</b>: Use only the original Tesseract engine</li>
            <li><b>Neural Network Only</b>: Use only the LSTM neural network engine</li>
            <li><b>Legacy + Neural Network</b>: Use both engines together</li>
            <li><b>Default (Best Available)</b>: Let Tesseract decide which engine to use</li>
        </ul>
        <p>The neural network engine generally provides better results for most modern fonts, while the legacy engine might perform better on some specific fonts or low-quality images.</p>
        """
        
        msg_box = QMessageBox()
        msg_box.setWindowTitle("OCR Engine Modes Help")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(help_text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        
        # Set application icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons', 'camera_icon.svg')
        if os.path.exists(icon_path):
            msg_box.setWindowIcon(QIcon(icon_path))
            
        msg_box.exec_()
        
    def show_font_help(self):
        """Show help dialog for font types"""
        help_text = """
        <h3>Font Type Selection Help</h3>
        <p>Select the font type that best matches your document to improve OCR accuracy:</p>
        <ul>
            <li><b>Standard</b>: General-purpose processing suitable for most documents.</li>
            <li><b>Legacy</b>: Optimized for older or lower quality documents.</li>
            <li><b>Custom</b>: Use custom processing parameters for special cases.</li>
        </ul>
        <p>Choosing the right font type can significantly improve OCR accuracy.</p>
        """
        
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Font Type Help")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(help_text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        
        # Set application icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons', 'camera_icon.svg')
        if os.path.exists(icon_path):
            msg_box.setWindowIcon(QIcon(icon_path))
            
        msg_box.exec_()
        
def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    window = OCRTextExtractor()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
