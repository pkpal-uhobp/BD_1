"""
Диалоги для операций с данными (CRUD)
"""

from .add_dialog import AddRecordDialog
from .update_dialog import EditRecordDialog
from .delete_dialog import DeleteRecordDialog
from .get_table import ShowTableDialog

__all__ = [
    'AddRecordDialog',
    'EditRecordDialog', 
    'DeleteRecordDialog',
    'ShowTableDialog'
]
