from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse

class WebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Set response status code
        self.send_response(200)
        
        # Set headers
        if path == "/" or path == "/index.html":
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Aplicación Web Simple</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
                    h1 { color: #333; }
                    .container { max-width: 600px; margin: 0 auto; }
                    a { color: #007bff; text-decoration: none; }
                    a:hover { text-decoration: underline; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>¡Bienvenido a Mi Aplicación Web!</h1>
                    <p>Esta aplicación está corriendo localmente en tu máquina.</p>
                    <p>Funciones disponibles:</p>
                    <ul>
                        <li><a href="/hello/usuario">Endpoint de prueba</a></li>
                        <li><a href="/api/status">API Status</a></li>
                    </ul>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html_content.encode())
        
        elif path.startswith("/hello/"):
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            name = path.split('/')[-1]  # Get the name from URL
            response = {"message": f"¡Hola {name}!"}
            self.wfile.write(json.dumps(response).encode())
        
        elif path == "/api/status":
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {"status": "ok", "message": "Servidor corriendo correctamente"}
            self.wfile.write(json.dumps(response).encode())
        
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write("<h1>404 - Página no encontrada</h1>".encode())

if __name__ == "__main__":
    server = HTTPServer(('localhost', 8000), WebHandler)
    print("Servidor iniciado en http://localhost:8000")
    print("Páginas disponibles:")
    print("  - http://localhost:8000 (página principal)")
    print("  - http://localhost:8000/hello/usuario (endpoint de prueba)")
    print("  - http://localhost:8000/api/status (API status)")
    print("Presiona Ctrl+C para detener el servidor")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\
Servidor detenido.")