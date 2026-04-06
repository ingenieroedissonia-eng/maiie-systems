content = open('api/main.py', encoding='utf-8', errors='replace').read()

old1 = 'import logging'
new1 = 'import logging\nimport threading\nimport uuid as _uuid\n\nmissions_store: dict = {}'
content = content.replace(old1, new1, 1)

old2 = 'class MissionResponse(BaseModel):\n    aprobado: bool\n    iteracion: int\n    observaciones: str'
new2 = 'class MissionResponse(BaseModel):\n    mission_id: str\n    status: str\n    message: str\n\nclass MissionStatusResponse(BaseModel):\n    mission_id: str\n    status: str\n    aprobado: bool = None\n    iteracion: int = None\n    observaciones: str = None\n    logs: list = []'
content = content.replace(old2, new2, 1)

old3 = '@app.post("/mission", response_model=MissionResponse)\ndef ejecutar_mision(request: MissionRequest):\n\n    if USAR_PLANNER:\n        resultados = planner_executor.ejecutar(sistema, request.orden)\n        resultado  = resultados[-1] if resultados else None\n    else:\n        resultado = pipeline.ejecutar_mision(sistema, request.orden)\n\n    return MissionResponse(\n        aprobado=resultado.aprobado,\n        iteracion=resultado.iteracion,\n        observaciones=resultado.observaciones\n    )'
new3 = '@app.post("/mission", response_model=MissionResponse)\ndef ejecutar_mision(request: MissionRequest):\n    mission_id = _uuid.uuid4().hex[:12]\n    missions_store[mission_id] = {"status": "running", "aprobado": None, "iteracion": None, "observaciones": None, "logs": []}\n\n    def _run():\n        try:\n            if USAR_PLANNER:\n                resultados = planner_executor.ejecutar(sistema, request.orden)\n                resultado  = resultados[-1] if resultados else None\n            else:\n                resultado = pipeline.ejecutar_mision(sistema, request.orden)\n            missions_store[mission_id].update({"status": "done", "aprobado": resultado.aprobado, "iteracion": resultado.iteracion, "observaciones": resultado.observaciones})\n        except Exception as e:\n            missions_store[mission_id].update({"status": "error", "observaciones": str(e)})\n\n    threading.Thread(target=_run, daemon=True).start()\n    return MissionResponse(mission_id=mission_id, status="running", message="Mision iniciada. Consulta GET /mission/{id}/status")\n\n\n@app.get("/mission/{mission_id}/status", response_model=MissionStatusResponse)\ndef estado_mision(mission_id: str):\n    data = missions_store.get(mission_id)\n    if not data:\n        raise HTTPException(status_code=404, detail="Mission no encontrada")\n    return MissionStatusResponse(mission_id=mission_id, status=data["status"], aprobado=data.get("aprobado"), iteracion=data.get("iteracion"), observaciones=data.get("observaciones"), logs=data.get("logs", []))'
content = content.replace(old3, new3, 1)

open('api/main.py', 'w', encoding='utf-8').write(content)
print('OK')
