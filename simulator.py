import sqlite3
import time
from datetime import datetime, timedelta
import random
from database import get_db_connection

def insert_attempt(ip, username, status, custom_time=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    timestamp = custom_time if custom_time else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT INTO login_attempts (ip_address, username, status, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (ip, username, status, timestamp))
    
    conn.commit()
    conn.close()

def generate_normal_traffic():
    print("[*] Generating legitimate user activity...")
    normal_users = ["alice", "bob", "developer", "rahul", "umar"]
    normal_ips = ["192.168.1.10", "192.168.1.15", "192.168.1.22", "192.168.1.30"]
    
    for _ in range(12):
        ip = random.choice(normal_ips)
        user = random.choice(normal_users)
        status = "SUCCESS" if random.random() > 0.15 else "FAILED"
        insert_attempt(ip, user, status)
        print(f"  [Normal] {ip} | User: {user} | Status: {status}")
        time.sleep(0.1)

def simulate_bruteforce_attack(attacker_ip="10.0.0.99", target_user="admin", attempts=8):
    print(f"\n[!] Simulating Brute-Force Attack from {attacker_ip} targeting '{target_user}'...")
    for i in range(1, attempts + 1):
        insert_attempt(attacker_ip, target_user, "FAILED")
        print(f"  [ATTACK Attempt #{i}] {attacker_ip} -> {target_user} (FAILED)")
        time.sleep(0.1)

def simulate_password_spray(attacker_ip="185.220.101.5", attempts=6):
    print(f"\n[!] Simulating Password Spraying Attack from {attacker_ip}...")
    targets = ["admin", "root", "support", "test", "sales", "hr"]
    for user in targets[:attempts]:
        insert_attempt(attacker_ip, user, "FAILED")
        print(f"  [SPRAY Attempt] {attacker_ip} -> {user} (FAILED)")
        time.sleep(0.1)

if __name__ == "__main__":
    generate_normal_traffic()
    simulate_bruteforce_attack()
    simulate_password_spray()
    print("\n[+] Synthetic simulation completed.")
