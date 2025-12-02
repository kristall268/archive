"""
Контроллер приложения с поддержкой фильтрации.
"""
from typing import Optional
from datetime import datetime
from models import Task, TaskManager
from dialogs import DialogFactory
from views import (TaskTableView, NotificationView, ContextMenuView,
                  HeaderView, TabsView, TableContainerView, MenuBarView,
                  FilterPanelView)
from storage import DataStorage, ExcelExporter, AutoSaveManager


class TaskController:
    """Контроллер для управления задачами"""

    def __init__(self, task_manager: TaskManager, table_view: TaskTableView,
                 notification_view: NotificationView, parent):
        self.task_manager = task_manager
        self.table_view = table_view
        self.notification_view = notification_view
        self.parent = parent
        self.clipboard_task: Optional[Task] = None
        self.dependency_popup_open = False
        self.current_dependency_dialog = None
        
        # Фильтры
        self.current_filters = {}
        self.all_tasks = []

        self._bind_events()

    def _bind_events(self):
        """Привязать обработчики событий"""
        self.table_view.bind_delete(self._on_delete_key)
        self.table_view.bind_copy(self._on_copy_key)
        self.table_view.bind_paste(self._on_paste_key)

    def set_filters(self, filters: dict):
        """Установить фильтры и обновить представление"""
        self.current_filters = filters
        self.refresh_view()

    def _apply_filters(self, tasks: list) -> list:
        """Применить фильтры к списку задач"""
        if not self.current_filters:
            return tasks
        
        filtered_tasks = tasks.copy()
        
        # Фильтр поиска
        search_text = self.current_filters.get('search', '')
        if search_text:
            filtered_tasks = [
                task for task in filtered_tasks
                if search_text in task.id.lower() or search_text in task.object.lower()
            ]
        
        # Фильтр по типу зависимости
        dep_type = self.current_filters.get('type', 'Все')
        if dep_type != 'Все':
            if dep_type == 'Без типа':
                filtered_tasks = [
                    task for task in filtered_tasks
                    if not task.type or task.type in ['', '--']
                ]
            else:
                filtered_tasks = [
                    task for task in filtered_tasks
                    if task.type == dep_type
                ]
        
        # Фильтр по количеству зависимостей
        deps_filter = self.current_filters.get('dependencies', 'Все')
        if deps_filter != 'Все':
            if deps_filter == 'Без зависимостей':
                filtered_tasks = [
                    task for task in filtered_tasks
                    if not task.dependencies
                ]
            elif deps_filter == 'С зависимостями':
                filtered_tasks = [
                    task for task in filtered_tasks
                    if task.dependencies
                ]
            elif deps_filter == '1 зависимость':
                filtered_tasks = [
                    task for task in filtered_tasks
                    if len(task.dependencies) == 1
                ]
            elif deps_filter == '2+ зависимости':
                filtered_tasks = [
                    task for task in filtered_tasks
                    if len(task.dependencies) >= 2
                ]
        
        # Фильтр по датам
        if self.current_filters.get('date_enabled', False):
            start_date_str = self.current_filters.get('start_date')
            end_date_str = self.current_filters.get('end_date')
            
            if start_date_str and end_date_str:
                try:
                    filter_start = datetime.strptime(start_date_str, "%d.%m.%Y")
                    filter_end = datetime.strptime(end_date_str, "%d.%m.%Y")
                    
                    filtered_tasks = [
                        task for task in filtered_tasks
                        if self._task_in_date_range(task, filter_start, filter_end)
                    ]
                except:
                    pass
        
        return filtered_tasks

    def _task_in_date_range(self, task: Task, filter_start: datetime, 
                           filter_end: datetime) -> bool:
        """Проверить, попадает ли задача в диапазон дат"""
        try:
            task_start = datetime.strptime(task.start_date, "%d.%m.%Y")
            task_end = datetime.strptime(task.end_date, "%d.%m.%Y")
            
            # Задача попадает в диапазон, если есть пересечение
            return not (task_end < filter_start or task_start > filter_end)
        except:
            return False

    def refresh_view(self):
        """Обновить представление с учетом фильтров"""
        all_tasks = self.task_manager.get_all_tasks()
        self.all_tasks = all_tasks
        
        # Применяем фильтры
        filtered_tasks = self._apply_filters(all_tasks)
        
        self.table_view.populate(filtered_tasks)

    def add_task(self):
        """Добавить задачу"""
        DialogFactory.create_add_task_dialog(
            self.parent,
            self._handle_add_task
        )

    def _handle_add_task(self, task: Task) -> bool:
        """Обработать добавление задачи"""
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

        # Получаем задачу из отфильтрованного списка
        filtered_tasks = self._apply_filters(self.all_tasks)
        if index >= len(filtered_tasks):
            return
        
        task = filtered_tasks[index]
        
        # Находим реальный индекс в полном списке
        real_index = None
        for i, t in enumerate(self.all_tasks):
            if t.id == task.id:
                real_index = i
                break
        
        if real_index is None:
            return

        DialogFactory.create_edit_task_dialog(
            self.parent,
            task,
            real_index,
            self._handle_edit_task
        )

    def _handle_edit_task(self, index: int, updated_task: Task) -> bool:
        """Обработать редактирование задачи"""
        old_task = self.task_manager.get_task_by_index(index)

        if updated_task.id != old_task.id:
            if self.task_manager.get_task_by_id(updated_task.id):
                return False

        if updated_task.dependencies:
            for dep_label in updated_task.dependencies:
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

        # Получаем задачу из отфильтрованного списка
        filtered_tasks = self._apply_filters(self.all_tasks)
        if index >= len(filtered_tasks):
            return
        
        task = filtered_tasks[index]
        
        # Находим реальный индекс
        real_index = None
        for i, t in enumerate(self.all_tasks):
            if t.id == task.id:
                real_index = i
                break
        
        if real_index is None:
            return

        DialogFactory.create_delete_confirmation_dialog(
            self.parent,
            task,
            lambda: self._handle_delete_task(real_index, task.id)
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

        filtered_tasks = self._apply_filters(self.all_tasks)
        if index >= len(filtered_tasks):
            return
        
        task = filtered_tasks[index]

        if task:
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

        base_id = self.clipboard_task.id
        counter = 1
        new_id = f"{base_id}-copy"

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
        if self.dependency_popup_open or self.current_dependency_dialog:
            self._force_close_dependency_dialog()
            return

        self.dependency_popup_open = True

        try:
            row_index = self.table_view.tree.index(row_id)
        except:
            self.dependency_popup_open = False
            return

        # Получаем задачу из отфильтрованного списка
        filtered_tasks = self._apply_filters(self.all_tasks)
        if row_index >= len(filtered_tasks):
            self.dependency_popup_open = False
            return
        
        current_task = filtered_tasks[row_index]

        if not current_task:
            self.dependency_popup_open = False
            return

        # Находим реальный индекс
        real_index = None
        for i, t in enumerate(self.all_tasks):
            if t.id == current_task.id:
                real_index = i
                break

        if real_index is None:
            self.dependency_popup_open = False
            return

        available_tasks = self.task_manager.get_available_dependencies(
            current_task.id
        )

        def save_callback(deps):
            self._handle_save_dependencies(real_index, deps)

        def close_callback():
            self._force_close_dependency_dialog()

        dialog = DialogFactory.create_dependency_dialog(
            self.parent,
            current_task,
            available_tasks,
            save_callback,
            close_callback
        )
        
        self.current_dependency_dialog = dialog

        try:
            x = self.parent.winfo_x() + event.x + 50
            y = self.parent.winfo_y() + event.y - 50
            dialog.geometry(f"+{x}+{y}")
        except:
            pass

        dialog.protocol("WM_DELETE_WINDOW", close_callback)

    def _handle_save_dependencies(self, index: int, dependencies: list):
        """Обработать сохранение зависимостей"""
        task = self.task_manager.get_task_by_index(index)
        if task:
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
        self.dependency_popup_open = False
        
        if self.current_dependency_dialog:
            try:
                self.current_dependency_dialog.destroy()
            except:
                pass
            finally:
                self.current_dependency_dialog = None

    def has_clipboard(self) -> bool:
        """Проверить наличие задачи в буфере"""
        return self.clipboard_task is not None


class ApplicationController:
    """Главный контроллер приложения"""

    def __init__(self, parent):
        self.parent = parent

        self.task_manager = TaskManager()
        self.storage = DataStorage()
        self.auto_save_manager = AutoSaveManager(self.task_manager, self.storage)

        self._create_views()

        self.task_controller = TaskController(
            self.task_manager,
            self.table_view,
            self.notification_view,
            self.parent
        )

        self.context_menu = ContextMenuView(
            self.parent,
            self.table_view.tree,
            self.task_controller.copy_task,
            self.task_controller.edit_task,
            self.task_controller.paste_task,
            self.task_controller.delete_task,
            self.task_controller.has_clipboard
        )
        
        self._load_data_on_startup()
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
        
        self.header_view = HeaderView(self.parent)
        self.tabs_view = TabsView(self.parent)

        # Контейнер таблицы с меню
        self.table_container = TableContainerView(
            self.parent,
            lambda: self.task_controller.add_task(),
            self.menu_bar
        )

        # Панель фильтрации
        self.filter_panel = FilterPanelView(
            self.table_container.container,
            self._on_filter_change
        )

        # Таблица задач
        self.table_view = TaskTableView(
            self.table_container.container,
            lambda event, row_id: self.task_controller.show_dependency_dialog(
                event, row_id
            ),
            lambda event: self.task_controller.edit_task(event)
        )

        self.notification_view = NotificationView(self.parent)

    def _on_filter_change(self):
        """Обработка изменения фильтров"""
        filters = self.filter_panel.get_filters()
        self.task_controller.set_filters(filters)

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
                self.task_manager.clear_all()
                
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
        self.auto_save_manager.save_now()
        self.auto_save_manager.stop()
        self.parent.quit()

    def refresh(self):
        """Обновить все представления"""
        self.task_controller.refresh_view()