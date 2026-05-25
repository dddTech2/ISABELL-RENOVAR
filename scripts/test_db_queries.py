import mysql.connector
import json

def main():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="asterisk",
            password="asterisk",
            database="call_center"
        )
        cursor = conn.cursor(dictionary=True)
        
        print("--- Table structure of calls ---")
        cursor.execute("DESCRIBE calls")
        for r in cursor.fetchall():
            print(r)
            
        print("\n--- Recent calls (max 5) ---")
        cursor.execute("SELECT * FROM calls ORDER BY start_time DESC LIMIT 5")
        for r in cursor.fetchall():
            print(json.dumps(r, default=str))

        print("\n--- Table structure of audit ---")
        cursor.execute("DESCRIBE audit")
        for r in cursor.fetchall():
            print(r)

        print("\n--- Recent audit records (max 5) ---")
        cursor.execute("SELECT * FROM audit ORDER BY datetime_init DESC LIMIT 5")
        for r in cursor.fetchall():
            print(json.dumps(r, default=str))

        print("\n--- Table structure of break ---")
        cursor.execute("DESCRIBE break")
        for r in cursor.fetchall():
            print(r)

        print("\n--- Break types ---")
        cursor.execute("SELECT * FROM break")
        for r in cursor.fetchall():
            print(r)

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    main()
