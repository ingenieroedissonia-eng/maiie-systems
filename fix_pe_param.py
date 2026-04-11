content = open('orchestrator/planner_executor.py', encoding='utf-8-sig').read()

old = '''    def ejecutar(self, orquestador: AgentExecutor, orden: str) -> List[Any]:
        logger.info("Iniciando ejecucion con Planner + contexto incremental")

        try:
            submisiones = self.planner.decompose(orden)
        except PlannerFailedError as e:
            logger.error(f"Mision abortada en fase de planificacion. Motivo: {e}")
            return []

        validator = PlanValidator()
        valido, motivo = validator.validar(submisiones)
        if not valido:
            logger.error(f"Plan invalido: {motivo}")
            raise PlanValidationError(motivo)'''

new = '''    def ejecutar(self, orquestador: AgentExecutor, orden: str, submisiones_previas: List[dict] = None) -> List[Any]:
        logger.info("Iniciando ejecucion con Planner + contexto incremental")

        if submisiones_previas:
            logger.info(f"Usando {len(submisiones_previas)} submisiones previas (sin nuevo decompose)")
            submisiones = submisiones_previas
        else:
            try:
                submisiones = self.planner.decompose(orden)
            except PlannerFailedError as e:
                logger.error(f"Mision abortada en fase de planificacion. Motivo: {e}")
                return [], []

        validator = PlanValidator()
        valido, motivo = validator.validar(submisiones)
        if not valido:
            logger.error(f"Plan invalido: {motivo}")
            raise PlanValidationError(motivo)'''

if old in content:
    open('orchestrator/planner_executor.py', 'w', encoding='utf-8').write(content.replace(old, new))
    print('OK planner_executor.py')
else:
    print('NOT FOUND')
