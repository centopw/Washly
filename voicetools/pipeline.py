"""
Pipecat voice pipeline — extracted from bot.py.
"""

from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import ErrorFrame, LLMRunFrame
from pipecat.observers.loggers.debug_log_observer import DebugLogObserver
from pipecat.observers.loggers.llm_log_observer import LLMLogObserver
from pipecat.observers.loggers.transcription_log_observer import TranscriptionLogObserver
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.processors.frameworks.rtvi import RTVIObserver, RTVIProcessor
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.smallwebrtc.transport import SmallWebRTCTransport

from voicetools.backends.provider import get_user_backend
from voicetools.config import settings
from voicetools.prompts import build_system_prompt
from voicetools.registry import register_all_tools


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
        default_headers={
            "HTTP-Referer": "https://valet.ai",
            "X-Title": "Valet AI",
        },
        settings=OpenAILLMService.Settings(model=settings.voice_model),
    )

    tts = ElevenLabsTTSService(
        api_key=settings.elevenlabs_api_key,
        settings=ElevenLabsTTSService.Settings(
            voice=settings.elevenlabs_voice_id,
            model=settings.elevenlabs_model,
        ),
    )

    tools = register_all_tools(llm)

    messages = [{"role": "system", "content": build_system_prompt()}]
    context = LLMContext(messages, tools=tools)

    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(
            vad_analyzer=SileroVADAnalyzer(
                params=VADParams(confidence=0.8, start_secs=0.4, stop_secs=0.3)
            ),
        ),
    )

    rtvi = RTVIProcessor(transport=transport)

    pipeline = Pipeline(
        [
            transport.input(),
            rtvi,
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
        observers=[RTVIObserver(rtvi=rtvi)],
    )

    if settings.debug_pipeline:
        task.add_observer(TranscriptionLogObserver())
        task.add_observer(LLMLogObserver())
        task.add_observer(DebugLogObserver(frame_types=(ErrorFrame,)))

    @llm.event_handler("on_completion_timeout")
    async def on_llm_timeout(svc):
        logger.error("LLM completion timeout (OpenRouter did not respond in time)")

    @tts.event_handler("on_connection_error")
    async def on_tts_error(svc, error):
        open_ctxs = tts.get_audio_contexts()
        logger.error(
            "ElevenLabs WebSocket connection error ({} open context(s)): {}",
            len(open_ctxs),
            error,
        )

    @task.event_handler("on_pipeline_error")
    async def on_error(task, frame):
        logger.error("Pipeline error: {}", frame)

    @transport.event_handler("on_client_connected")
    async def on_connected(transport, client):
        logger.info("Client connected")

    @transport.event_handler("on_client_disconnected")
    async def on_disconnected(transport, client):
        logger.info("Client disconnected")
        open_ctxs = tts.get_audio_contexts()
        if open_ctxs:
            logger.debug("Closing {} lingering ElevenLabs context(s) on disconnect", len(open_ctxs))
            for ctx_id in list(open_ctxs):
                try:
                    await tts._close_context(ctx_id)
                except Exception:
                    pass
        await task.cancel()

    @transport.event_handler("on_app_message")
    async def on_app_message(transport, message, sender):
        if isinstance(message, dict) and message.get("type") == "session_start":
            logger.info("Session started")

            phone = message.get("phone_number", "").strip()
            if phone.startswith("0"):
                phone = "+84" + phone[1:]

            user_ctx = ""
            if phone:
                user = await get_user_backend().get_user_by_phone(phone)
                if user:
                    name = user.get("name", "")
                    car = f"{user.get('car_make', '')} {user.get('car_model', '')}".strip()
                    plate = user.get("car_plate", "")
                    tier = user.get("tier", "")
                    history = user.get("service_history", [])
                    last_service = history[-1] if history else None
                    user_ctx = (
                        f"RETURNING CUSTOMER IDENTIFIED: {name} | Tier: {tier} | "
                        f"Vehicle: {car} ({plate})"
                    )
                    if last_service:
                        user_ctx += f" | Last service: {last_service}"
                    user_ctx += (
                        f". Greet them by first name ({name.split()[0] if name else 'there'}), "
                        "do NOT ask for their name or phone number again. "
                        "Ask if they are still in the same area and how you can help today."
                    )
                    user_ctx += (
                        f" KNOWN PHONE NUMBER: {phone}. For ALL tool calls that require phone_number, "
                        f"use {phone} directly — never ask the customer for it."
                    )
                else:
                    user_ctx = (
                        f"NEW CUSTOMER (phone not recognized): {phone}. "
                        "Welcome them as a first-time customer when get_user_details is called. "
                        f"For ALL tool calls requiring phone_number, use {phone} — do not ask for it."
                    )

            if user_ctx:
                context.add_message({"role": "system", "content": user_ctx})
            context.add_message({
                "role": "user",
                "content": "[Customer connected. Greet them warmly and ask how you can help.]",
            })
            await task.queue_frames([LLMRunFrame()])

    runner = PipelineRunner(handle_sigint=False)
    try:
        await runner.run(task)
    except Exception:
        logger.exception("Bot pipeline error")
