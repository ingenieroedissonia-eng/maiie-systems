content = open('api/main.py', 'r', encoding='utf-8').read()

old = '''@app.get("/mission/{mission_id}/status", response_model=MissionStatusResponse)
def estado_mision(mission_id: str):'''

new = '''@app.get("/mission/{mission_id}/submissions")
def obtener_submisiones(mission_id: str):
    data = _gcs_obtener(mission_id)
    if not data:
        raise HTTPException(status_code=404, detail="Mission no encontrada")
    return {"mission_id": mission_id, "submisiones": data.get("submisiones", []), "status": data.get("status")}

@app.get("/mission/{mission_id}/status", response_model=MissionStatusResponse)
def estado_mision(mission_id: str):'''

if old in content:
    open('api/main.py', 'w', encoding='utf-8').write(content.replace(old, new))
    print('OK endpoint submissions')
else:
    print('NO MATCH')
