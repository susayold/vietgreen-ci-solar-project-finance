from openpyxl.cell.cell import MergedCell
from openpyxl.utils import get_column_letter

# The classic builder uses worksheet cells to derive column letters. Banner rows
# are merged across the model width, so openpyxl returns MergedCell objects for
# those coordinates. Expose the same column_letter convenience property used by
# normal Cell objects before importing the builder.
if not hasattr(MergedCell, "column_letter"):
    MergedCell.column_letter = property(lambda self: get_column_letter(self.column))

from build_classic_project_finance_workbook import main


if __name__ == "__main__":
    main()
