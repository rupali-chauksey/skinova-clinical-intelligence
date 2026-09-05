import base64
import cv2
import json
import os
import re
from io import BytesIO

from dotenv import load_dotenv
from groq import Groq
from PIL import Image


load_dotenv()


def encode_image_for_groq(filepath):
    image = Image.open(filepath)
    image.thumbnail((1536, 1536))

    buffer = BytesIO()

    image.convert("RGB").save(
        buffer,
        format="JPEG",
        quality=85
    )

    return base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")



BODY_PART_LABELS = (
    "face",
    "scalp",
    "neck",
    "chest",
    "back",
    "arm",
    "hand",
    "leg",
    "foot",
    "abdomen",
    "other",
    "unknown",
)


def _extract_json_object(text):
    """Extract one JSON object from a model response."""
    text = (text or "").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise ValueError(
                "Body-part classifier did not return valid JSON."
            )
        return json.loads(match.group(0))


def classify_body_part(image_filepath):
    """
    Stage-1 routing classifier.

    This call does not diagnose the skin condition. It only identifies
    the dominant visible body area for deterministic image/video validation.
    """
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError(
            "Missing GROQ_API_KEY in .env or environment"
        )

    if not image_filepath:
        raise ValueError("An image is required for body-part classification.")

    image_data = encode_image_for_groq(image_filepath)

    prompt = (
        "Classify only the dominant visible body area in this image. "
        "This is a routing task, NOT a medical diagnosis. "
        "Choose exactly one label from: "
        + ", ".join(BODY_PART_LABELS)
        + ". "
        "Return ONLY valid JSON in exactly this format: "
        '{"body_part":"face","confidence":"high"}. '
        "body_part must be one of the allowed labels. "
        "confidence must be exactly high, medium, or low. "
        "Do not include markdown or explanation."
    )

    client = Groq(api_key=groq_api_key)

    response = client.chat.completions.create(
        model=os.environ.get(
            "GROQ_MODEL",
            "qwen/qwen3.6-27b"
        ),
        reasoning_effort="none",
        max_completion_tokens=120,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict body-part routing classifier. "
                    "Return JSON only. Never diagnose skin conditions."
                ),
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}"
                        },
                    },
                ],
            },
        ],
    )

    result = _extract_json_object(
        response.choices[0].message.content or ""
    )

    body_part = str(
        result.get("body_part", "unknown")
    ).strip().lower()

    confidence = str(
        result.get("confidence", "low")
    ).strip().lower()

    if body_part not in BODY_PART_LABELS:
        body_part = "unknown"

    # Normalize common model synonyms/verbose labels to the application's
    # deterministic routing labels.
    if body_part == "unknown":
        raw_lower = (response.choices[0].message.content or "").strip().lower()
        synonym_map = {
            "forehead": "face", "cheek": "face", "cheeks": "face",
            "nose": "face", "eye": "face", "eyes": "face",
            "jaw": "face", "chin": "face", "lip": "face", "lips": "face",
            "mouth": "face", "ear": "face", "ears": "face",
            "hair": "scalp", "head": "scalp",
            "shoulder": "arm", "upper arm": "arm",
            "wrist": "hand", "palm": "hand", "finger": "hand", "fingers": "hand",
            "thigh": "leg", "knee": "leg", "calf": "leg",
            "ankle": "foot", "toe": "foot", "toes": "foot", "sole": "foot",
            "belly": "abdomen", "stomach": "abdomen",
            "breast": "chest", "breasts": "chest",
        }
        for phrase, normalized in sorted(synonym_map.items(), key=lambda item: -len(item[0])):
            if re.search(rf"\b{re.escape(phrase)}\b", raw_lower):
                body_part = normalized
                break

    # Deterministic visual fallback for the most common case: face imagery.
    # This prevents a verbose/uncertain LLM routing response from turning an
    # obviously visible face into an 'unknown' mismatch.
    if body_part == "unknown":
        try:
            pil_img = Image.open(image_filepath).convert("RGB")
            frame = cv2.cvtColor(__import__("numpy").array(pil_img), cv2.COLOR_RGB2GRAY)
            cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )
            faces = cascade.detectMultiScale(
                frame, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
            )
            if len(faces) > 0:
                body_part = "face"
                confidence = "high"
        except Exception:
            pass

    if confidence not in {"high", "medium", "low"}:
        confidence = "low"

    return {
        "body_part": body_part,
        "confidence": confidence,
    }


