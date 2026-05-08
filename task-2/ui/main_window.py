import os
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QTextEdit, QScrollArea, QFrame, QProgressBar, QFileDialog, QGridLayout, QSizePolicy, QApplication, QSpacerItem
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize
from PySide6.QtGui import QFont, QIcon
from core.audio_recorder import AudioRecorderThread
from core.transcriber import TranscriberThread, get_language_display, WHISPER_MODELS, LANGUAGE_NAMES
from core.ingredient_parser import parse_ingredients
from core.recipe_filter import load_recipes, filter_recipes

class IngredientChip(QFrame):

    def __init__(self, text: str, on_remove=None, parent=None):
        super().__init__(parent)
        self.ingredient_text = text
        self.on_remove = on_remove
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 6, 5)
        layout.setSpacing(6)
        label = QLabel(text)
        label
        layout.addWidget(label)
        remove_btn = QPushButton('✕')
        remove_btn.setFixedSize(20, 20)
        remove_btn.setCursor(Qt.PointingHandCursor)
        remove_btn
        remove_btn.clicked.connect(self._on_remove_clicked)
        layout.addWidget(remove_btn)
        self

    def _on_remove_clicked(self):
        if self.on_remove:
            self.on_remove(self.ingredient_text)

class RecipeCard(QFrame):

    def __init__(self, recipe: dict, matched_ingredients: set=None, parent=None):
        super().__init__(parent)
        self.setObjectName('recipeCard')
        self.setCursor(Qt.PointingHandCursor)
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 14, 16, 14)
        category = recipe.get('category', 'inne')
        cat_label = QLabel(f'KATEGORIA: {category.upper()}')
        cat_label
        layout.addWidget(cat_label)
        name_label = QLabel(recipe.get('name', 'Bez nazwy'))
        name_label
        name_label.setWordWrap(True)
        layout.addWidget(name_label)
        meta_text = f"Czas: {recipe.get('prep_time', '?')} | Porcje: {recipe.get('servings', '?')}"
        meta_label = QLabel(meta_text)
        meta_label
        layout.addWidget(meta_label)
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep
        layout.addWidget(sep)
        ing_label = QLabel('Składniki:')
        ing_label
        layout.addWidget(ing_label)
        matched = matched_ingredients or set()
        ingredients = recipe.get('ingredients', [])
        for ing in ingredients:
            is_matched = ing.lower() in {m.lower() for m in matched}
            marker = '-'
            il = QLabel(f'  {marker} {ing}')
            il
            layout.addWidget(il)
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2
        layout.addWidget(sep2)
        instr_label = QLabel('Sposób przygotowania:')
        instr_label
        layout.addWidget(instr_label)
        instructions = recipe.get('instructions', 'Brak instrukcji.')
        instr_text = QLabel(instructions)
        instr_text.setWordWrap(True)
        instr_text
        layout.addWidget(instr_text)
        layout.addStretch()
        self.setMinimumWidth(280)
        self.setMaximumWidth(400)

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Filtr Przepisów Głosowy')
        self.setMinimumSize(1000, 750)
        self.resize(1100, 850)
        self.recipes = load_recipes()
        self.current_ingredients = []
        self.detected_language = None
        self.transcribed_text = ''
        self.recorder_thread = None
        self.transcriber_thread = None
        self.is_recording = False
        self._pulse_state = False
        self
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        central.setObjectName('centralWidget')
        self.setCentralWidget(central)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_content = QWidget()
        self.main_layout = QVBoxLayout(scroll_content)
        self.main_layout.setSpacing(4)
        self.main_layout.setContentsMargins(4, 4, 4, 4)
        scroll.setWidget(scroll_content)
        outer_layout = QVBoxLayout(central)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)
        self._create_voice_input_section()
        self._create_transcription_section()
        self._create_ingredients_section()
        self._create_recipes_section()
        self.main_layout.addStretch()

    def _create_voice_input_section(self):
        section = QFrame()
        section.setObjectName('sectionFrame')
        layout = QVBoxLayout(section)
        layout.setSpacing(4)
        title = QLabel('Wejście głosowe')
        title.setObjectName('sectionTitle')
        layout.addWidget(title)
        controls = QHBoxLayout()
        controls.setSpacing(4)
        self.record_btn = QPushButton('Nagraj')
        self.record_btn.setObjectName('recordButton')
        self.record_btn.setToolTip('Kliknij, aby rozpocząć nagrywanie')
        self.record_btn.setCursor(Qt.PointingHandCursor)
        self.record_btn.clicked.connect(self._toggle_recording)
        controls.addWidget(self.record_btn)
        mid_layout = QVBoxLayout()
        mid_layout.setSpacing(6)
        self.status_label = QLabel('Gotowy — kliknij mikrofon lub załaduj plik audio')
        self.status_label.setObjectName('statusLabel')
        mid_layout.addWidget(self.status_label)
        controls.addLayout(mid_layout, 1)
        right_layout = QVBoxLayout()
        right_layout.setSpacing(4)
        load_btn = QPushButton('Załaduj plik audio')
        load_btn.setCursor(Qt.PointingHandCursor)
        load_btn.clicked.connect(self._load_audio_file)
        right_layout.addWidget(load_btn)
        model_row = QHBoxLayout()
        model_label = QLabel('Model:')
        model_label
        model_row.addWidget(model_label)
        self.model_combo = QComboBox()
        for m in WHISPER_MODELS:
            self.model_combo.addItem(m)
        self.model_combo.setCurrentText('base')
        self.model_combo.setToolTip('Większy model = lepsza dokładność, ale wolniejszy')
        model_row.addWidget(self.model_combo)
        right_layout.addLayout(model_row)
        controls.addLayout(right_layout)
        layout.addLayout(controls)
        self.main_layout.addWidget(section)

    def _create_transcription_section(self):
        section = QFrame()
        section.setObjectName('sectionFrame')
        layout = QVBoxLayout(section)
        layout.setSpacing(4)
        title = QLabel('Transkrypcja')
        title.setObjectName('sectionTitle')
        layout.addWidget(title)
        lang_row = QHBoxLayout()
        lang_title = QLabel('Wykryty język:')
        lang_title
        lang_row.addWidget(lang_title)
        self.lang_label = QLabel('brak')
        self.lang_label.setObjectName('langLabel')
        lang_row.addWidget(self.lang_label)
        lang_row.addStretch()
        layout.addLayout(lang_row)
        self.transcription_edit = QTextEdit()
        self.transcription_edit.setPlaceholderText('Tekst transkrypcji pojawi się tutaj...')
        self.transcription_edit.setMaximumHeight(100)
        self.transcription_edit.setReadOnly(True)
        layout.addWidget(self.transcription_edit)
        self.main_layout.addWidget(section)

    def _create_ingredients_section(self):
        section = QFrame()
        section.setObjectName('sectionFrame')
        layout = QVBoxLayout(section)
        layout.setSpacing(4)
        title_row = QHBoxLayout()
        title = QLabel('Wykryte składniki')
        title.setObjectName('sectionTitle')
        title_row.addWidget(title)
        title_row.addStretch()
        self.ingredient_count_label = QLabel('0 składników')
        self.ingredient_count_label
        title_row.addWidget(self.ingredient_count_label)
        self.clear_btn = QPushButton('Wyczyść wszystko')
        self.clear_btn.setObjectName('dangerButton')
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.setFixedHeight(32)
        self.clear_btn.setEnabled(False)
        self.clear_btn.clicked.connect(self._clear_ingredients)
        title_row.addWidget(self.clear_btn)
        layout.addLayout(title_row)
        self.chips_container = QWidget()
        self.chips_layout = FlowLayout(self.chips_container, margin=4, spacing=8)
        layout.addWidget(self.chips_container)
        self.no_ingredients_label = QLabel('Nagraj lub załaduj audio, aby wyodrębnić składniki...')
        self.no_ingredients_label
        self.no_ingredients_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.no_ingredients_label)
        self.search_btn = QPushButton('Szukaj przepisów')
        self.search_btn.setObjectName('accentButton')
        self.search_btn.setCursor(Qt.PointingHandCursor)
        self.search_btn.setEnabled(False)
        self.search_btn.setFixedHeight(42)
        self.search_btn.clicked.connect(self._search_recipes)
        layout.addWidget(self.search_btn)
        self.main_layout.addWidget(section)

    def _create_recipes_section(self):
        section = QFrame()
        section.setObjectName('sectionFrame')
        section_layout = QVBoxLayout(section)
        section_layout.setSpacing(4)
        title_row = QHBoxLayout()
        self.recipes_title = QLabel('Przepisy')
        self.recipes_title.setObjectName('sectionTitle')
        title_row.addWidget(self.recipes_title)
        title_row.addStretch()
        self.recipe_count_label = QLabel('')
        self.recipe_count_label
        title_row.addWidget(self.recipe_count_label)
        section_layout.addLayout(title_row)
        self.recipe_container = QWidget()
        self.recipe_grid = QGridLayout(self.recipe_container)
        self.recipe_grid.setSpacing(4)
        self.recipe_grid.setContentsMargins(0, 0, 0, 0)
        section_layout.addWidget(self.recipe_container)
        self.no_results_label = QLabel('Wyszukaj przepisy za pomocą składników wykrytych w nagraniu.')
        self.no_results_label
        self.no_results_label.setAlignment(Qt.AlignCenter)
        section_layout.addWidget(self.no_results_label)
        self.main_layout.addWidget(section)

    def _toggle_recording(self):
        if self.is_recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self):
        self.is_recording = True
        self.record_btn.setObjectName('recordButtonRecording')
        self.record_btn.setText('Stop')
        self.record_btn.setToolTip('Kliknij, aby zatrzymać nagrywanie')
        self.status_label.setText('Nagrywanie... Powiedz składniki!')
        self.record_btn.style().unpolish(self.record_btn)
        self.record_btn.style().polish(self.record_btn)
        self.recorder_thread = AudioRecorderThread(sample_rate=16000)
        self.recorder_thread.finished.connect(self._on_recording_finished)
        self.recorder_thread.error.connect(self._on_recording_error)
        self.recorder_thread.start()

    def _stop_recording(self):
        self.is_recording = False
        self.record_btn.setObjectName('recordButton')
        self.record_btn.setText('Nagraj')
        self.record_btn.setToolTip('Kliknij, aby rozpocząć nagrywanie')
        self.record_btn.style().unpolish(self.record_btn)
        self.record_btn.style().polish(self.record_btn)
        self.status_label.setText('Przetwarzanie nagrania...')
        self.status_label
        if self.recorder_thread:
            self.recorder_thread.stop()
        pass

    def _on_recording_finished(self, audio_path: str):
        self.status_label.setText('Nagranie zapisane. Rozpoczynam transkrypcję...')
        self._start_transcription(audio_path)

    def _on_recording_error(self, error_msg: str):
        self.status_label.setText(f'Błąd: {error_msg}')
        self.status_label

    def _load_audio_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Wybierz plik audio', '', 'Pliki audio (*.wav *.mp3 *.m4a *.flac *.ogg *.wma);;Wszystkie pliki (*)')
        if file_path:
            self.status_label.setText(f'Załadowano: {os.path.basename(file_path)}')
            self._start_transcription(file_path)

    def _start_transcription(self, audio_path: str):
        model_name = self.model_combo.currentText()
        self.record_btn.setEnabled(False)
        self.status_label.setText('Ładowanie modelu Whisper...')
        self.transcriber_thread = TranscriberThread(audio_path, model_name)
        self.transcriber_thread.finished.connect(self._on_transcription_finished)
        self.transcriber_thread.progress.connect(self._on_transcription_progress)
        self.transcriber_thread.error.connect(self._on_transcription_error)
        self.transcriber_thread.start()

    def _on_transcription_progress(self, msg: str):
        self.status_label.setText(msg)

    def _on_transcription_finished(self, text: str, lang_code: str, lang_probs: dict):
        self.record_btn.setEnabled(True)
        self.transcribed_text = text
        self.detected_language = lang_code
        self.status_label.setText('Transkrypcja zakończona!')
        self.status_label
        self.lang_label.setText(get_language_display(lang_code))
        self.transcription_edit.setText(text)
        ingredients = parse_ingredients(text)
        self._update_ingredients(ingredients)

    def _on_transcription_error(self, error_msg: str):
        self.record_btn.setEnabled(True)
        self.status_label.setText(f'Błąd: {error_msg}')
        self.status_label

    def _update_ingredients(self, ingredients: list):
        self.current_ingredients = list(ingredients)
        self._refresh_ingredient_chips()

    def _refresh_ingredient_chips(self):
        self.chips_layout.clearAll()
        if self.current_ingredients:
            self.no_ingredients_label.setVisible(False)
            for ing in self.current_ingredients:
                chip = IngredientChip(ing, on_remove=self._remove_ingredient)
                self.chips_layout.addWidget(chip)
            self.ingredient_count_label.setText(f'{len(self.current_ingredients)} składników')
            self.search_btn.setEnabled(True)
            self.clear_btn.setEnabled(True)
        else:
            self.no_ingredients_label.setVisible(True)
            self.ingredient_count_label.setText('0 składników')
            self.search_btn.setEnabled(False)
            self.clear_btn.setEnabled(False)
        if self.current_ingredients:
            self._search_recipes()

    def _remove_ingredient(self, ingredient: str):
        if ingredient in self.current_ingredients:
            self.current_ingredients.remove(ingredient)
            self._refresh_ingredient_chips()

    def _clear_ingredients(self):
        self.current_ingredients = []
        self._refresh_ingredient_chips()
        self._clear_recipe_results()

    def _search_recipes(self):
        results = filter_recipes(self.recipes, self.current_ingredients)
        self._display_recipes(results)

    def _display_recipes(self, results: list):
        while self.recipe_grid.count():
            item = self.recipe_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if results:
            self.no_results_label.setVisible(False)
            self.recipe_count_label.setText(f'Znaleziono {len(results)} przepisów')
            self.recipes_title.setText(f'Przepisy ({len(results)})')
            cols = max(1, (self.width() - 80) // 340)
            for i, recipe in enumerate(results):
                matched = recipe.get('_matched_ingredients', set())
                card = RecipeCard(recipe, matched)
                row = i // cols
                col = i % cols
                self.recipe_grid.addWidget(card, row, col, Qt.AlignTop)
            total_rows = (len(results) + cols - 1) // cols
            self.recipe_grid.setRowStretch(total_rows, 1)
        else:
            self.no_results_label.setVisible(True)
            self.no_results_label.setText('Nie znaleziono przepisów zawierających wszystkie podane składniki.\nSpróbuj usunąć niektóre składniki.')
            self.recipe_count_label.setText('0 przepisów')
            self.recipes_title.setText('Przepisy')

    def _clear_recipe_results(self):
        while self.recipe_grid.count():
            item = self.recipe_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.no_results_label.setVisible(True)
        self.no_results_label.setText('Wyszukaj przepisy za pomocą składników wykrytych w nagraniu.')
        self.recipe_count_label.setText('')
        self.recipes_title.setText('Przepisy')

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.recipe_grid.count() > 0:
            pass

class FlowLayout(QVBoxLayout):

    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        self.setContentsMargins(margin, margin, margin, margin)
        self._spacing = spacing if spacing >= 0 else 8
        self._items = []
        self._rows = []
        self.setSpacing(2)

    def addWidget(self, widget):
        self._items.append(widget)
        self._relayout()

    def clearAll(self):
        for widget in self._items:
            widget.deleteLater()
        self._items.clear()
        self._relayout()

    def _relayout(self):
        for row_layout in self._rows:
            while row_layout.count():
                row_layout.takeAt(0)
            self.removeItem(row_layout)
            row_layout.deleteLater()
        self._rows = []
        if not self._items:
            return
        row = QHBoxLayout()
        row.setSpacing(self._spacing)
        row.setContentsMargins(0, 0, 0, 0)
        for widget in self._items:
            row.addWidget(widget)
        row.addStretch()
        self._rows.append(row)
        super().addLayout(row)