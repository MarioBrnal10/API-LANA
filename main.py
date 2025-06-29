from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.usuarios import routerUsuarios
from routers.transacciones import routerTransacciones
from routers.presupuestos import routerPresupuestos

app = FastAPI(
    title='API LANA APP',
    description='API PARA LA APLICACION LANA APP',
    version='1.0.1'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)



app.include_router(routerUsuarios)
app.include_router(routerTransacciones)

app.include_router(routerPresupuestos)

