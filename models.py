"""
Модели данных для приложения управления проектами
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Task:
    """Модель задачи проекта"""
    id: str
    object: str
    start_date: str
    end_date: str
    duration: int = 0
    dependencies: List[str] = field(default_factory=list)
    type: str = ""

    def __post_init__(self):
        """Вычисление длительности после инициализации"""
        if self.duration == 0:
            self.duration = self.calculate_duration()

    def calculate_duration(self) -> int:
        """Вычисление длительности между двумя датами"""
        try:
            start = datetime.strptime(self.start_date, "%d.%m.%Y")
            end = datetime.strptime(self.end_date, "%d.%m.%Y")
            duration = (end - start).days + 1
            return max(0, duration)
        except Exception:
            return 0

    def to_dict(self) -> dict:
        """Конвертация в словарь"""
        return {
            "id": self.id,
            "object": self.object,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "duration": self.duration,
            "dependencies": self.dependencies,
            "type": self.type
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """Создание из словаря"""
        return cls(**data)

    def add_dependency(self, dependency: str):
        """Добавить зависимость"""
        if dependency not in self.dependencies:
            self.dependencies.append(dependency)

    def remove_dependency(self, dependency: str):
        """Удалить зависимость"""
        if dependency in self.dependencies:
            self.dependencies.remove(dependency)

    def get_dependency_text(self) -> str:
        """Получить текст зависимостей для отображения"""
        if not self.dependencies:
            return "Выберите задачу"
        elif len(self.dependencies) == 1:
            return self.dependencies[0]
        else:
            return "\n".join(self.dependencies)


class TaskManager:
    """Менеджер задач - паттерн Repository"""

    def __init__(self):
        self._tasks: List[Task] = []

    def add_task(self, task: Task) -> bool:
        """Добавить задачу"""
        if self.get_task_by_id(task.id):
            return False
        self._tasks.append(task)
        return True

    def remove_task(self, task_id: str) -> bool:
        """Удалить задачу по ID"""
        task = self.get_task_by_id(task_id)
        if task:
            self._tasks.remove(task)
            return True
        return False

    def remove_task_by_index(self, index: int) -> bool:
        """Удалить задачу по индексу"""
        if 0 <= index < len(self._tasks):
            self._tasks.pop(index)
            return True
        return False

    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Получить задачу по ID"""
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None

    def get_task_by_index(self, index: int) -> Optional[Task]:
        """Получить задачу по индексу"""
        if 0 <= index < len(self._tasks):
            return self._tasks[index]
        return None

    def update_task(self, index: int, updated_task: Task) -> bool:
        """Обновить задачу по индексу"""
        if 0 <= index < len(self._tasks):
            self._tasks[index] = updated_task
            return True
        return False

    def get_all_tasks(self) -> List[Task]:
        """Получить все задачи"""
        return self._tasks.copy()

    def get_available_dependencies(self, task_id: str) -> List[Task]:
        """Получить доступные задачи для зависимостей"""
        return [task for task in self._tasks if task.id != task_id]

    def clear_all(self):
        """Очистить все задачи"""
        self._tasks.clear()

    def __len__(self):
        return len(self._tasks)