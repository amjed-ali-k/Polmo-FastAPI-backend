import fastapi
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from api import auth, sensornode
from views import home
from config import settings
import uvicorn

tags_metadata = [
    {
        "name": "User",
        "description": "User registration and Authentication REST API Routes.",
    },
    {
        "name": "SensorNode",
        "description": "Endpoint related to sensor nodes. Here you can fetch all data related to sensor nodes. Data "
                       "are directly fetched from databases. This API endpoint doesn't have any direct link to "
                       "sensornodes and its hardware.",
        "externalDocs": {
            "description": "Full Project GitHub Link",
            "url": "https://github.com/HarinarayananP/Air-polution-monitoring",
        },
    },
]
app = fastapi.FastAPI(title="POLMO",
                      openapi_tags=tags_metadata,
                      description="Air pollution monitoring system",
                      version="0.1.0",
                      license_info={
                          "name": "Apache 2.0",
                          "url": "https://www.apache.org/licenses/LICENSE-2.0.html"},
                     )



def configure():
    configure_middlewares()
    configure_routing()


def configure_middlewares():
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def configure_routing():
    app.mount('/static', StaticFiles(directory='static'), name='static')
    app.include_router(home.router)
    app.include_router(auth.router)
    app.include_router(sensornode.r)


if __name__ == '__main__':
    configure()
    uvicorn.run("main:app", port=8000, host="127.0.0.1", reload=True)
else:
    configure()
