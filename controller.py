"""
Контроллер приложения - паттерн MVC
"""
from typing import Optional
from models import Task, TaskManager
from dialogs import DialogFactory
from views import (TaskTableView, NotificationView, ContextMenuView,
                  HeaderView, TabsView, TableContainerView, MenuBarView)
from storage import DataStorage, ExcelExporter, AutoSaveManager


class TaskController:
    """Контроллер для управления задачами - паттерн Command"""

    def __init__(self, task_manager: TaskManager, table_view: TaskTableView,
                 notification_view: NotificationView, parent):
        self.task_manager = task_manager
        self.table_view = table_view
        self.notification_view = notification_view
        self.parent = parent
        self.clipboard_task: Optional[Task] = None
        self.dependency_popup_open = False
        self.current_dependency_dialog = None

        # Привязка обработчиков событий
        self._bind_events()

    def _bind_events(self):
        """Привязать обработчики событий"""
        self.table_view.bind_delete(self._on_delete_key)
        self.table_view.bind_copy(self._on_copy_key)
        self.table_view.bind_paste(self._on_paste_key)

    def refresh_view(self):
        """Обновить представление"""
        tasks = self.task_manager.get_all_tasks()
        self.table_view.populate(tasks)

    def add_task(self):
        """Добавить задачу"""
        DialogFactory.create_add_task_dialog(
            self.parent,
            self._handle_add_task
        )

    def _handle_add_task(self, task: Task) -> bool:
        """Обработать добавление задачи"""
        # Правило 2: если это первая задача, то она не должна иметь зависимостей,
        # а тип зависимости должен быть '--' (или 'None')
        if len(self.task_manager) == 0:
            task.dependencies = []
            task.type = "--"

        if self.task_manager.add_task(task):
            self.refresh_view()
            self.notification_view.show(f"✅ Задача {task.id} добавлена")
            return True
        else:
            return False

    def edit_task(self, event=None):
        """Редактировать задачу"""
        index = self.table_view.get_selected_index()
        if index is None:
            return

        task = self.task_manager.get_task_by_index(index)
        if task:
            DialogFactory.create_edit_task_dialog(
                self.parent,
                task,
                index,
                self._handle_edit_task
            )

    def _handle_edit_task(self, index: int, updated_task: Task) -> bool:
        """Обработать редактирование задачи"""
        old_task = self.task_manager.get_task_by_index(index)

        # Проверка уникальности ID
        if updated_task.id != old_task.id:
            if self.task_manager.get_task_by_id(updated_task.id):
                return False

        # Правило 1: если у задачи есть зависимости, дата начала не может
        # совпадать с датой начала любой задачи, от которой она зависит
        if updated_task.dependencies:
            for dep_label in updated_task.dependencies:
                # Ожидаемый формат зависит от UI: "ID - Object"
                dep_id = dep_label.split(" - ")[0].strip() if dep_label else ""
                dep_task = self.task_manager.get_task_by_id(dep_id)
                if dep_task and dep_task.start_date == updated_task.start_date:
                    self.notification_view.show(
                        f"❌ Дата начала совпадает с зависимостью: {dep_id}"
                    )
                    return False

        if self.task_manager.update_task(index, updated_task):
            self.refresh_view()
            self.notification_view.show(f"✅ Задача {updated_task.id} обновлена")
            return True
        return False

    def delete_task(self):
        """Удалить задачу"""
        index = self.table_view.get_selected_index()
        if index is None:
            return

        task = self.task_manager.get_task_by_index(index)
        if task:
            DialogFactory.create_delete_confirmation_dialog(
                self.parent,
                task,
                lambda: self._handle_delete_task(index, task.id)
            )

    def _handle_delete_task(self, index: int, task_id: str):
        """Обработать удаление задачи"""
        if self.task_manager.remove_task_by_index(index):
            self.refresh_view()
            self.notification_view.show(f"✅ Задача {task_id} удалена")
        else:
            self.notification_view.show(f"❌ Ошибка при удалении задачи")

    def _on_delete_key(self, event):
        """Обработка клавиши Delete"""
        self.delete_task()

    def copy_task(self):
        """Копировать задачу"""
        index = self.table_view.get_selected_index()
        if index is None:
            return

        task = self.task_manager.get_task_by_index(index)
        if task:
            # Создаем копию задачи
            self.clipboard_task = Task(
                id=task.id,
                object=task.object,
                start_date=task.start_date,
                end_date=task.end_date,
                duration=task.duration,
                dependencies=task.dependencies.copy(),
                type=task.type
            )
            self.notification_view.show("✅ Задача скопирована в буфер обмена")

    def _on_copy_key(self, event):
        """Обработка Ctrl+C"""
        self.copy_task()

    def paste_task(self):
        """Вставить задачу из буфера"""
        if not self.clipboard_task:
            self.notification_view.show("⚠️ Буфер обмена пуст")
            return

        # Создаем новую задачу на основе скопированной
        base_id = self.clipboard_task.id
        counter = 1
        new_id = f"{base_id}-copy"

        # Проверяем уникальность ID
        while self.task_manager.get_task_by_id(new_id):
            counter += 1
            new_id = f"{base_id}-copy{counter}"

        new_task = Task(
            id=new_id,
            object=f"{self.clipboard_task.object} (копия)",
            start_date=self.clipboard_task.start_date,
            end_date=self.clipboard_task.end_date,
            duration=self.clipboard_task.duration,
            dependencies=self.clipboard_task.dependencies.copy(),
            type=self.clipboard_task.type
        )

        self.task_manager.add_task(new_task)
        self.refresh_view()
        self.notification_view.show(f"✅ Задача вставлена: {new_id}")

    def _on_paste_key(self, event):
        """Обработка Ctrl+V"""
        self.paste_task()

    def show_dependency_dialog(self, event, row_id):
        """Показать диалог выбора зависимостей"""
        # ВАЖНО: Сначала проверяем и закрываем предыдущий диалог
        if self.dependency_popup_open or self.current_dependency_dialog:
            print("DEBUG: Диалог уже открыт, закрываем...")
            self._force_close_dependency_dialog()
            return

        print("DEBUG: Открываем диалог зависимостей")
        self.dependency_popup_open = True

        # Получаем индекс строки
        try:
            row_index = self.table_view.tree.index(row_id)
        except:
            print("DEBUG: Ошибка получения индекса строки")
            self.dependency_popup_open = False
            return

        current_task = self.task_manager.get_task_by_index(row_index)

        if not current_task:
            print("DEBUG: Задача не найдена")
            self.dependency_popup_open = False
            return

        # Получаем доступные задачи
        available_tasks = self.task_manager.get_available_dependencies(
            current_task.id
        )

        # Создаем callback для сохранения
        def save_callback(deps):
            print("DEBUG: Вызван save_callback")
            self._handle_save_dependencies(row_index, deps)

        # Создаем callback для закрытия
        def close_callback():
            print("DEBUG: Вызван close_callback (отмена)")
            self._force_close_dependency_dialog()

        # Создаем диалог с передачей callback для закрытия
        dialog = DialogFactory.create_dependency_dialog(
            self.parent,
            current_task,
            available_tasks,
            save_callback,
            close_callback  # Передаем callback для отмены
        )
        
        self.current_dependency_dialog = dialog

        # Позиционируем рядом с курсором
        try:
            x = self.parent.winfo_x() + event.x + 50
            y = self.parent.winfo_y() + event.y - 50
            dialog.geometry(f"+{x}+{y}")
        except:
            pass

        # Обработка закрытия через X
        dialog.protocol("WM_DELETE_WINDOW", close_callback)

    def _handle_save_dependencies(self, index: int, dependencies: list):
        """Обработать сохранение зависимостей"""
        print(f"DEBUG: Сохранение зависимостей для задачи с индексом {index}")
        task = self.task_manager.get_task_by_index(index)
        if task:
            # Проверка на совпадение даты начала с любой из выбранных зависимостей
            for dep_label in dependencies:
                dep_id = dep_label.split(" - ")[0].strip() if dep_label else ""
                dep_task = self.task_manager.get_task_by_id(dep_id)
                if dep_task and dep_task.start_date == task.start_date:
                    self.notification_view.show(
                        f"❌ Нельзя выбрать зависимость с такой же датой начала: {dep_id}"
                    )
                    self._force_close_dependency_dialog()
                    return

            task.dependencies = dependencies
            self.refresh_view()
        
        self._force_close_dependency_dialog()

    def _force_close_dependency_dialog(self):
        """Принудительно закрыть диалог зависимостей"""
        print("DEBUG: Принудительное закрытие диалога")
        
        # Сначала сбрасываем флаг
        self.dependency_popup_open = False
        
        # Затем закрываем диалог
        if self.current_dependency_dialog:
            try:
                self.current_dependency_dialog.destroy()
            except Exception as e:
                print(f"DEBUG: Ошибка при закрытии диалога: {e}")
            finally:
                self.current_dependency_dialog = None
        
        print(f"DEBUG: Флаг dependency_popup_open = {self.dependency_popup_open}")

    def has_clipboard(self) -> bool:
        """Проверить наличие задачи в буфере"""
        return self.clipboard_task is not None


