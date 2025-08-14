from dataclasses import dataclass
from typing import Optional, Any


from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    PrerecordedOptions,
    FileSource,
)


@dataclass
class STTOptions:
    model: str = "nova-2"
    language: str = "ru"
    smart_format: bool = True
    punctuate: bool = True
    paragraphs: bool = True
    utterances: bool = True


class DeepgramSpeech:
    def __init__(self, api_key: Optional[str] = None, verbose: Optional[int] = None):
        if api_key is None:
            api_key = "184d88e033362e8347aff7f5238e4d0d7e106a05"
        if not api_key:
            raise ValueError("DEEPGRAM_API_KEY не задан. Установите переменную окружения или передайте api_key в конструктор.")

        client_options: Optional[DeepgramClientOptions] = None
        if verbose is not None:
            client_options = DeepgramClientOptions(verbose=verbose)

        self._client: DeepgramClient = DeepgramClient(api_key, client_options)


    def transcribe_url(self, url: str, options: Optional[STTOptions] = None, return_text_only: bool = True) -> str | dict:
        opts = options or STTOptions()
        dg_opts = PrerecordedOptions(
            model=opts.model,
            language=opts.language,
            smart_format=opts.smart_format,
            punctuate=opts.punctuate,
            paragraphs=opts.paragraphs,
            utterances=opts.utterances,
        )
        response = self._client.listen.rest.v("1").transcribe_url({"url": url}, dg_opts)
        return self._extract_text(response) if return_text_only else response

    def transcribe_file(self, file_path: str, options: Optional[STTOptions] = None, return_text_only: bool = True) -> str | dict:
        opts = options or STTOptions()
        dg_opts = PrerecordedOptions(
            model=opts.model,
            language=opts.language,
            smart_format=opts.smart_format,
            punctuate=opts.punctuate,
            paragraphs=opts.paragraphs,
            utterances=opts.utterances,
        )
        with open(file_path, "rb") as f:
            buffer_data = f.read()
        payload: FileSource = {"buffer": buffer_data}
        response = self._client.listen.rest.v("1").transcribe_file(payload, dg_opts)
        return self._extract_text(response) if return_text_only else response


    def transcribe_bytes(self, data: bytes, options: Optional[STTOptions] = None, return_text_only: bool = True) -> str | dict:
        opts = options or STTOptions()
        dg_opts = PrerecordedOptions(
            model=opts.model,
            language=opts.language,
            smart_format=opts.smart_format,
            punctuate=opts.punctuate,
            paragraphs=opts.paragraphs,
            utterances=opts.utterances,
        )
        payload: FileSource = {"buffer": data}
        response = self._client.listen.rest.v("1").transcribe_file(payload, dg_opts)
        return self._extract_text(response) if return_text_only else response


    @staticmethod
    def _extract_text(response: Any) -> str:
        try:
            # SDK typed response
            if hasattr(response, "results"):
                results = response.results
                if not results or not getattr(results, "channels", None):
                    return ""
                first_channel = results.channels[0]
                alternatives = getattr(first_channel, "alternatives", [])
                if not alternatives:
                    return ""
                first_alternative = alternatives[0]
                paragraphs_obj = getattr(first_alternative, "paragraphs", None)
                if paragraphs_obj is not None:
                    para_text = getattr(paragraphs_obj, "transcript", None)
                    if para_text:
                        return para_text
                return getattr(first_alternative, "transcript", "") or ""

            # Fallback to dict-like
            if isinstance(response, dict):
                channels = response.get("results", {}).get("channels", [])
                if not channels:
                    return ""
                alternatives = channels[0].get("alternatives", [])
                if not alternatives:
                    return ""
                alt0 = alternatives[0]
                paragraphs_obj = alt0.get("paragraphs") if isinstance(alt0, dict) else None
                if isinstance(paragraphs_obj, dict):
                    para_text = paragraphs_obj.get("transcript")
                    if para_text:
                        return para_text
                return alt0.get("transcript", "")

            return ""
        except Exception:
            return ""
