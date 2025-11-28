from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Mi Aplicación Web")

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mi Aplicación Web</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
            h1 { color: #333; }
            .container { max-width: 600px; margin: 0 auto; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>¡Bienvenido a Mi Aplicación Web!</h1>
            <p>Esta aplicación está corriendo localmente en tu máquina.</p>
            <p>Funciones disponibles:</p>
            <ul>
                <li><a href="/docs">Documentación API (Swagger)</a></li>
                <li><a href="/redoc">Documentación API (ReDoc)</a></li>
            </ul>
        </div>
    </body>
    </html>
    """

@app.get("/hello/{name}")
def read_item(name: str):
    return {"message": f"¡Hola {name}!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)