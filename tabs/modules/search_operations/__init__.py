"""
Диалоги для операций поиска и выборки данных
"""

from .text_search_dialog import TextSearchDialog
from .advanced_select_dialog import AdvancedSelectDialog, AggregateFunctionDialog

__all__ = [
    'TextSearchDialog',
    'AdvancedSelectDialog',
    'AggregateFunctionDialog'
]
