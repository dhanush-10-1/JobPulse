import psycopg2
import config
from jobpulse.utils.logger import logger
def connect_db():
    try:
        conn=psycopg2.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD
    )

        logger.info("connected to postgres DB successfully")
        return conn
    except psycopg2.Error:
        logger.exception("falied to connect to Pgsql DB")
        raise
    

    