content = open('api/main.py', encoding='utf-8-sig').read()

old = '''    _gcs_guardar(mission_id, {"status": "running", "aprobado": None, "iteracion": None, "observaciones": None, "logs": [], "submissions": []})

    def _run():
        try:
            if USAR_PLANNER:
                submisiones, resultados = planner_executor.ejecutar(sistema, request.orden)
                resultado  = resultados[-1] if resultados else None'''

new = '''    submisiones_iniciales = []
    if USAR_PLANNER:
        try:
            subs_raw = planner_executor.planner.decompose(request.orden)
            submisiones_iniciales = [{"id": s["id"], "descripcion": s["descripcion"], "status": "pending"} for s in subs_raw]
        except Exception:
            submisiones_iniciales = []
    _gcs_guardar(mission_id, {"status": "running", "aprobado": None, "iteracion": None, "observaciones": None, "logs": [], "submissions": submisiones_iniciales})

    def _run():
        try:
            if USAR_PLANNER:
                submisiones, resultados = planner_executor.ejecutar(sistema, request.orden)
                resultado  = resultados[-1] if resultados else None'''

if old in content:
    open('api/main.py', 'w', encoding='utf-8').write(content.replace(old, new))
    print('OK')
else:
    print('NOT FOUND')