def brain_of_the_doctor(
    patient_text,
    image_filepath=None,
    video_filepath=None
):
    groq_api_key = os.environ.get("GROQ_API_KEY")

    if not groq_api_key:
        raise ValueError(
            "Missing GROQ_API_KEY in .env or environment"
        )

    if not image_filepath:
        raise ValueError(
            "Groq vision requires an image. Please upload a skin image."
        )

    image_data = encode_image_for_groq(image_filepath)

    prompt = (
        "You are a professional, careful and reassuring AI skin-care assistant. "

        "The visual input may contain a labeled contact sheet. "
        "The panel labeled PATIENT IMAGE is the patient's still image. "
        "Panels labeled VIDEO FRAME are representative frames from the uploaded video. "

        "Your response must be concise, natural, patient-facing, and suitable for audio. "
        "Use 5 to 6 sentences when a matching video is available. "
        "Use 4 sentences when the video is missing. "

        "First, describe only visible findings. Mention only observations that are "
        "actually visible, such as redness, dryness, scaling, bumps, swelling, "
        "discoloration, or texture changes. Never invent symptoms. "

        "Second, briefly explain what the visible findings MAY be associated with. "
        "Use cautious language such as 'may be associated with' or "
        "'may be consistent with'. Never state a definitive diagnosis. "
        "Do not assign an exact severity such as mild, moderate, or severe unless "
        "the visual evidence clearly supports it. "

        "For a matching video, give simple temporary supportive precautions. "
        "Recommend gentle cleansing, avoiding harsh rubbing or hot water, and using "
        "a simple fragrance-free moisturizer when appropriate. For suitable dry or "
        "cracked areas, plain petroleum jelly may be mentioned as basic barrier support. "

        "Clearly tell the patient to avoid scratching, picking, squeezing, rubbing, "
        "scrubbing, harsh exfoliation, exfoliating acids, retinoids, alcohol-based "
        "products, fragrance-heavy products, and introducing multiple new active "
        "skincare products while the skin is irritated. "

        "Keep medical claims conservative. Do not say that bacteria will spread, "
        "that scarring or infection will definitely occur, or that a specific "
        "treatment is required. Prefer cautious wording such as 'may increase irritation'. "

        "Do not prescribe antibiotics, steroids, prescription medicines, or strong "
        "medicated treatments. Do not recommend a specific medical treatment plan. "

        "Mention professional evaluation in one short sentence when appropriate, "
        "such as when symptoms persist, worsen, spread, become significantly painful, "
        "or do not improve. "

        "Do not use markdown, bullets, headings, asterisks, emojis, or special "
        "formatting because the response will be converted to audio. "

        "Return only the final patient-facing response. "
        "Never reveal internal reasoning, hidden analysis, or chain of thought. "

        f"\\n\\nPatient text: {patient_text}"
    )

    if video_filepath:
        prompt += (
            "\\n\\nVIDEO STATUS: VIDEO AVAILABLE. "
            "The application has already performed explicit body-area validation "
            "before this medical-analysis stage. "
            "Assume the media is consistent and do not repeat frame-by-frame details. "
            "Provide the concise observation, cautious possible association, simple "
            "supportive precautions, things to avoid, and one short follow-up sentence. "
            "Do not mention internal validation logic to the patient."
        )
    else:
        prompt += (
            "\\n\\nVIDEO STATUS: VIDEO NOT AVAILABLE. "
            "Provide exactly four short sentences: one sentence describing the "
            "visible image findings, one sentence giving a cautious possible association, "
            "one sentence stating that no video was uploaded, and one sentence asking "
            "for a short video of the same affected area from multiple angles and "
            "under good lighting. "
            "Do not provide skincare advice, products, medications, home remedies, "
            "warning signs, or treatment guidance when the video is missing."
        )

    client = Groq(
        api_key=groq_api_key
    )

    response = client.chat.completions.create(
        model=os.environ.get(
            "GROQ_MODEL",
            "qwen/qwen3.6-27b"
        ),
        reasoning_effort="none",
        max_completion_tokens=520,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional AI skin-care assistant. "
                    "Follow the VIDEO STATUS branch exactly. "
                    "Keep the answer concise, cautious, patient-facing, and suitable for audio. "
                    "For a matching video, return 5 to 6 sentences covering visible findings, "
                    "a cautious possible association, supportive precautions, what to avoid, "
                    "and one short professional follow-up statement when appropriate. "
                    "For a missing video, return only four short sentences covering visible "
                    "findings, cautious association, video missing, and request for the correct video. "
                    "Do not provide definitive diagnoses, exact severity labels, prescription "
                    "medicines, antibiotics, steroids, or strong medicated treatments. "
                    "Avoid alarming or unsupported claims. Never invent symptoms. "
                    "Return only the final patient-facing answer."
                ),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": (
                                f"data:image/jpeg;base64,{image_data}"
                            )
                        },
                    },
                ],
            },
        ],
    )

    doctor_text = (
        response.choices[0].message.content or ""
    )

    doctor_text = re.sub(
        r"<think>.*?</think>",
        "",
        doctor_text,
        flags=re.DOTALL | re.IGNORECASE,
    ).strip()

    doctor_text = re.sub(
        r"</?think>",
        "",
        doctor_text,
        flags=re.IGNORECASE,
    ).strip()

    return doctor_text

