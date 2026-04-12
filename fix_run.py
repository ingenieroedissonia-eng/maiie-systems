path = 'api/main.py'
c = open(path, encoding='utf-8').read()

# Encontrar inicio y fin del bloque _run
start = c.find('    def _run():')
end = c.find('    threading.Thread(target=_run')

if start == -1 or end == -1:
    print(f'NO ENCONTRADO start={start} end={end}')
else:
    new_run = '''    def _run():
        try:
            def _on_submision_done(sub_id, status, codigo, feedback=None):
                try:
                    estado_actual = _gcs_obtener(mission_id)
                    if not estado_actual:
                        return
                    subs = estado_actual.get("submissions", [])
                    for s in subs:
                        if s.get("id") == sub_id:
                            s["status"] = status
                            s["codigo"] = codigo
                            if feedback is not None:
                                s["feedback"] = feedback
                            break
                    estado_actual["submissions"] = subs
                    _gcs_guardar(mission_id, estado_actual)
                except Exception as _e:
                    logger.warning(f"_on_submision_done error sub {sub_id}: {_e}")

            if USAR_PLANNER:
                submisiones, resultados = planner_executor.ejecutar(sistema, request.orden, submisiones_previas=submisiones_iniciales, on_submision_done=_on_submision_done)
                resultado = resultados[-1] if resultados else None
            else:
                submisiones = []
                resultados = []
                resultado = pipeline.ejecutar_mision(sistema, request.orden)

            _gcs_guardar(mission_id, {
                "status": "done",
                "aprobado": resultado.aprobado if resultado else False,
                "iteracion": resultado.iteracion if resultado else None,
                "observaciones": resultado.observaciones if resultado else "Sin resultado",
                "logs": [],
                "submissions": [
                    dict(s, status="done",
                         feedback=resultados[i].reporte_auditoria if USAR_PLANNER and i < len(resultados) and resultados[i].aprobado else None,
                         codigo=resultados[i].codigo_final if USAR_PLANNER and i < len(resultados) else None)
                    for i, s in enumerate(submisiones)
                ],
                "codigo_generado": resultado.codigo_final if resultado and hasattr(resultado, "codigo_final") else None
            })

            if resultado and resultado.aprobado:
                try:
                    from utils.github_publisher import GitHubPublisher
                    publisher = GitHubPublisher()
                    repo_path = resultado.repo_path
                    publisher.publicar_mision(mission_id=mission_id, repo_path=repo_path, descripcion=request.orden[:100])
                    logger.info('GitHub autopublish OK: ' + str(mission_id))
                except Exception as _ge:
                    logger.warning('GitHub autopublish error: ' + str(_ge))

        except Exception as e:
            _gcs_guardar(mission_id, {"status": "error", "aprobado": None, "iteracion": None, "observaciones": str(e), "logs": []})

'''
    new_content = c[:start] + new_run + c[end:]
    open(path, 'w', encoding='utf-8').write(new_content)
    print('OK')
