import pytest


@pytest.fixture
def sample_data():
    return [ 
         {
                "id": 1,
                "title": "Test Product",
                "price": 100,
                "description": "Test description",
                "category": "electronics",
                "image": "test.jpg",
                "rating": {
                    "rate": 4.0,
                    "count": 10
                }
            },
            {
                "id": 2,
                "title": "Another Product",
                "price": 50,
                "description": "Another description",
                "category": "books",
                "image": "test2.jpg",
                "rating": {
                    "rate": 3.5,
                    "count": 5
                }
            }
    ]