from typing import Optional

class PaginationParams:
    def __init__(self, page: int = 1, page_size: int = 5, sort_by: Optional[str] = 'ToAddress', sort_order: Optional[str] = 'desc'):
        self.page = page
        self.page_size = page_size
        self.sort_by = sort_by
        self.sort_order = sort_order
