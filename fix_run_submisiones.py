content = open('api/main.py', 'r', encoding='utf-8').read()

old = '''    def _run():
        try:
            if USAR_PLANNER:
                resultados = planner_executor.ejecutar(sistema, request.orden)
                resultado  = resultados[-1] if resultados else None
            else:
                resultado = pipeline.ejecutar_mision(sistema, request.orden)
            _gcs_guardar(mission_id, {"status": "done", "aprobado": resultado.aprobado, "iteracion": resultado.iteracion, "observaciones": resultado.observaciones, "logs": []})
        except Exception as e:
            _gcs_guardar(mission_id, {"status": "error", "aprobado": None, "iteracion": None, "observaciones": str(e), "logs": []})'''

new = '''    def _run():
        try:
            if USAR_PLANNER:
                try:
                    submisiones_raw = planner_executor.planner.decompose(request.orden)
                    submisiones = [{"id": s["id"], "descripcion": s["descripcion"], "status": "pending"} for s in submisiones_raw]
                except Exception:
                    submisiones = []
                _gcs_guardar(mission_id, {"status": "running", "aprobado": None, "iteracion": None, "observaciones": None, "logs": [], "submisiones": submisiones})
                resultados = planner_executor.ejecutar(sistema, request.orden)
                resultado  = resultados[-1] if resultados else None
            else:
                resultado = pipeline.ejecutar_mision(sistema, request.orden)
            _gcs_guardar(mission_id, {"status": "done", "aprobado": resultado.aprobado, "iteracion": resultado.iteracion, "observaciones": resultado.observaciones, "logs": [], "submisiones": submisiones if USAR_PLANNER else []})
        except Exception as e:
            _gcs_guardar(mission_id, {"status": "error", "aprobado": None, "iteracion": None, "observaciones": str(e), "logs": []})'''

if old in content:
    open('api/main.py', 'w', encoding='utf-8').write(content.replace(old, new))
    print('OK patch _run')
else:
    print('NO MATCH')
