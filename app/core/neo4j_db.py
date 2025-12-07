from neo4j import GraphDatabase, AsyncGraphDatabase
from app.core.config import settings

# Global driver instance
driver = None

async def init_neo4j():
    global driver
    driver = AsyncGraphDatabase.driver(
        settings.NEO4J_URI, 
        auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
    )

async def close_neo4j():
    global driver
    if driver:
        await driver.close()

def get_neo4j_driver():
    return driver
