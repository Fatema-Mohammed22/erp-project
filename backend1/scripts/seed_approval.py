import os, sqlite3

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "erp_sample.db")
con = sqlite3.connect(DB)
con.execute("PRAGMA foreign_keys=ON;")
con.execute("""
INSERT INTO approvals(module, payload_json, status, requested_by, created_at)
VALUES('finance', '{"action":"post_invoice","invoice_id":101}', 'pending', 'user.alfa', datetime('now'));
""")
con.commit()
con.close()
print("Inserted a pending approval into approvals table.")
