content = open('api/main.py', encoding='utf-8').read()

old = 'class MissionStatusResponse(BaseModel):\n    mission_id: str\n    status: str\n    aprobado: bool = None\n    iteracion: int = None\n    observaciones: str = None\n    logs: list = []'
new = 'class MissionStatusResponse(BaseModel):\n    mission_id: str\n    status: str\n    aprobado: Optional[bool] = None\n    iteracion: Optional[int] = None\n    observaciones: Optional[str] = None\n    logs: list = []'
content = content.replace(old, new, 1)

open('api/main.py', 'w', encoding='utf-8').write(content)
print('OK')
