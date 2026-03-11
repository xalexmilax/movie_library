from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from routers.auth import auth_router
from routers.movies import movies_router

from common.exceptions import AppError


app = FastAPI(
    title='Secure Movie Library API',
    description='A secure FastAPI application for managing movies with background rating enrichment',
    version='1.0'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


# ==================== ERROR HANDLERS ====================


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={'message': exc.message}
    )

@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={'message': 'Internal Server Error'}
    )


# ==================== REGISTER ROUTERS ====================


app.include_router(auth_router, prefix='/auth', tags=['Authentication'])
app.include_router(movies_router)


# ==================== ROOT ENDPOINT ====================


@app.get('/', tags=['Root'])
def root():
    return {
        'message': 'Welcome to my Secure Movie Library API',
        'docs': '/docs',
        'version': '1.0'
    }


# ==================== FAVICON ERROR FIX ====================


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Return empty response for favicon to avoid 404 errors in browser."""
    return Response(status_code=204)