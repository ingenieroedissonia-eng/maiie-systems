content = open('orchestrator/pipeline.py', encoding='utf-8').read()

old = '            console.print("[bold red]\u26a0\ufe0f RECHAZADO. Reingeni\u00eer\u00eda iniciada...[/]")\n            print(f"\u274c RECHAZADO en ciclo {iteracion} \u2014 iniciando siguiente ciclo")'

new = '            if feedback_actual and feedback_actual == getattr(ejecutar_mision, "_ultimo_feedback", None):\n                ejecutar_mision._contador_error = getattr(ejecutar_mision, "_contador_error", 0) + 1\n            else:\n                ejecutar_mision._contador_error = 0\n            ejecutar_mision._ultimo_feedback = feedback_actual\n\n            if getattr(ejecutar_mision, "_contador_error", 0) >= 2:\n                logger.warning("Early kill: mismo error 2 ciclos consecutivos")\n                print("Early kill activado - regenerando desde cero")\n                break\n\n            console.print("[bold red]\u26a0\ufe0f RECHAZADO. Reingeni\u00eer\u00eda iniciada...[/]")\n            print(f"\u274c RECHAZADO en ciclo {iteracion} \u2014 iniciando siguiente ciclo")'

result = content.replace(old, new)
if result == content:
    print('ERROR: patron no encontrado')
else:
    open('orchestrator/pipeline.py', 'w', encoding='utf-8').write(result)
    print('OK')
