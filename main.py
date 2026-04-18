# main.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import asyncio

from camera import Camera
from servo import ServoController

app = FastAPI(title="Chicken Coop Remote")
camera = Camera()
servo = ServoController(gpio_pin=17)

# Create static directory for web interface
import os
os.makedirs("static", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chicken Coop Remote</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: system-ui, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background: #1a1a1a;
                color: #fff;
            }
            h1 { text-align: center; }
            .video-container {
                background: #000;
                border-radius: 8px;
                overflow: hidden;
                margin-bottom: 20px;
            }
            .video-container img {
                width: 100%;
                height: auto;
                display: block;
            }
            .controls {
                display: flex;
                gap: 10px;
                justify-content: center;
                flex-wrap: wrap;
            }
            button {
                padding: 15px 30px;
                font-size: 16px;
                border: none;
                border-radius: 8px;
                background: #4CAF50;
                color: white;
                cursor: pointer;
                min-width: 100px;
            }
            button:hover { background: #45a049; }
            button:active { transform: scale(0.95); }
            .status {
                text-align: center;
                margin-top: 15px;
                color: #aaa;
            }
        </style>
    </head>
    <body>
        <h1>🐔 Chicken Coop Remote</h1>
        
        <div class="video-container">
            <img src="/video" alt="Camera feed">
        </div>
        
        <div class="controls">
            <button onclick="moveServo(90)">⬅️ Left</button>
            <button onclick="moveServo(0)">⏹️ Center</button>
            <button onclick="moveServo(-90)">➡️ Right</button>
        </div>
        
        <div class="status" id="status">Servo position: center</div>
        
        <script>
            async function moveServo(angle) {
                try {
                    const response = await fetch(`/servo/${angle}`, {
                        method: 'POST'
                    });
                    const data = await response.json();
                    document.getElementById('status').textContent = 
                        `Servo position: ${data.angle}°`;
                } catch (err) {
                    document.getElementById('status').textContent = 
                        'Error: ' + err.message;
                }
            }
        </script>
    </body>
    </html>
    """


@app.get("/video")
async def video_feed():
    return StreamingResponse(
        camera.generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.post("/servo/{angle}")
async def set_servo(angle: int):
    servo.set_angle(angle)
    return {"angle": angle, "status": "ok"}


@app.on_event("shutdown")
async def shutdown():
    camera.close()
    servo.close()