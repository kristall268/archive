"""
Диалоговые окна приложения - паттерн Factory
"""
import customtkinter as ctk
from datetime import datetime
from tkcalendar import DateEntry
from typing import Callable, Optional, List
from models import Task


class DialogFactory:
    """Фабрика для создания диалоговых окон"""

    @staticmethod
    def create_add_task_dialog(parent, on_save: Callable):
        """Создать диалог добавления задачи"""
        return AddTaskDialog(parent, on_save)

    @staticmethod
    def create_edit_task_dialog(parent, task: Task, index: int, on_save: Callable):
        """Создать диалог редактирования задачи"""
        return EditTaskDialog(parent, task, index, on_save)

    @staticmethod
    def create_delete_confirmation_dialog(parent, task: Task, on_confirm: Callable):
        """Создать диалог подтверждения удаления"""
        return DeleteConfirmationDialog(parent, task, on_confirm)

    @staticmethod
    def create_dependency_dialog(parent, task: Task, available_tasks: List[Task],
                                on_save: Callable, on_cancel: Callable = None):
        """Создать диалог выбора зависимостей"""
        return DependencyDialog(parent, task, available_tasks, on_save, on_cancel)


class BaseDialog(ctk.CTkToplevel):
    """Базовый класс для диалогов"""

    def __init__(self, parent, title: str, width: int, height: int):
        super().__init__(parent)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.transient(parent)
        self.update_idletasks()
        self.grab_set()
        self.focus_force()

        self.content = ctk.CTkFrame(self, fg_color="white")
        self.content.pack(fill="both", expand=True, padx=20, pady=20)

    def center_on_screen(self):
        """Центрировать окно на экране"""
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")


