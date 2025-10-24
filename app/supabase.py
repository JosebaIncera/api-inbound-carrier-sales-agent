import os
from dotenv import load_dotenv
import logging

# Set up logger for this module
logger = logging.getLogger(__name__)

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

logger.debug(f"Supabase URL: {SUPABASE_URL}")
logger.debug(f"Supabase Key: {SUPABASE_KEY[:8] if SUPABASE_KEY else 'None'}...")

# Try to create real Supabase client, fallback to mock if it fails
try:
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.warning("Supabase URL or KEY not provided, using mock client")
        raise ImportError("Supabase credentials not provided")
    
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("Real Supabase client initialized successfully")
    
except Exception as e:
    logger.warning(f"Failed to initialize real Supabase client: {str(e)}")
    logger.info("Falling back to mock Supabase client")
    
    # Mock Supabase client for fallback
    class MockSupabaseClient:
        def __init__(self, url, key):
            self.url = url
            self.key = key
            logger.debug("Initialized MockSupabaseClient")
        
        def table(self, table_name):
            logger.debug(f"Accessing table: {table_name}")
            return MockTable(table_name)

    class MockTable:
        def __init__(self, table_name):
            self.table_name = table_name
            logger.debug(f"Initialized MockTable for: {table_name}")
        
        def select(self, columns="*"):
            logger.debug(f"Selecting columns: {columns}")
            return MockQuery(self.table_name, columns)
        
        def insert(self, data):
            logger.debug(f"Inserting data into {self.table_name}: {data}")
            return self
        
        def update(self, data):
            logger.debug(f"Updating data in {self.table_name}: {data}")
            return self
        
        def eq(self, column, value):
            logger.debug(f"Adding equality filter: {column} = {value}")
            return self
        
        def gte(self, column, value):
            logger.debug(f"Adding greater than or equal filter: {column} >= {value}")
            return self
        
        def lte(self, column, value):
            logger.debug(f"Adding less than or equal filter: {column} <= {value}")
            return self
        
        def limit(self, count):
            logger.debug(f"Adding limit: {count}")
            return self
        
        def order(self, column, desc=False):
            logger.debug(f"Adding order: {column} {'DESC' if desc else 'ASC'}")
            return self
        
        def execute(self):
            logger.debug("Executing mock query")
            return MockResult()

    class MockQuery:
        def __init__(self, table_name, columns):
            self.table_name = table_name
            self.columns = columns
            logger.debug(f"Initialized MockQuery for table: {table_name}, columns: {columns}")
        
        def eq(self, column, value):
            logger.debug(f"Adding equality filter: {column} = {value}")
            return self
        
        def gte(self, column, value):
            logger.debug(f"Adding greater than or equal filter: {column} >= {value}")
            return self
        
        def lte(self, column, value):
            logger.debug(f"Adding less than or equal filter: {column} <= {value}")
            return self
        
        def limit(self, count):
            logger.debug(f"Adding limit: {count}")
            return self
        
        def order(self, column, desc=False):
            logger.debug(f"Adding order: {column} {'DESC' if desc else 'ASC'}")
            return self
        
        def execute(self):
            logger.debug("Executing mock query")
            return MockResult()

    class MockResult:
        def __init__(self):
            self.data = []
            logger.debug("Initialized MockResult with empty data")

    # Use mock client as fallback
    supabase = MockSupabaseClient(SUPABASE_URL or "mock-url", SUPABASE_KEY or "mock-key")
    logger.info("Mock Supabase client initialized as fallback")
