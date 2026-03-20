"""
Valet AI — Voice Agent
Pipecat v0.0.106+  |  Python 3.13
"""

from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import LLMRunFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.kokoro.tts import KokoroTTSService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transcriptions.language import Language
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
from voicetools.prompts import build_system_prompt
from voicetools.registry import register_all_tools
from voicetools.backends.db import close_db, ensure_indexes

configure_logging(settings.log_level)


async def run_bot(transport: SmallWebRTCTransport) -> None:
    stt = DeepgramSTTService(
        api_key=settings.deepgram_api_key,
        settings=DeepgramSTTService.Settings(
            language="en",
            model="nova-2",
        ),
    )

    llm = OpenAILLMService(
        api_key=settings.openrouter_api_key,
        base_url="https://openrouter.ai/api/v1",
        model=settings.voice_model,
        extra_headers={
            "HTTP-Referer": "https://valet.ai",
            "X-Title": "Valet AI",
        },
    )

    tts = KokoroTTSService(
        settings=KokoroTTSService.Settings(
            voice=settings.tts_voice_id,
            language=Language.EN,
        ),
    )

    tools = register_all_tools(llm)

    messages = [{"role": "system", "content": build_system_prompt()}]
    context = LLMContext(messages, tools=tools)

    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(
            vad_analyzer=SileroVADAnalyzer(
                params=VADParams(stop_secs=0.3)
            ),
        ),
    )

    pipeline = Pipeline(
        [
            transport.input(),
            stt,
            user_aggregator,
            llm,
            tts,
            transport.output(),
            assistant_aggregator,
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            allow_interruptions=True,
            enable_metrics=True,
        ),
    )

    @transport.event_handler("on_client_connected")
    async def on_connected(transport, client):
        logger.info("Client connected")
        context.add_message({
            "role": "user",
            "content": "[Customer just connected. Greet them warmly and ask how you can help.]",
        })
        await task.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_disconnected")
    async def on_disconnected(transport, client):
        logger.info("Client disconnected")
        await task.cancel()

    runner = PipelineRunner(handle_sigint=False)
    try:
        await runner.run(task)
    except Exception:
        logger.exception("Bot pipeline error")


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