class TaskDialog(BaseDialog):
    """Базовый класс для диалогов задач"""

    def __init__(self, parent, title: str, task: Optional[Task] = None):
        super().__init__(parent, title, 550, 700)
        self.task = task
        self.create_widgets()
        self.bind('<Return>', lambda e: self.save())
        self.bind('<Escape>', lambda e: self.destroy())

    def create_widgets(self):
        """Создать виджеты"""
        # Заголовок
        title = ctk.CTkLabel(
            self.content,
            text=self.title(),
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title.pack(pady=(0, 25))

        # ID задачи
        self._create_field_label("ID задачи:", pady=(10, 5))
        self.entry_id = ctk.CTkEntry(
            self.content,
            height=40,
            placeholder_text="Например: WBS-01-13-001",
            font=ctk.CTkFont(size=12)
        )
        self.entry_id.pack(fill="x")
        if self.task:
            self.entry_id.insert(0, self.task.id)
        self.entry_id.focus_set()

        # Объект
        self._create_field_label("Объект:", pady=(15, 5))
        self.entry_object = ctk.CTkEntry(
            self.content,
            height=40,
            placeholder_text="Название объекта работ",
            font=ctk.CTkFont(size=12)
        )
        self.entry_object.pack(fill="x")
        if self.task:
            self.entry_object.insert(0, self.task.object)

        # Даты
        self.date_start = self._create_date_field("Дата начала:",
                                                   self.task.start_date if self.task else None)
        self.date_end = self._create_date_field("Дата окончания:",
                                                self.task.end_date if self.task else None)

        # Длительность
        duration_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        duration_frame.pack(fill="x", pady=(15, 0))

        label_duration = ctk.CTkLabel(
            duration_frame,
            text="Длительность:",
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        label_duration.pack(side="left")

        self.duration_value = ctk.CTkLabel(
            duration_frame,
            text="0 дней",
            font=ctk.CTkFont(size=13),
            text_color="#3B8ED0"
        )
        self.duration_value.pack(side="left", padx=(10, 0))

        # Привязка обновления длительности
        self.date_start.bind("<<DateEntrySelected>>", self._update_duration)
        self.date_end.bind("<<DateEntrySelected>>", self._update_duration)
        self._update_duration()

        # Тип зависимости
        self._create_field_label("Тип зависимости:", pady=(15, 5))
        type_options = ["", "FS - Finish-Start", "SS - Start-Start",
                       "FF - Finish-Finish", "SF - Start-Finish"]
        self.combo_type = ctk.CTkComboBox(
            self.content,
            values=type_options,
            height=40,
            font=ctk.CTkFont(size=12)
        )
        self.combo_type.set(self.task.type if self.task else "")
        self.combo_type.pack(fill="x")

        # Информация о зависимостях
        if self.task and self.task.dependencies:
            dep_info = ctk.CTkLabel(
                self.content,
                text=f"Зависимости: {len(self.task.dependencies)} задач(и)",
                font=ctk.CTkFont(size=11),
                text_color="gray"
            )
            dep_info.pack(pady=(10, 0))

        # Сообщение об ошибке
        self.error_label = ctk.CTkLabel(
            self.content,
            text="",
            text_color="red",
            font=ctk.CTkFont(size=11)
        )
        self.error_label.pack(pady=(10, 0))

        # Кнопки
        self._create_buttons()

    def _create_field_label(self, text: str, pady=(10, 5)):
        """Создать метку поля"""
        label = ctk.CTkLabel(
            self.content,
            text=text,
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        label.pack(fill="x", pady=pady)
        return label

    def _create_date_field(self, label_text: str, date_str: Optional[str]):
        """Создать поле даты"""
        self._create_field_label(label_text, pady=(15, 5))

        date_frame = ctk.CTkFrame(
            self.content,
            fg_color="#f0f0f0",
            height=40,
            corner_radius=6
        )
        date_frame.pack(fill="x")
        date_frame.pack_propagate(False)

        # Парсинг даты
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, "%d.%m.%Y")
            except:
                date_obj = datetime.now()
        else:
            date_obj = datetime.now()

        date_entry = DateEntry(
            date_frame,
            width=30,
            background='#3B8ED0',
            foreground='white',
            borderwidth=0,
            date_pattern='dd.mm.yyyy',
            font=('Segoe UI', 11),
            year=date_obj.year,
            month=date_obj.month,
            day=date_obj.day
        )
        date_entry.pack(fill="both", expand=True, padx=5, pady=5)
        return date_entry

    def _update_duration(self, *args):
        """Обновить длительность"""
        start = self.date_start.get_date().strftime("%d.%m.%Y")
        end = self.date_end.get_date().strftime("%d.%m.%Y")

        try:
            start_dt = datetime.strptime(start, "%d.%m.%Y")
            end_dt = datetime.strptime(end, "%d.%m.%Y")
            duration = (end_dt - start_dt).days + 1
            duration = max(0, duration)
        except:
            duration = 0

        self.duration_value.configure(text=f"{duration} дней")
        return duration

    def _create_buttons(self):
        """Создать кнопки"""
        button_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        button_frame.pack(fill="x", pady=(30, 0))

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Отмена",
            command=self.destroy,
            fg_color="gray",
            hover_color="#666666",
            height=40,
            width=120,
            font=ctk.CTkFont(size=13)
        )
        cancel_btn.pack(side="right")

        save_btn = ctk.CTkButton(
            button_frame,
            text="Сохранить",
            command=self.save,
            height=40,
            width=120,
            font=ctk.CTkFont(size=13)
        )
        save_btn.pack(side="right", padx=(0, 10))

    def get_task_data(self) -> Optional[dict]:
        """Получить данные задачи"""
        task_id = self.entry_id.get().strip()
        task_object = self.entry_object.get().strip()

        if not task_id or not task_object:
            self.error_label.configure(
                text="⚠ Заполните ID задачи и название объекта!"
            )
            return None

        return {
            "id": task_id,
            "object": task_object,
            "start_date": self.date_start.get_date().strftime("%d.%m.%Y"),
            "end_date": self.date_end.get_date().strftime("%d.%m.%Y"),
            "duration": self._update_duration(),
            "type": self.combo_type.get()
        }

    def save(self):
        """Сохранить - должен быть переопределен"""
        raise NotImplementedError


class AddTaskDialog(TaskDialog):
    """Диалог добавления задачи"""

    def __init__(self, parent, on_save: Callable):
        self.on_save_callback = on_save
        super().__init__(parent, "Добавить задачу", None)

    def save(self):
        """Сохранить новую задачу"""
        data = self.get_task_data()
        if data:
            data["dependencies"] = []
            task = Task(**data)
            if self.on_save_callback(task):
                self.destroy()


class EditTaskDialog(TaskDialog):
    """Диалог редактирования задачи"""

    def __init__(self, parent, task: Task, index: int, on_save: Callable):
        self.index = index
        self.on_save_callback = on_save
        super().__init__(parent, "Редактировать задачу", task)

    def save(self):
        """Сохранить изменения"""
        data = self.get_task_data()
        if data:
            data["dependencies"] = self.task.dependencies.copy()
            updated_task = Task(**data)

            if self.on_save_callback(self.index, updated_task):
                self.destroy()
            else:
                self.error_label.configure(
                    text="⚠ Задача с таким ID уже существует!"
                )


class DeleteConfirmationDialog(BaseDialog):
    """Диалог подтверждения удаления"""

    def __init__(self, parent, task: Task, on_confirm: Callable):
        super().__init__(parent, "Подтверждение удаления", 450, 220)
        self.task = task
        self.on_confirm_callback = on_confirm
        self.create_content()
        self.center_on_screen()
        self.bind('<Escape>', lambda e: self.destroy())
        self.bind('<Return>', lambda e: self.confirm())

    def create_content(self):
        """Создать содержимое"""
        # Иконка предупреждения
        warning_label = ctk.CTkLabel(
            self.content,
            text="",
            font=ctk.CTkFont(size=48)
        )
        warning_label.pack(pady=(15, 15))

        # Вопрос
        question_label = ctk.CTkLabel(
            self.content,
            text="Вы уверены, что хотите удалить задачу?",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        question_label.pack(pady=(0, 10))

        # Информация о задаче
        task_info_label = ctk.CTkLabel(
            self.content,
            text=f"{self.task.id} - {self.task.object}",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            wraplength=400
        )
        task_info_label.pack(pady=(0, 25))

        # Кнопки
        button_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 5))

        # Кнопка "Нет"
        no_btn = ctk.CTkButton(
            button_frame,
            text="Нет",
            command=self.destroy,
            fg_color="gray",
            hover_color="#666666",
            height=40,
            width=140,
            font=ctk.CTkFont(size=14)
        )
        no_btn.pack(side="right", padx=(10, 0))

        # Кнопка "Да"
        yes_btn = ctk.CTkButton(
            button_frame,
            text="Да",
            command=self.confirm,
            fg_color="#dc3545",
            hover_color="#c82333",
            height=40,
            width=140,
            font=ctk.CTkFont(size=14)
        )
        yes_btn.pack(side="right")

        # Фокус на кнопке "Нет" (безопасный выбор по умолчанию)
        no_btn.focus_set()

    def confirm(self):
        """Подтвердить удаление"""
        self.on_confirm_callback()
        self.destroy()


