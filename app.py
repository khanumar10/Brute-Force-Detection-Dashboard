from flask import Flask, render_template, jsonify, request
from database import get_db_connection
from detector import scan_for_bruteforce
from simulator import simulate_bruteforce_attack

app = Flask(__name__)


@app.route('/')
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    
    cursor.execute("SELECT COUNT(*) FROM login_attempts")
    total_attempts = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM login_attempts WHERE status = 'SUCCESS'")
    success_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM login_attempts WHERE status = 'FAILED'")
    failed_count = cursor.fetchone()[0]

    
    cursor.execute("SELECT COUNT(*) FROM security_alerts")
    alert_count = cursor.fetchone()[0]

    
    cursor.execute("SELECT * FROM security_alerts ORDER BY detected_at DESC LIMIT 10")
    recent_alerts = cursor.fetchall()

    
    cursor.execute("SELECT * FROM login_attempts ORDER BY timestamp DESC LIMIT 15")
    recent_logs = cursor.fetchall()

    conn.close()

    return render_template(
        'index.html',
        total_attempts=total_attempts,
        success_count=success_count,
        failed_count=failed_count,
        alert_count=alert_count,
        recent_alerts=recent_alerts,
        recent_logs=recent_logs
    )


@app.route('/api/chart-data')
def chart_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    
    cursor.execute('''
        SELECT ip_address, COUNT(*) as count 
        FROM login_attempts 
        WHERE status = 'FAILED' 
        GROUP BY ip_address 
        ORDER BY count DESC 
        LIMIT 5
    ''')
    top_ips = cursor.fetchall()

    
    cursor.execute("SELECT status, COUNT(*) as count FROM login_attempts GROUP BY status")
    status_data = cursor.fetchall()

    conn.close()

    return jsonify({
        "top_ips": {
            "labels": [row["ip_address"] for row in top_ips],
            "counts": [row["count"] for row in top_ips]
        },
        "status_ratio": {
            "labels": [row["status"] for row in status_data],
            "counts": [row["count"] for row in status_data]
        }
    })


@app.route('/api/trigger-scan', methods=['POST'])
def trigger_scan():
    alerts_created = scan_for_bruteforce()
    return jsonify({"status": "success", "new_alerts": alerts_created})


@app.route('/api/simulate-attack', methods=['POST'])
def trigger_attack():
    simulate_bruteforce_attack(attacker_ip="198.51.100.42", target_user="admin", attempts=7)
    scan_for_bruteforce()
    return jsonify({"status": "success", "message": "Attack simulated"})

if __name__ == '__main__':
    scan_for_bruteforce()
    app.run(debug=True, host='0.0.0.0', port=5000)
