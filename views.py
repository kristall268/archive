"""
Представления приложения с фильтрацией и поиском
"""
import customtkinter as ctk
from tkinter import ttk
from typing import Callable, Optional, List
from models import Task
from tkcalendar import DateEntry
from datetime import datetime


class MenuBarView:
    """Меню приложения - интегрировано в заголовок таблицы"""
    
    def __init__(self, parent, on_save: Callable, on_load: Callable, 
                 on_export: Callable, on_exit: Callable):
        self.parent = parent
        self.on_save = on_save
        self.on_load = on_load
        self.on_export = on_export
        self.on_exit = on_exit
        # Меню теперь создается в TableContainerView
    
    def create_file_button(self, parent) -> ctk.CTkButton:
        """Создать кнопку 'Файл' в стиле кнопки 'Добавить'"""
        file_btn = ctk.CTkButton(
            parent,
            text="📁 Файл",
            font=ctk.CTkFont(size=13),
            height=35,
            width=100,
            corner_radius=8,
            command=self._show_file_menu
        )
        return file_btn
    
    def _show_file_menu(self):
        """Показать меню файла"""
        menu = ctk.CTkToplevel(self.parent)
        menu.overrideredirect(True)
        menu.configure(fg_color="white")
        
        menu_frame = ctk.CTkFrame(
            menu,
            fg_color="white",
            border_width=1,
            border_color="#d0d0d0",
            corner_radius=8
        )
        menu_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Пункты меню
        self._create_menu_item(menu_frame, "💾 Сохранить", self.on_save, menu)
        self._create_menu_item(menu_frame, "📂 Открыть...", self.on_load, menu)
        
        separator = ctk.CTkFrame(menu_frame, height=1, fg_color="#e0e0e0")
        separator.pack(fill="x", padx=5, pady=2)
        
        self._create_menu_item(menu_frame, "📊 Экспорт в Excel...", self.on_export, menu)
        
        separator2 = ctk.CTkFrame(menu_frame, height=1, fg_color="#e0e0e0")
        separator2.pack(fill="x", padx=5, pady=2)
        
        self._create_menu_item(menu_frame, "❌ Выход", self.on_exit, menu)
        
        # Позиционирование меню
        try:
            x = self.parent.winfo_rootx() + 50
            y = self.parent.winfo_rooty() + 150
            menu.geometry(f"+{x}+{y}")
        except:
            pass
        
        menu.bind('<FocusOut>', lambda e: menu.destroy())
        menu.focus_set()
    
    def _create_menu_item(self, parent, text: str, command: Callable, menu):
        """Создать пункт меню"""
        def execute_and_close():
            menu.destroy()
            command()
        
        btn = ctk.CTkButton(
            parent,
            text=text,
            command=execute_and_close,
            fg_color="white",
            text_color="black",
            hover_color="#e0e0e0",
            anchor="w",
            height=35,
            width=200
        )
        btn.pack(fill="x", padx=2, pady=2)
        return btn


