import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


def connect_to_db():
    """
    Connect to the PostgreSQL database using environment variables.
    Returns a connection object.
    """
    db_password = os.getenv("DB_PASSWORD")
    if not db_password:
        raise ValueError(
            "Database password not found in environment variables. Please set DB_PASSWORD."
        )

    # Get database connection details from environment variables with defaults
    db_host = os.getenv("DB_HOST")
    db_port = int(os.getenv("DB_PORT"))
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")

    return psycopg2.connect(
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_password,
        cursor_factory=psycopg2.extras.DictCursor,
    )


def cleanup_old_configurations():
    cleanup_situations = [
        """
        DELETE FROM api_configurations
        WHERE stop_at IS NOT NULL
            AND stop_at < NOW() - INTERVAL '14 days';
        """,
    ]

    conn = None
    try:
        conn = connect_to_db()
        with conn.cursor() as cur:
            for raw_sql in cleanup_situations:
                sql = raw_sql.strip()
                if not sql:
                    continue

                cur.execute(sql)
                deleted = cur.rowcount
                print(f"[CLEANUP] {deleted} rows deleted.")
        conn.commit()
        print("[SUCCESS] Database cleanup completed successfully")

    except Exception as e:
        print(f"[ERROR] cleanup failed: {e}")

    finally:
        if conn:
            conn.close()


def job_schedule():
    sched = BlockingScheduler()
    sched.add_job(cleanup_old_configurations, "cron", hour=0, minute=0)
    print("cleanup job scheduled at 00:00 UTC")
    sched.start()


if __name__ == "__main__":
    print("[INFO] Starting database cleanup scheduler...")
    job_schedule()