class DependencyDialog(BaseDialog):
    """Диалог выбора зависимостей"""

    def __init__(self, parent, task: Task, available_tasks: List[Task],
                 on_save: Callable, on_cancel: Callable = None):
        # Инициализируем атрибуты ДО вызова super().__init__
        self.task = task
        self.available_tasks = available_tasks
        self.on_save_callback = on_save
        self.on_cancel_callback = on_cancel
        self.checkbox_vars = {}
        self.is_closed = False
        
        # Вызываем базовый конструктор
        super().__init__(parent, "Выбор зависимостей", 380, 400)
        
        # Создаем содержимое
        self.create_content()

    def create_content(self):
        """Создать содержимое"""
        # Заголовок
        title_label = ctk.CTkLabel(
            self.content,
            text="Зависимости задачи",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(0, 10))

        info_label = ctk.CTkLabel(
            self.content,
            text=f"Выберите задачи, от которых зависит:\n{self.task.id} - {self.task.object}",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            wraplength=340
        )
        info_label.pack(pady=(0, 15))

        # Список задач
        scroll_frame = ctk.CTkScrollableFrame(
            self.content,
            width=340,
            height=220,
            fg_color="#f8f9fa",
            corner_radius=8
        )
        scroll_frame.pack(fill="both", expand=True, pady=(0, 10))

        if not self.available_tasks:
            no_tasks_label = ctk.CTkLabel(
                scroll_frame,
                text="Нет доступных задач для зависимостей",
                font=ctk.CTkFont(size=12),
                text_color="gray"
            )
            no_tasks_label.pack(pady=20)
        else:
            for task in self.available_tasks:
                task_label = f"{task.id} - {task.object}"
                is_selected = task_label in self.task.dependencies

                checkbox_var = ctk.BooleanVar(value=is_selected)
                self.checkbox_vars[task_label] = checkbox_var

                task_frame = ctk.CTkFrame(
                    scroll_frame,
                    fg_color="white",
                    corner_radius=6
                )
                task_frame.pack(fill="x", padx=8, pady=4)

                checkbox = ctk.CTkCheckBox(
                    task_frame,
                    text=task_label,
                    variable=checkbox_var,
                    font=ctk.CTkFont(size=12),
                    fg_color="#3B8ED0",
                    hover_color="#2E7AB8"
                )
                checkbox.pack(anchor="w", padx=12, pady=10)

        # Кнопки
        self._create_buttons()

    def _create_buttons(self):
        """Создать кнопки"""
        button_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Отмена",
            command=self.cancel,
            fg_color="gray",
            hover_color="#666666",
            height=35,
            width=100,
            font=ctk.CTkFont(size=12)
        )
        cancel_btn.pack(side="right")

        save_btn = ctk.CTkButton(
            button_frame,
            text="Применить",
            command=self.save,
            height=35,
            width=100,
            font=ctk.CTkFont(size=12)
        )
        save_btn.pack(side="right", padx=(0, 10))

    def cancel(self):
        """Отменить изменения"""
        print("DEBUG: DependencyDialog.cancel() вызван")
        if self.is_closed:
            return
        self.is_closed = True
        
        # Вызываем callback отмены
        if self.on_cancel_callback:
            self.on_cancel_callback()
        else:
            # Если callback не передан, просто закрываем
            try:
                super().destroy()
            except:
                pass

    def save(self):
        """Сохранить зависимости"""
        print("DEBUG: DependencyDialog.save() вызван")
        if self.is_closed:
            return
        self.is_closed = True
        
        selected_deps = [
            task_label for task_label, var in self.checkbox_vars.items()
            if var.get()
        ]
        self.on_save_callback(selected_deps)
    
    def destroy(self):
        """Переопределение destroy для предотвращения повторного вызова"""
        if not self.is_closed:
            self.is_closed = True
            if self.on_cancel_callback:
                self.on_cancel_callback()
                return
        try:
            super().destroy()
        except:
            pass