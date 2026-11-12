
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

import psycopg


DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "labops")
DB_USER = os.getenv("POSTGRES_USER", "labops")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")


class LabOpsHandler(BaseHTTPRequestHandler):

    def send_json(self, status_code, data):
        response = json.dumps(data).encode("utf-8")

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def do_GET(self):

        if self.path == "/":
            self.send_json(200, {
                "application": "LabOps Demo App",
                "version": "0.1.0",
                "message": "Infrastructure platform is running."
            })

        elif self.path == "/health":
            self.send_json(200, {
                "status": "healthy"
            })

        elif self.path == "/db-health":
            try:
                with psycopg.connect(
                    host=DB_HOST,
                    port=DB_PORT,
                    dbname=DB_NAME,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    connect_timeout=3,
                ) as connection:

                    with connection.cursor() as cursor:
                        cursor.execute("SELECT 1")
                        result = cursor.fetchone()

                self.send_json(200, {
                    "status": "healthy",
                    "database": "connected",
                    "query_result": result[0]
                })

            except psycopg.Error:
                self.send_json(503, {
                    "status": "unhealthy",
                    "database": "unavailable"
                })

        else:
            self.send_json(404, {
                "error": "Not found"
            })


def main():
    port = int(os.getenv("APP_PORT", "8080"))

    server = HTTPServer(("0.0.0.0", port), LabOpsHandler)

    print(f"LabOps Demo App listening on port {port}")

    server.serve_forever()


if __name__ == "__main__":
    main()
