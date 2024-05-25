from pydantic import BaseModel
from typing import List
from datetime import datetime

class UniversityData(BaseModel):
    id: int
    date: str
    url: str
    university_name: str
    title: str
    content: str
    # "id": 9,
    # "date": "2024-05-21T10:57:25.733783",
    # "url": "https://www.stanford.edu/admission/",
    # "university_name": "Stanford University",
    # "title": "Search Stanford:",
    # "content":