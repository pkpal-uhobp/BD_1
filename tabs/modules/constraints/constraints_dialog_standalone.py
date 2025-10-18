from PySide6.QtWidgets import QDialog
from tabs.modules.table_operations import ConstraintsDialog


class ConstraintsDialogStandalone(ConstraintsDialog):
    """Отдельное окно для наложения ограничений на существующий столбец.
    PK и FK намеренно скрыты/отключены по требованию.
    """

    def __init__(self, db_instance, parent=None):
        super().__init__(db_instance, parent)
        # Отключаем PK/FK для существующих столбцов
        self.pk_check.setChecked(False)
        self.pk_check.setEnabled(False)
        self.fk_check.setChecked(False)
        self.fk_check.setEnabled(False)
        self.ref_table.setEnabled(False)
        self.ref_column.setEnabled(False)


