"""
Главный файл приложения управления проектами
Рефакторинг с применением паттернов:
- MVC (Model-View-Controller)
- Repository (TaskManager)
- Factory (DialogFactory)
- Observer (для обновления представлений)
"""
import customtkinter as ctk
from controller import ApplicationController

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class ProjectManagementApp(ctk.CTk):
    """Главное окно приложения"""

    def __init__(self):
        super().__init__()

        self.title("Управление проектом")
        self.geometry("1400x700")

        # Создаем главный контроллер
        self.app_controller = ApplicationController(self)

        # Обработка закрытия окна
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Инициализация данных (опционально)
        self._load_sample_data()

    def _load_sample_data(self):
        """Загрузить тестовые данные (опционально)"""
        # Здесь можно добавить загрузку из файла или базы данных
        pass

    def _on_closing(self):
        """Обработка закрытия окна"""
        # Сохраняем данные через контроллер
        self.app_controller.on_exit()


def main():
    """Точка входа в приложение"""
    app = ProjectManagementApp()
    app.mainloop()


if __name__ == "__main__":
    main()