class FilterPanelView:
    """Панель фильтрации и поиска"""
    
    def __init__(self, parent, on_filter_change: Callable):
        self.on_filter_change = on_filter_change
        self.filter_frame = ctk.CTkFrame(
            parent,
            fg_color="#f8f9fa",
            corner_radius=10
        )
        self.filter_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Создать виджеты фильтрации"""
        # Заголовок панели
        header_frame = ctk.CTkFrame(self.filter_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="🔍 Фильтры и поиск",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#495057"
        )
        title_label.pack(side="left")
        
        # Кнопка сброса фильтров
        self.reset_btn = ctk.CTkButton(
            header_frame,
            text="Сбросить",
            width=90,
            height=28,
            corner_radius=6,
            fg_color="#6c757d",
            hover_color="#5a6268",
            font=ctk.CTkFont(size=11),
            command=self._reset_filters
        )
        self.reset_btn.pack(side="right")
        
        # Контейнер для фильтров
        content_frame = ctk.CTkFrame(self.filter_frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # Первая строка: Поиск
        search_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 10))
        
        search_label = ctk.CTkLabel(
            search_frame,
            text="Поиск по ID / Объекту:",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=150,
            anchor="w"
        )
        search_label.pack(side="left", padx=(0, 10))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Введите ID или название объекта...",
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind('<KeyRelease>', lambda e: self.on_filter_change())
        
        # Вторая строка: Тип зависимости и Количество зависимостей
        row2_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        row2_frame.pack(fill="x", pady=(0, 10))
        
        # Тип зависимости
        type_container = ctk.CTkFrame(row2_frame, fg_color="transparent")
        type_container.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        type_label = ctk.CTkLabel(
            type_container,
            text="Тип зависимости:",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=150,
            anchor="w"
        )
        type_label.pack(side="left", padx=(0, 10))
        
        type_options = ["Все", "FS - Finish-Start", "SS - Start-Start",
                       "FF - Finish-Finish", "SF - Start-Finish", "Без типа"]
        self.type_combo = ctk.CTkComboBox(
            type_container,
            values=type_options,
            height=35,
            font=ctk.CTkFont(size=12),
            command=lambda _: self.on_filter_change()
        )
        self.type_combo.set("Все")
        self.type_combo.pack(side="left", fill="x", expand=True)
        
        # Количество зависимостей
        deps_container = ctk.CTkFrame(row2_frame, fg_color="transparent")
        deps_container.pack(side="left", fill="x", expand=True)
        
        deps_label = ctk.CTkLabel(
            deps_container,
            text="Зависимости:",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=120,
            anchor="w"
        )
        deps_label.pack(side="left", padx=(0, 10))
        
        deps_options = ["Все", "Без зависимостей", "С зависимостями", "1 зависимость", 
                       "2+ зависимости"]
        self.deps_combo = ctk.CTkComboBox(
            deps_container,
            values=deps_options,
            height=35,
            font=ctk.CTkFont(size=12),
            command=lambda _: self.on_filter_change()
        )
        self.deps_combo.set("Все")
        self.deps_combo.pack(side="left", fill="x", expand=True)
        
        # Третья строка: Даты
        date_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        date_frame.pack(fill="x")
        
        # Дата начала
        start_date_container = ctk.CTkFrame(date_frame, fg_color="transparent")
        start_date_container.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        start_label = ctk.CTkLabel(
            start_date_container,
            text="Дата начала (от):",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=150,
            anchor="w"
        )
        start_label.pack(side="left", padx=(0, 10))
        
        start_date_frame = ctk.CTkFrame(
            start_date_container,
            fg_color="white",
            height=35,
            corner_radius=6
        )
        start_date_frame.pack(side="left", fill="x", expand=True)
        start_date_frame.pack_propagate(False)
        
        self.start_date_entry = DateEntry(
            start_date_frame,
            width=20,
            background='#3B8ED0',
            foreground='white',
            borderwidth=0,
            date_pattern='dd.mm.yyyy',
            font=('Segoe UI', 10)
        )
        self.start_date_entry.pack(fill="both", expand=True, padx=5, pady=3)
        self.start_date_entry.bind("<<DateEntrySelected>>", lambda e: self.on_filter_change())
        
        # Дата окончания
        end_date_container = ctk.CTkFrame(date_frame, fg_color="transparent")
        end_date_container.pack(side="left", fill="x", expand=True)
        
        end_label = ctk.CTkLabel(
            end_date_container,
            text="Дата окончания (до):",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=150,
            anchor="w"
        )
        end_label.pack(side="left", padx=(0, 10))
        
        end_date_frame = ctk.CTkFrame(
            end_date_container,
            fg_color="white",
            height=35,
            corner_radius=6
        )
        end_date_frame.pack(side="left", fill="x", expand=True)
        end_date_frame.pack_propagate(False)
        
        self.end_date_entry = DateEntry(
            end_date_frame,
            width=20,
            background='#3B8ED0',
            foreground='white',
            borderwidth=0,
            date_pattern='dd.mm.yyyy',
            font=('Segoe UI', 10)
        )
        self.end_date_entry.pack(fill="both", expand=True, padx=5, pady=3)
        self.end_date_entry.bind("<<DateEntrySelected>>", lambda e: self.on_filter_change())
        
        # Чекбокс для включения фильтра по датам
        self.date_filter_enabled = ctk.BooleanVar(value=False)
        self.date_checkbox = ctk.CTkCheckBox(
            date_frame,
            text="Применить",
            variable=self.date_filter_enabled,
            font=ctk.CTkFont(size=11),
            command=self.on_filter_change
        )
        self.date_checkbox.pack(side="left", padx=(10, 0))
    
    def _reset_filters(self):
        """Сбросить все фильтры"""
        self.search_entry.delete(0, 'end')
        self.type_combo.set("Все")
        self.deps_combo.set("Все")
        self.date_filter_enabled.set(False)
        self.start_date_entry.set_date(datetime.now())
        self.end_date_entry.set_date(datetime.now())
        self.on_filter_change()
    
    def get_filters(self) -> dict:
        """Получить текущие значения фильтров"""
        return {
            'search': self.search_entry.get().strip().lower(),
            'type': self.type_combo.get(),
            'dependencies': self.deps_combo.get(),
            'date_enabled': self.date_filter_enabled.get(),
            'start_date': self.start_date_entry.get_date().strftime("%d.%m.%Y") if self.date_filter_enabled.get() else None,
            'end_date': self.end_date_entry.get_date().strftime("%d.%m.%Y") if self.date_filter_enabled.get() else None
        }


class NotificationView:
    """Компонент для отображения уведомлений"""

    def __init__(self, parent):
        self.parent = parent

    def show(self, message: str, duration: int = 2000):
        """Показать уведомление"""
        notification = ctk.CTkFrame(
            self.parent,
            fg_color="#2d2d2d",
            corner_radius=8
        )
        notification.place(relx=0.5, rely=0.95, anchor="center")

        label = ctk.CTkLabel(
            notification,
            text=message,
            font=ctk.CTkFont(size=12),
            text_color="white"
        )
        label.pack(padx=20, pady=10)

        self.parent.after(duration, notification.destroy)


class ContextMenuView:
    """Контекстное меню для таблицы"""

    def __init__(self, parent, tree: ttk.Treeview,
                 on_copy: Callable, on_edit: Callable,
                 on_paste: Callable, on_delete: Callable,
                 has_clipboard: Callable):
        self.parent = parent
        self.tree = tree
        self.on_copy = on_copy
        self.on_edit = on_edit
        self.on_paste = on_paste
        self.on_delete = on_delete
        self.has_clipboard = has_clipboard
        self.current_menu = None
        self.menu_closing = False

        self.tree.bind('<Button-3>', self.show)

    def close_current_menu(self):
        """Закрыть текущее меню"""
        if self.current_menu and not self.menu_closing:
            self.menu_closing = True
            try:
                self.current_menu.destroy()
            except:
                pass
            self.current_menu = None
            self.menu_closing = False

    def show(self, event):
        """Показать контекстное меню"""
        self.close_current_menu()

        row_id = self.tree.identify_row(event.y)
        if not row_id:
            return

        self.tree.selection_set(row_id)

        menu = ctk.CTkToplevel(self.parent)
        menu.overrideredirect(True)
        menu.configure(fg_color="white")
        self.current_menu = menu

        menu_frame = ctk.CTkFrame(
            menu,
            fg_color="white",
            border_width=1,
            border_color="#d0d0d0",
            corner_radius=8
        )
        menu_frame.pack(fill="both", expand=True, padx=2, pady=2)

        self._create_menu_button(
            menu_frame,
            "📋 Копировать (Ctrl+C)",
            self.on_copy
        )

        self._create_menu_button(
            menu_frame,
            "✏️ Редактировать",
            self.on_edit
        )

        self._create_menu_button(
            menu_frame,
            "📄 Вставить (Ctrl+V)",
            self.on_paste,
            state="normal" if self.has_clipboard() else "disabled"
        )

        separator = ctk.CTkFrame(menu_frame, height=1, fg_color="#e0e0e0")
        separator.pack(fill="x", padx=5, pady=2)

        self._create_menu_button(
            menu_frame,
            "🗑️ Удалить (Delete)",
            self.on_delete,
            text_color="#dc3545",
            hover_color="#ffebee"
        )

        menu.geometry(f"+{event.x_root}+{event.y_root}")

        menu.bind('<FocusOut>', lambda e: self.close_current_menu())
        
        def handle_outside_click(e):
            widget = e.widget
            try:
                if str(widget).startswith(str(menu)):
                    return
            except:
                pass
            self.close_current_menu()
        
        self.parent.after(50, lambda: self.parent.bind('<Button-1>', handle_outside_click, add='+'))

        menu.focus_set()

    def _create_menu_button(self, parent, text: str, command: Callable,
                            text_color="black", hover_color="#e0e0e0",
                            state="normal"):
        """Создать кнопку меню"""
        def execute_and_close():
            self.close_current_menu()
            command()

        btn = ctk.CTkButton(
            parent,
            text=text,
            command=execute_and_close,
            fg_color="white",
            text_color=text_color,
            hover_color=hover_color,
            anchor="w",
            height=35,
            state=state
        )
        btn.pack(fill="x", padx=2, pady=2)
        return btn


class TaskTableView:
    """Представление таблицы задач с улучшенным выделением"""

    def __init__(self, parent_frame, on_dependency_click: Callable,
                 on_edit: Callable):
        self.on_dependency_click = on_dependency_click
        self.on_edit = on_edit
        self.processing_click = False

        self._configure_styles()

        tree_frame = ctk.CTkFrame(parent_frame, fg_color="white")
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")

        columns = ("ID", "Объект", "Дата начала", "Дата окончания",
                   "Длительность", "Зависит от", "Тип зависимости")

        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar.set,
            selectmode="browse"
        )

        scrollbar.config(command=self.tree.yview)

        column_widths = [120, 150, 130, 140, 100, 200, 150]
        for col, width in zip(columns, column_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")

        self.tree.pack(fill="both", expand=True)

        self.tree.bind('<Button-1>', self._on_button_press, add='+')
        self.tree.bind('<Double-Button-1>', self._on_double_click, add='+')

    def _configure_styles(self):
        """Настройка стилей с улучшенным выделением"""
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Treeview",
                        background="white",
                        foreground="black",
                        rowheight=50,
                        fieldbackground="white",
                        borderwidth=0,
                        font=('Segoe UI', 10))

        style.configure("Treeview.Heading",
                        background="#f8f9fa",
                        foreground="#6c757d",
                        borderwidth=0,
                        font=('Segoe UI', 10, 'bold'))

        # Улучшенное выделение
        style.map('Treeview',
                  background=[('selected', '#B8E6F0')],
                  foreground=[('selected', '#0D7C99')])

    def _on_button_press(self, event):
        """Обработка нажатия кнопки мыши"""
        if self.processing_click:
            return "break"
        
        self.processing_click = True
        
        try:
            region = self.tree.identify_region(event.x, event.y)
            row_id = self.tree.identify_row(event.y)
            column = self.tree.identify_column(event.x)
            
            if region == "cell" and row_id and column == "#6":
                self.tree.selection_set(row_id)
                self.tree.focus(row_id)
                self.tree.after(10, lambda: self.on_dependency_click(event, row_id))
                return "break"
            
        finally:
            self.tree.after(10, lambda: setattr(self, 'processing_click', False))

    def _on_double_click(self, event):
        """Обработка двойного клика"""
        if self.processing_click:
            return "break"
            
        region = self.tree.identify_region(event.x, event.y)
        
        if region != "cell":
            return "break"

        column = self.tree.identify_column(event.x)
        row_id = self.tree.identify_row(event.y)
        
        if not row_id:
            return "break"
        
        if column == "#6":
            return "break"

        self.tree.selection_set(row_id)
        self.tree.after(10, lambda: self.on_edit(event))
        return "break"

    def populate(self, tasks: List[Task]):
        """Заполнить таблицу данными"""
        current_selection = self.tree.selection()
        selected_index = None
        if current_selection:
            try:
                selected_index = self.tree.index(current_selection[0])
            except:
                pass

        for item in self.tree.get_children():
            self.tree.delete(item)

        for task in tasks:
            self.tree.insert("", "end", values=(
                task.id,
                task.object,
                task.start_date,
                task.end_date,
                task.duration,
                task.get_dependency_text(),
                task.type
            ))

        if selected_index is not None:
            try:
                items = self.tree.get_children()
                if 0 <= selected_index < len(items):
                    self.tree.selection_set(items[selected_index])
                    self.tree.see(items[selected_index])
            except:
                pass

    def get_selected_index(self) -> Optional[int]:
        """Получить индекс выбранной строки"""
        selection = self.tree.selection()
        if not selection:
            return None
        row_id = selection[0]
        return self.tree.index(row_id)

    def bind_delete(self, callback: Callable):
        """Привязать обработчик удаления"""
        self.tree.bind('<Delete>', callback)

    def bind_copy(self, callback: Callable):
        """Привязать обработчик копирования"""
        self.tree.bind('<Control-c>', callback)

    def bind_paste(self, callback: Callable):
        """Привязать обработчик вставки"""
        self.tree.bind('<Control-v>', callback)


class HeaderView:
    """Представление заголовка приложения"""

    def __init__(self, parent):
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 10))

        title_label = ctk.CTkLabel(
            header_frame,
            text="Управление проектом",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Планирование и визуализация задач",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        subtitle_label.pack(anchor="w")


class TabsView:
    """Представление вкладок"""

    def __init__(self, parent):
        tab_frame = ctk.CTkFrame(parent, fg_color="transparent")
        tab_frame.pack(fill="x", padx=30, pady=(10, 0))

        table_tab = ctk.CTkButton(
            tab_frame,
            text="Таблица",
            width=120,
            height=40,
            corner_radius=8,
            fg_color="white",
            text_color="black",
            hover_color="#e0e0e0"
        )
        table_tab.pack(side="left", padx=(0, 5))

        gantt_tab = ctk.CTkButton(
            tab_frame,
            text="Диаграмма Ганта",
            width=150,
            height=40,
            corner_radius=8,
            fg_color="transparent",
            text_color="gray",
            hover_color="#f0f0f0",
            border_width=0
        )
        gantt_tab.pack(side="left")


class TableContainerView:
    """Контейнер таблицы с заголовком и кнопками"""

    def __init__(self, parent, on_add_task: Callable, menu_bar_view: MenuBarView):
        self.container = ctk.CTkFrame(
            parent,
            fg_color="white",
            corner_radius=10
        )
        self.container.pack(fill="both", expand=True, padx=30, pady=20)

        # Заголовок таблицы и кнопки
        table_header = ctk.CTkFrame(self.container, fg_color="transparent")
        table_header.pack(fill="x", padx=20, pady=(20, 10))

        table_title = ctk.CTkLabel(
            table_header,
            text="Таблица задач",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        table_title.pack(side="left")

        # Контейнер для кнопок справа
        buttons_container = ctk.CTkFrame(table_header, fg_color="transparent")
        buttons_container.pack(side="right")

        # Кнопка "Файл"
        file_button = menu_bar_view.create_file_button(buttons_container)
        file_button.pack(side="left", padx=(0, 10))

        # Кнопка "Добавить"
        add_button = ctk.CTkButton(
            buttons_container,
            text="+ Добавить задачу",
            font=ctk.CTkFont(size=13),
            height=35,
            width=150,
            corner_radius=8,
            command=on_add_task
        )
        add_button.pack(side="left")