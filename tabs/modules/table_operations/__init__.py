"""
Диалоги для операций с таблицами и столбцами
"""

from .add_column import AddColumnDialog, ConstraintsDialog
from .drop_column_dialog import DropColumnDialog
from .rename_dialog import RenameDialog
from .change_type_dialog import ChangeTypeDialog

__all__ = [
    'AddColumnDialog',
    'ConstraintsDialog',
    'DropColumnDialog',
    'RenameDialog',
    'ChangeTypeDialog'
]
