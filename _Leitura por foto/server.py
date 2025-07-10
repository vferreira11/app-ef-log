from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import cv2, numpy as np
import io
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class Slot(BaseModel):
    x: int; y: int; w: int; h: int

class SlotsResponse(BaseModel):
    slots: list[Slot]

@app.post("/api/detect_slots", response_model=SlotsResponse)
async def detect_slots(file: UploadFile = File(...)):
    data = await file.read()
    arr = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges,1,np.pi/180,100,minLineLength=50,maxLineGap=10)
    # simplificação: detecta retângulos fixos
    # A sua lógica de agrupar linhas e extrair slots entra aqui
    slots = []
    # Exemplo estático para testar:
    h, w = img.shape[:2]
    slots.append({"x": int(w*0.1), "y": int(h*0.1), "w": int(w*0.3), "h": int(h*0.3)})
    slots.append({"x": int(w*0.6), "y": int(h*0.1), "w": int(w*0.3), "h": int(h*0.3)})
    return {"slots": slots}
