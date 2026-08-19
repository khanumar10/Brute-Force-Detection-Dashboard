from datetime import datetime, timedelta
from database import get_db_connection


FAILED_THRESHOLD = 5       
TIME_WINDOW_MINUTES = 10   

def scan_for_bruteforce():
    conn = get_db_connection()
    cursor = conn.cursor()

    
    cutoff_time = (datetime.now() - timedelta(minutes=TIME_WINDOW_MINUTES)).strftime("%Y-%m-%d %H:%M:%S")

    
    query = '''
        SELECT 
            ip_address, 
            username, 
            COUNT(*) as failure_count,
            MIN(timestamp) as first_seen,
            MAX(timestamp) as last_seen
        FROM login_attempts
        WHERE status = 'FAILED' AND timestamp >= ?
        GROUP BY ip_address
        HAVING COUNT(*) >= ?
    '''
    cursor.execute(query, (cutoff_time, FAILED_THRESHOLD))
    suspicious_entries = cursor.fetchall()

    alerts_created = 0
    for entry in suspicious_entries:
        ip = entry["ip_address"]
        user = entry["username"]
        count = entry["failure_count"]
        first_seen = entry["first_seen"]
        last_seen = entry["last_seen"]

        
        cursor.execute('''
            SELECT id FROM security_alerts 
            WHERE ip_address = ? AND last_attempt = ?
        ''', (ip, last_seen))
        
        existing_alert = cursor.fetchone()

        if not existing_alert:
            cursor.execute('''
                INSERT INTO security_alerts 
                (ip_address, target_username, failed_count, first_attempt, last_attempt, severity)
                VALUES (?, ?, ?, ?, ?, 'HIGH')
            ''', (ip, user, count, first_seen, last_seen))
            alerts_created += 1
            print(f"[!] ALERT: Brute-force detected from {ip} on user '{user}' ({count} failed attempts)")

    conn.commit()
    conn.close()
    return alerts_created

if __name__ == "__main__":
    print("[*] Running detection engine scan...")
    detected = scan_for_bruteforce()
    print(f"[+] Scan finished. New incidents flagged: {detected}")
