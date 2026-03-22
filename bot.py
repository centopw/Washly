"""
Washly AI — Voice Agent
Pipecat v0.0.106+  |  Python 3.13
"""

from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from loguru import logger

from pipecat.audio.filters.rnnoise_filter import RNNoiseFilter
from pipecat.transports.base_transport import TransportParams
from pipecat.transports.smallwebrtc.request_handler import (
    IceCandidate,
    SmallWebRTCPatchRequest,
    SmallWebRTCRequest,
    SmallWebRTCRequestHandler,
)
from pipecat.transports.smallwebrtc.transport import SmallWebRTCTransport
from pipecat_ai_small_webrtc_prebuilt.frontend import SmallWebRTCPrebuiltUI

from voicetools.config import settings
from voicetools.logging import configure_logging
from voicetools.backends.db import close_db, ensure_indexes
from voicetools.pipeline import run_bot

configure_logging(settings.log_level)


# ── FastAPI ───────────────────────────────────────────────────

webrtc_handler = SmallWebRTCRequestHandler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Valet starting — open http://localhost:{}/client in Chrome", settings.server_port)
    await ensure_indexes()
    yield
    await webrtc_handler.close()
    await close_db()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/client", SmallWebRTCPrebuiltUI)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/client")


@app.post("/start")
async def start():
    """Prebuilt UI calls /start first to discover the offer URL."""
    return JSONResponse({"webrtcUrl": "/api/offer"})


@app.post("/api/offer")
async def offer(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    try:
        req = SmallWebRTCRequest(
            sdp=body["sdp"],
            type=body["type"],
            pc_id=body.get("pc_id") or body.get("pcId"),
        )

        async def on_connection(connection):
            transport = SmallWebRTCTransport(
                webrtc_connection=connection,
                params=TransportParams(
                    audio_in_enabled=True,
                    audio_out_enabled=True,
                    audio_in_filter=RNNoiseFilter(),
                ),
            )
            background_tasks.add_task(run_bot, transport)

        answer = await webrtc_handler.handle_web_request(
            request=req,
            webrtc_connection_callback=on_connection,
        )
        return JSONResponse(answer)
    except KeyError as e:
        return JSONResponse({"error": f"Missing field: {e}"}, status_code=400)
    except Exception:
        logger.exception("Error handling /api/offer")
        return JSONResponse({"error": "Internal server error"}, status_code=500)


@app.patch("/api/offer")
async def patch_offer(request: Request):
    body = await request.json()
    pc_id = body.get("pc_id") or body.get("pcId")
    candidates = [
        IceCandidate(
            candidate=c["candidate"],
            sdp_mid=c.get("sdp_mid") or c.get("sdpMid"),
            sdp_mline_index=c.get("sdp_mline_index") or c.get("sdpMLineIndex"),
        )
        for c in body.get("candidates", [])
    ]
    req = SmallWebRTCPatchRequest(pc_id=pc_id, candidates=candidates)
    await webrtc_handler.handle_patch_request(req)
    return JSONResponse({"status": "ok"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.server_host, port=settings.server_port)
