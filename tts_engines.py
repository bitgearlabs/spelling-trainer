"""Các engine Text-to-Speech: edge-tts (khuyến nghị), gTTS, pyttsx3."""
import asyncio
import importlib.util


def _has(mod: str) -> bool:
    return importlib.util.find_spec(mod) is not None


EDGE_VOICES = [
    ("Sonia – British female (most natural)", "en-GB-SoniaNeural"),
    ("Ryan – British male", "en-GB-RyanNeural"),
    ("Libby – British female", "en-GB-LibbyNeural"),
    ("Natasha – Australian female", "en-AU-NatashaNeural"),
    ("William – Australian male", "en-AU-WilliamNeural"),
    ("Ava – American female", "en-US-AvaNeural"),
    ("Emma – American female", "en-US-EmmaNeural"),
    ("Andrew – American male", "en-US-AndrewNeural"),
    ("Brian – American male", "en-US-BrianNeural"),
]
GTTS_VOICES = [("British accent", "co.uk"), ("American accent", "com"), ("Australian accent", "com.au")]


class EdgeEngine:
    key, label, ext = "edge", "Microsoft Edge Neural", ".mp3"
    available = staticmethod(lambda: _has("edge_tts"))

    @staticmethod
    def voices():
        return EDGE_VOICES

    @staticmethod
    def synth(text, voice, speed, path):
        import edge_tts
        rate = f"{int(round((speed - 1) * 100)):+d}%"

        async def run():
            await edge_tts.Communicate(text, voice, rate=rate).save(path)
        asyncio.run(run())


class GttsEngine:
    key, label, ext = "gtts", "Google gTTS", ".mp3"
    available = staticmethod(lambda: _has("gtts"))

    @staticmethod
    def voices():
        return GTTS_VOICES

    @staticmethod
    def synth(text, voice, speed, path):
        from gtts import gTTS
        gTTS(text=text, lang="en", tld=voice, slow=speed < 0.85).save(path)


class Pyttsx3Engine:
    key, label, ext = "pyttsx3", "Offline (Windows SAPI5)", ".wav"
    available = staticmethod(lambda: _has("pyttsx3"))

    @staticmethod
    def _com():
        try:
            import comtypes
            comtypes.CoInitialize()
        except Exception:  # noqa: BLE001
            pass

    @classmethod
    def voices(cls):
        import pyttsx3
        cls._com()
        eng = pyttsx3.init()
        res = [(v.name, v.id) for v in eng.getProperty("voices")]
        eng.stop()
        return res or [("Default", "")]

    @classmethod
    def synth(cls, text, voice, speed, path):
        import pyttsx3
        cls._com()
        eng = pyttsx3.init()
        if voice:
            eng.setProperty("voice", voice)
        eng.setProperty("rate", int(175 * speed))
        eng.save_to_file(text, path)
        eng.runAndWait()
        eng.stop()


ENGINES = {e.key: e for e in (EdgeEngine, GttsEngine, Pyttsx3Engine)}
