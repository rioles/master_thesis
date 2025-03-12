#!/usr/bin/env python3
"""Simple pagination"""
from math import ceil
from typing import Any, Dict, List, Iterable
from typing import Optional


def index_range(page: int, page_size: int) -> tuple:
    """return a tuple of size two containing a start index and an end index"""
    start = (page - 1) * page_size
    return (start, start + page_size)


class Paginator:
    """Paginator class to paginate a database.
    """

    def __init__(self, dataset: List[Iterable[Any]]):
        self.dataset = dataset
        
    
    def get_page(self, page: int = 1, page_size: int = 10) -> List[Dict[str, Any]]:
        """finds the correct indexes to paginate the dataset \
            correctly and return the appropriate page of the dataset
        """
        assert type(page) == int and type(page_size) == int
        assert page > 0 and page_size > 0
        start, end = index_range(page, page_size)

        if start >= len(self.dataset):
            return []  # Return an empty list if start index is beyond the dataset
        else:
            return self.dataset[start:end if end <= len(self.dataset) else min(end, len(self.dataset))]

        
    def get_hyper( self, page: int = 1, page_size: int = 10, extra_info: Optional[Any] = None, key_name:Optional[str] = "extra_info") -> dict:
        """returns an hypermedia object based on self.get_page result"""
        page_data = self.get_page(page, page_size)
        print(page_data)
        total_pages = ceil(len(self.dataset) / page_size)
        next_page = page + 1 if page + 1 <= total_pages else None
        prev_page = page - 1 if page - 1 >= 1 else None
        
        hypermedia_obj = {
            "page_size": len(page_data),
            "page": page,
            "data": page_data,
            "next_page": next_page,
            "prev_page": prev_page,
            "total_pages": total_pages
        }
        
        if extra_info is not None:
            hypermedia_obj[key_name] = extra_info
        return hypermedia_obj
    
