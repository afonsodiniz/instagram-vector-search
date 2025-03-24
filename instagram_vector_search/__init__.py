# instagram_vector_search/__init__.py
"""Instagram Vector Search - Semantic search for Instagram content."""
__version__ = "0.1.0"

from .create_mock_data import main as create_data
from .process_data import main as process_data
from .app import main as run_app

