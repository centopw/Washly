from pipecat.frames.frames import Frame, TranscriptionFrame
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.processors.aggregators.llm_context import LLMContext
from loguru import logger

LANGUAGE_NAMES = {
    "en": "English",
    "vi": "Vietnamese",
}


class LanguageDetectionProcessor(FrameProcessor):
    def __init__(self, context: LLMContext, **kwargs):
        super().__init__(**kwargs)
        self._context = context
        self._current_language: str | None = None

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if isinstance(frame, TranscriptionFrame) and frame.language:
            detected = str(frame.language).split("-")[0]  # "en-US" -> "en"
            if detected != self._current_language:
                self._current_language = detected
                lang_name = LANGUAGE_NAMES.get(detected, detected)
                logger.info("Language switch detected: {}", lang_name)
                self._context.add_message({
                    "role": "system",
                    "content": f"[The customer is now speaking {lang_name}. You MUST respond in {lang_name}.]",
                })

        await self.push_frame(frame, direction)