class ApplicationController:
    """Главный контроллер приложения"""

    def __init__(self, parent):
        self.parent = parent

        # Создаем менеджер задач
        self.task_manager = TaskManager()

        # Инициализация хранилища данных
        self.storage = DataStorage()
        
        # Менеджер автосохранения
        self.auto_save_manager = AutoSaveManager(self.task_manager, self.storage)

        # Создаем представления
        self._create_views()

        # Создаем контроллер задач
        self.task_controller = TaskController(
            self.task_manager,
            self.table_view,
            self.notification_view,
            self.parent
        )

        # Создаем контекстное меню
        self.context_menu = ContextMenuView(
            self.parent,
            self.table_view.tree,
            self.task_controller.copy_task,
            self.task_controller.edit_task,
            self.task_controller.paste_task,
            self.task_controller.delete_task,
            self.task_controller.has_clipboard
        )
        
        # Загружаем данные при запуске
        self._load_data_on_startup()
        
        # Запускаем автосохранение
        self.auto_save_manager.start(self.parent)

    def _create_views(self):
        """Создать представления"""
        # Меню
        self.menu_bar = MenuBarView(
            self.parent,
            on_save=self.save_data,
            on_load=self.load_data,
            on_export=self.export_to_excel,
            on_exit=self.on_exit
        )
        
        # Заголовок
        self.header_view = HeaderView(self.parent)

        # Вкладки
        self.tabs_view = TabsView(self.parent)

        # Контейнер таблицы
        self.table_container = TableContainerView(
            self.parent,
            lambda: self.task_controller.add_task()
        )

        # Таблица задач
        self.table_view = TaskTableView(
            self.table_container.container,
            lambda event, row_id: self.task_controller.show_dependency_dialog(
                event, row_id
            ),
            lambda event: self.task_controller.edit_task(event)
        )

        # Уведомления
        self.notification_view = NotificationView(self.parent)

    def _load_data_on_startup(self):
        """Загрузить данные при запуске"""
        if self.storage.file_exists():
            tasks = self.storage.load_tasks()
            if tasks:
                for task in tasks:
                    self.task_manager.add_task(task)
                self.refresh()
                self.notification_view.show(f"✅ Загружено задач: {len(tasks)}")

    def save_data(self):
        """Сохранить данные"""
        tasks = self.task_manager.get_all_tasks()
        if self.storage.save_tasks(tasks):
            self.notification_view.show("✅ Данные сохранены")
        else:
            self.notification_view.show("❌ Ошибка при сохранении данных")

    def load_data(self):
        """Загрузить данные из файла"""
        from tkinter import filedialog
        
        filename = filedialog.askopenfilename(
            title="Загрузить проект",
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")],
            defaultextension=".json"
        )
        
        if not filename:
            return
        
        try:
            storage = DataStorage(filename)
            tasks = storage.load_tasks()
            
            if tasks:
                # Очищаем текущие задачи
                self.task_manager.clear_all()
                
                # Добавляем загруженные
                for task in tasks:
                    self.task_manager.add_task(task)
                
                self.refresh()
                self.notification_view.show(f"✅ Загружено задач: {len(tasks)}")
            else:
                self.notification_view.show("⚠️ Файл пуст или поврежден")
        except Exception as e:
            self.notification_view.show(f"❌ Ошибка загрузки: {str(e)}")

    def export_to_excel(self):
        """Экспортировать данные в Excel"""
        from tkinter import filedialog
        
        tasks = self.task_manager.get_all_tasks()
        
        if not tasks:
            self.notification_view.show("⚠️ Нет задач для экспорта")
            return
        
        # Выбор файла для сохранения
        filename = filedialog.asksaveasfilename(
            title="Экспорт в Excel",
            defaultextension=".xlsx",
            filetypes=[("Excel файлы", "*.xlsx"), ("Все файлы", "*.*")]
        )
        
        if not filename:
            return
        
        success, message = ExcelExporter.export_to_excel(tasks, filename)
        
        if success:
            self.notification_view.show("✅ " + message, duration=3000)
        else:
            self.notification_view.show("❌ " + message, duration=3000)

    def on_exit(self):
        """Обработка выхода из приложения"""
        # Сохраняем данные перед выходом
        self.auto_save_manager.save_now()
        self.auto_save_manager.stop()
        self.parent.quit()

    def refresh(self):
        """Обновить все представления"""
        self.task_controller.refresh_view()