"""
Представления приложения - паттерн Observer/MVC
"""
import customtkinter as ctk
from tkinter import ttk
from typing import Callable, Optional, List
from models import Task


class MenuBarView:
    """Меню приложения"""

    def __init__(self, parent, on_save: Callable, on_load: Callable, 
                 on_export: Callable, on_exit: Callable):
        self.parent = parent
        
        # Создаем фрейм для меню
        menu_frame = ctk.CTkFrame(parent, fg_color="#f0f0f0", height=40)
        menu_frame.pack(fill="x", padx=0, pady=0)
        menu_frame.pack_propagate(False)
        
        # Контейнер для кнопок меню
        buttons_container = ctk.CTkFrame(menu_frame, fg_color="transparent")
        buttons_container.pack(side="left", padx=10, pady=5)
        
        # Кнопка "Файл"
        self._create_menu_button(
            buttons_container,
            "📁 Файл",
            lambda: self._show_file_menu(on_save, on_load, on_export, on_exit)
        )

    def _create_menu_button(self, parent, text: str, command: Callable):
        """Создать кнопку меню"""
        btn = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=80,
            height=30,
            fg_color="transparent",
            hover_color="#e0e0e0",
            text_color="#333333",
            font=ctk.CTkFont(size=12)
        )
        btn.pack(side="left", padx=2)
        return btn

    def _show_file_menu(self, on_save: Callable, on_load: Callable,
                        on_export: Callable, on_exit: Callable):
        """Показать меню файла"""
        menu = ctk.CTkToplevel(self.parent)
        menu.overrideredirect(True)
        menu.configure(fg_color="white")
        
        menu_frame = ctk.CTkFrame(
            menu,
            fg_color="white",
            border_width=1,
            border_color="#d0d0d0"
        )
        menu_frame.pack(fill="both", expand=True)
        
        # Пункты меню
        self._create_menu_item(menu_frame, "💾 Сохранить", on_save, menu)
        self._create_menu_item(menu_frame, "📂 Открыть...", on_load, menu)
        
        # Разделитель
        separator = ctk.CTkFrame(menu_frame, height=1, fg_color="#e0e0e0")
        separator.pack(fill="x", padx=5, pady=2)
        
        self._create_menu_item(menu_frame, "📊 Экспорт в Excel...", on_export, menu)
        
        # Разделитель
        separator2 = ctk.CTkFrame(menu_frame, height=1, fg_color="#e0e0e0")
        separator2.pack(fill="x", padx=5, pady=2)
        
        self._create_menu_item(menu_frame, "❌ Выход", on_exit, menu)
        
        # Позиционирование меню
        x = self.parent.winfo_rootx() + 10
        y = self.parent.winfo_rooty() + 50
        menu.geometry(f"+{x}+{y}")
        
        # Закрытие при потере фокуса
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

        # Автоматическое скрытие
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

        # Привязка правой кнопки мыши
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
        # Закрыть предыдущее меню
        self.close_current_menu()

        # Выбираем строку под курсором
        row_id = self.tree.identify_row(event.y)
        if not row_id:
            return

        self.tree.selection_set(row_id)

        # Создаем новое меню
        menu = ctk.CTkToplevel(self.parent)
        menu.overrideredirect(True)
        menu.configure(fg_color="white")
        self.current_menu = menu

        menu_frame = ctk.CTkFrame(
            menu,
            fg_color="white",
            border_width=1,
            border_color="#d0d0d0"
        )
        menu_frame.pack(fill="both", expand=True)

        # Кнопки меню
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

        # Разделитель
        separator = ctk.CTkFrame(menu_frame, height=1, fg_color="#e0e0e0")
        separator.pack(fill="x", padx=5, pady=2)

        self._create_menu_button(
            menu_frame,
            "🗑️ Удалить (Delete)",
            self.on_delete,
            text_color="#dc3545",
            hover_color="#ffebee"
        )

        # Позиционирование меню
        menu.geometry(f"+{event.x_root}+{event.y_root}")

        # Закрытие меню при потере фокуса
        menu.bind('<FocusOut>', lambda e: self.close_current_menu())
        
        # Закрытие при клике вне меню
        def handle_outside_click(e):
            # Проверяем, что клик был не по меню
            widget = e.widget
            try:
                if str(widget).startswith(str(menu)):
                    return
            except:
                pass
            self.close_current_menu()
        
        # Привязываем с небольшой задержкой
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
    """Представление таблицы задач"""

    def __init__(self, parent_frame, on_dependency_click: Callable,
                 on_edit: Callable):
        self.on_dependency_click = on_dependency_click
        self.on_edit = on_edit
        self.processing_click = False

        # Настройка стилей Treeview
        self._configure_styles()

        # Фрейм для таблицы с прокруткой
        tree_frame = ctk.CTkFrame(parent_frame, fg_color="white")
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")

        # Treeview
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

        # Настройка колонок
        column_widths = [120, 150, 130, 140, 100, 200, 150]
        for col, width in zip(columns, column_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")

        self.tree.pack(fill="both", expand=True)

        # Привязка событий - ВАЖНО: перехватываем ДО стандартной обработки
        self.tree.bind('<Button-1>', self._on_button_press, add='+')
        self.tree.bind('<Double-Button-1>', self._on_double_click, add='+')

    def _configure_styles(self):
        """Настройка стилей"""
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

        style.map('Treeview',
                  background=[('selected', '#e3f2fd')],
                  foreground=[('selected', '#000000')])

    def _on_button_press(self, event):
        """Обработка нажатия кнопки мыши"""
        if self.processing_click:
            return "break"
        
        self.processing_click = True
        
        try:
            # Определяем, куда кликнули
            region = self.tree.identify_region(event.x, event.y)
            row_id = self.tree.identify_row(event.y)
            column = self.tree.identify_column(event.x)
            
            # Если клик по колонке "Зависит от" (#6)
            if region == "cell" and row_id and column == "#6":
                # Выбираем строку
                self.tree.selection_set(row_id)
                self.tree.focus(row_id)
                # Открываем диалог зависимостей
                self.tree.after(10, lambda: self.on_dependency_click(event, row_id))
                return "break"  # Прерываем стандартную обработку
            
            # Для остальных случаев позволяем стандартную обработку
            # (выбор строки, снятие выделения при клике на пустое место)
            
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
        
        # Если двойной клик по колонке "Зависит от", ничего не делаем
        if column == "#6":
            return "break"

        # Для остальных колонок - открываем редактирование
        self.tree.selection_set(row_id)
        self.tree.after(10, lambda: self.on_edit(event))
        return "break"

    def populate(self, tasks: List[Task]):
        """Заполнить таблицу данными"""
        # Сохраняем текущее выделение
        current_selection = self.tree.selection()
        selected_index = None
        if current_selection:
            try:
                selected_index = self.tree.index(current_selection[0])
            except:
                pass

        # Очистка существующих данных
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Добавление задач
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

        # Восстанавливаем выделение, если возможно
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
    """Контейнер таблицы с заголовком"""

    def __init__(self, parent, on_add_task: Callable):
        self.container = ctk.CTkFrame(
            parent,
            fg_color="white",
            corner_radius=10
        )
        self.container.pack(fill="both", expand=True, padx=30, pady=20)

        # Заголовок таблицы и кнопка
        table_header = ctk.CTkFrame(self.container, fg_color="transparent")
        table_header.pack(fill="x", padx=20, pady=(20, 10))

        table_title = ctk.CTkLabel(
            table_header,
            text="Таблица задач",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        table_title.pack(side="left")

        add_button = ctk.CTkButton(
            table_header,
            text="+ Добавить задачу",
            font=ctk.CTkFont(size=13),
            height=35,
            corner_radius=8,
            command=on_add_task
        )
        add_button.pack(side="right")