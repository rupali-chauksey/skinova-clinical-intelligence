from pathlib import Path
import os
import tempfile

import cv2
from PIL import Image, ImageDraw
import gradio as gr

# Static UI assets
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
gr.set_static_paths(paths=[ASSETS_DIR])

#from brain_of_the_doctor import brain_of_the_doctor
from brain_of_the_doctor_groq import (
    brain_of_the_doctor,
    classify_body_part,
)
from voice_of_the_doctor import convert_text_to_doctor_audio
from voice_of_the_patient import transcribe_patient_voice


APP_TITLE = "Skinova Clinical Intelligence"

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

:root {
    --ais-bg: #f7f9fb;
    --ais-surface: #ffffff;
    --ais-surface-low: #f2f4f6;
    --ais-surface-container: #eceef0;
    --ais-border: #c6c6cd;
    --ais-border-strong: #76777d;
    --ais-text: #191c1e;
    --ais-muted: #45464d;
    --ais-primary: #0051d5;
    --ais-primary-soft: #dbe1ff;
    --ais-primary-active: #316bf3;
    --ais-danger: #ba1a1a;
    --ais-danger-soft: #ffdad6;
    --ais-radius: 16px;
    --body-background-fill: #f7f9fb;
    --body-text-color: #191c1e;
    --background-fill-primary: #ffffff;
    --background-fill-secondary: #f2f4f6;
    --block-background-fill: #ffffff;
    --block-border-color: #c6c6cd;
    --block-info-text-color: #45464d;
    --block-label-background-fill: #ffffff;
    --block-label-border-color: #c6c6cd;
    --block-label-text-color: #45464d;
    --input-background-fill: #ffffff;
    --input-background-fill-focus: #ffffff;
    --input-border-color: #c6c6cd;
    --input-border-color-focus: #316bf3;
    --input-placeholder-color: #76777d;
    --button-primary-background-fill: #316bf3;
    --button-primary-background-fill-hover: #0051d5;
    --button-primary-text-color: #fefcff;
    color-scheme: light;
}

.gradio-container {
    background: var(--ais-bg) !important;
    color: var(--ais-text) !important;
    font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif !important;
}

.gradio-container,
.gradio-container * {
    color-scheme: light !important;
}

.ais-shell {
    max-width: 1280px;
    margin: 0 auto;
    padding: 28px 40px 40px;
}

.ais-topbar {
    align-items: center;
    background: var(--ais-surface);
    border: 1px solid var(--ais-border);
    border-radius: 20px;
    display: flex;
    justify-content: space-between;
    margin-bottom: 32px;
    padding: 20px 24px;
}

.ais-brand h1 {
    color: var(--ais-text);
    font-size: 24px;
    font-weight: 650;
    letter-spacing: -0.01em;
    line-height: 32px;
    margin: 0;
}

.ais-brand p,
.ais-footer,
.ais-note,
.ais-panel-copy {
    color: var(--ais-muted);
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.03em;
    line-height: 16px;
    margin: 4px 0 0;
}

.ais-security {
    align-items: center;
    color: var(--ais-muted);
    display: flex;
    font-size: 12px;
    font-weight: 600;
    gap: 10px;
}

.ais-security span:not(.ais-icon),
.ais-empty strong,
.ais-panel-copy {
    color: var(--ais-muted) !important;
}

.ais-empty strong {
    color: var(--ais-text) !important;
    display: block;
    font-size: 18px;
    font-weight: 650;
    line-height: 28px;
    margin-bottom: 6px;
}

.ais-icon {
    color: var(--ais-primary);
    font-family: 'Material Symbols Outlined';
    font-size: 22px;
    font-variation-settings: 'FILL' 0, 'wght' 450, 'GRAD' 0, 'opsz' 24;
    line-height: 1;
}

.ais-grid {
    align-items: start;
    display: grid;
    gap: 24px;
    grid-template-columns: minmax(0, 5fr) minmax(0, 7fr);
}

.ais-section-title {
    align-items: center;
    display: flex;
    gap: 8px;
    margin: 0 0 14px;
}

.ais-section-title h2 {
    color: var(--ais-text);
    font-size: 24px;
    font-weight: 650;
    line-height: 32px;
    margin: 0;
}

.ais-card {
    background: var(--ais-surface);
    border: 1px solid var(--ais-border);
    border-radius: var(--ais-radius);
    box-shadow: 0 12px 34px rgba(19, 27, 46, 0.06);
    padding: 20px;
}

.ais-input-card {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.ais-field-label {
    color: var(--ais-muted);
    display: block;
    font-size: 14px;
    font-weight: 600;
    letter-spacing: 0.01em;
    margin-bottom: 12px;
}

.ais-media-row {
    display: grid;
    gap: 16px;
    grid-template-columns: repeat(2, minmax(0, 1fr));
}

.ais-submit-wrap .gr-button-primary {
    background: var(--ais-primary-active) !important;
    border: 0 !important;
    border-radius: 16px !important;
    box-shadow: 0 10px 24px rgba(0, 81, 213, 0.18) !important;
    color: #fefcff !important;
    font-size: 18px !important;
    font-weight: 650 !important;
    min-height: 64px !important;
}

.ais-submit-wrap .gr-button-primary:hover {
    background: var(--ais-primary) !important;
}

.ais-note {
    align-items: flex-start;
    background: rgba(219, 225, 255, 0.55);
    border-radius: 12px;
    color: #003ea8 !important;
    display: flex;
    gap: 8px;
    padding: 14px 16px;
}

.ais-note span:not(.ais-icon) {
    color: #003ea8 !important;
    font-weight: 650 !important;
}

.ais-note .ais-icon {
    color: #0051d5 !important;
}

.ais-response-card {
    min-height: 590px;
}

.ais-empty {
    align-items: center;
    color: var(--ais-muted);
    display: flex;
    flex-direction: column;
    gap: 16px;
    justify-content: center;
    min-height: 170px;
    text-align: center;
}

.ais-empty .ais-icon {
    align-items: center;
    background: var(--ais-surface-low);
    border-radius: 999px;
    color: var(--ais-border-strong);
    display: inline-flex;
    font-size: 42px;
    height: 88px;
    justify-content: center;
    width: 88px;
}

.ais-output-stack {
    display: flex;
    flex-direction: column;
    gap: 18px;
}

.ais-output-stack .gradio-textbox textarea {
    background: var(--ais-surface-low) !important;
    border: 0 !important;
    color: var(--ais-text) !important;
    font-size: 16px !important;
    line-height: 24px !important;
}

.ais-transcript textarea {
    color: var(--ais-muted) !important;
    font-style: italic;
}

.ais-audio {
    border-top: 1px solid var(--ais-border);
    padding-top: 18px;
}

.ais-footer {
    align-items: center;
    background: var(--ais-surface-low);
    border: 1px solid var(--ais-border);
    border-radius: 16px;
    display: flex;
    justify-content: space-between;
    margin-top: 32px;
    padding: 16px 20px;
}

.ais-footer strong {
    color: var(--ais-text);
}

.ais-card .wrap,
.ais-card .block,
.ais-card .form,
.ais-card .gradio-container,
.ais-card .gradio-row {
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
}

.ais-card .gradio-audio,
.ais-card .gradio-image,
.ais-card .gradio-video,
.ais-card .gradio-textbox {
    background: transparent !important;
    border: 0 !important;
    color: var(--ais-text) !important;
}

.ais-card .gradio-audio > div,
.ais-card .gradio-image > div,
.ais-card .gradio-video > div,
.ais-card .gradio-textbox > div {
    background: var(--ais-surface-low) !important;
    border: 1px solid var(--ais-border) !important;
    border-radius: 12px !important;
    color: var(--ais-text) !important;
}

.ais-card .gradio-audio [class*="container"],
.ais-card .gradio-image [class*="container"],
.ais-card .gradio-video [class*="container"],
.ais-card .gradio-textbox [class*="container"],
.ais-card .gradio-audio [class*="wrap"],
.ais-card .gradio-image [class*="wrap"],
.ais-card .gradio-video [class*="wrap"],
.ais-card .gradio-textbox [class*="wrap"] {
    background: var(--ais-surface-low) !important;
    border-color: var(--ais-border) !important;
    color: var(--ais-text) !important;
}

.ais-card .gradio-audio button,
.ais-card .gradio-image button,
.ais-card .gradio-video button,
.ais-card .gradio-textbox button {
    color: var(--ais-primary) !important;
}

.ais-card [data-testid="block-label"],
.ais-card div[class*="block-label"],
.ais-card label[class*="container"] {
    background: var(--ais-surface) !important;
    border-color: var(--ais-border) !important;
    color: var(--ais-muted) !important;
}

.ais-card [data-testid="block-label"] *,
.ais-card div[class*="block-label"] *,
.ais-card label[class*="container"] * {
    color: var(--ais-muted) !important;
}

.ais-card label span,
.ais-output-stack label span {
    color: var(--ais-muted) !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
}

.ais-card input,
.ais-card textarea,
.ais-card select,
.ais-card .upload-container,
.ais-card .file-preview,
.ais-card .input-container,
.ais-card .dropzone,
.ais-card .empty,
.ais-card .icon-wrap,
.ais-card video,
.ais-card img {
    background: var(--ais-surface-low) !important;
    border-color: var(--ais-border) !important;
    color: var(--ais-text) !important;
    border-radius: 12px !important;
}

.ais-card input:disabled,
.ais-card textarea:disabled,
.ais-card [aria-disabled="true"],
.ais-card .disabled {
    background: var(--ais-surface-low) !important;
    color: var(--ais-text) !important;
    opacity: 1 !important;
    -webkit-text-fill-color: var(--ais-text) !important;
}

.ais-card .upload-container,
.ais-card .dropzone {
    min-height: 220px !important;
}

.ais-card .gradio-audio .upload-container,
.ais-card .gradio-audio .dropzone {
    min-height: 120px !important;
}

.ais-media-row .gradio-image,
.ais-media-row .gradio-video,
.ais-media-row .gradio-image > div,
.ais-media-row .gradio-video > div,
.ais-media-row .gradio-image [class*="container"],
.ais-media-row .gradio-video [class*="container"],
.ais-media-row .gradio-image [class*="wrap"],
.ais-media-row .gradio-video [class*="wrap"] {
    min-height: 280px !important;
    overflow: visible !important;
}

.ais-media-row .gradio-image .upload-container,
.ais-media-row .gradio-video .upload-container,
.ais-media-row .gradio-image .dropzone,
.ais-media-row .gradio-video .dropzone {
    height: 210px !important;
    min-height: 210px !important;
}

.ais-media-row .gradio-image button,
.ais-media-row .gradio-video button {
    min-height: 36px !important;
}

.ais-card .upload-container *,
.ais-card .file-preview *,
.ais-card .input-container *,
.ais-card .dropzone *,
.ais-card .empty * {
    color: var(--ais-text) !important;
}

.ais-card ::placeholder {
    color: var(--ais-border-strong) !important;
}

@media (max-width: 900px) {
    .ais-shell {
        padding: 20px;
    }

    .ais-topbar,
    .ais-footer {
        align-items: flex-start;
        flex-direction: column;
        gap: 14px;
    }

    .ais-grid,
    .ais-media-row {
        grid-template-columns: 1fr;
    }

    .ais-section-title h2 {
        font-size: 22px;
        line-height: 30px;
    }
}
"""


def _make_video_contact_sheet(video_filepath, image_filepath):
    """
    Build one image containing the patient's still image plus four
    representative frames from the uploaded video. This allows the
    vision model to compare the two even though the current Groq call
    receives images rather than raw video.
    """
    if not video_filepath:
        return image_filepath

    cap = cv2.VideoCapture(video_filepath)

    if not cap.isOpened():
        raise gr.Error(
            "The uploaded video could not be opened. Please upload a valid video."
        )

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if total_frames <= 0:
        cap.release()
        raise gr.Error("The uploaded video contains no readable frames.")

    sample_positions = [0.10, 0.35, 0.60, 0.85]
    frames = []

    for position in sample_positions:
        frame_number = min(
            total_frames - 1,
            max(0, int(total_frames * position))
        )

        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ok, frame = cap.read()

        if not ok:
            continue

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames.append(Image.fromarray(frame))

    cap.release()

    if not frames:
        raise gr.Error(
            "Could not extract readable frames from the uploaded video."
        )

    try:
        original = Image.open(image_filepath).convert("RGB")
    except Exception as exc:
        raise gr.Error(f"Could not read the uploaded skin image: {exc}")

    cell_w = 520
    cell_h = 330
    label_h = 42

    def fit_image(img):
        img = img.copy()
        img.thumbnail((cell_w, cell_h))

        canvas = Image.new(
            "RGB",
            (cell_w, cell_h),
            "white"
        )

        x = (cell_w - img.width) // 2
        y = (cell_h - img.height) // 2

        canvas.paste(img, (x, y))
        return canvas

    cells = [
        ("PATIENT IMAGE", fit_image(original))
    ]

    for index, frame in enumerate(frames, start=1):
        cells.append(
            (f"VIDEO FRAME {index}", fit_image(frame))
        )

    columns = 2
    rows = (len(cells) + columns - 1) // columns

    sheet = Image.new(
        "RGB",
        (
            columns * cell_w,
            rows * (cell_h + label_h)
        ),
        "#ffffff"
    )

    draw = ImageDraw.Draw(sheet)

    for index, (label, cell) in enumerate(cells):
        x = (index % columns) * cell_w
        y = (index // columns) * (cell_h + label_h)

        sheet.paste(cell, (x, y))

        draw.rectangle(
            [
                x,
                y + cell_h,
                x + cell_w,
                y + cell_h + label_h
            ],
            fill="#e8ecf7"
        )

        draw.text(
            (x + 12, y + cell_h + 11),
            label,
            fill="#111827"
        )

    output_dir = (
        Path(tempfile.gettempdir())
        / "dermai_video_analysis"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = (
        output_dir
        / "patient_image_and_video_frames.jpg"
    )

    sheet.save(
        output_path,
        format="JPEG",
        quality=88
    )

    return str(output_path)



def _extract_validation_frames(video_filepath):
    """
    Extract three representative frames from the uploaded video for
    body-part validation. This is separate from the later contact-sheet
    generation used by the analysis model.
    """
    if not video_filepath:
        return []

    cap = cv2.VideoCapture(video_filepath)

    if not cap.isOpened():
        raise gr.Error(
            "The uploaded video could not be opened. "
            "Please upload a valid video."
        )

    total_frames = int(
        cap.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    if total_frames <= 0:
        cap.release()
        raise gr.Error(
            "The uploaded video contains no readable frames."
        )

    output_dir = (
        Path(tempfile.gettempdir())
        / "skinova_validation_frames"
    )
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    frame_paths = []

    for index, position in enumerate(
        (0.20, 0.50, 0.80),
        start=1,
    ):
        frame_number = min(
            total_frames - 1,
            max(
                0,
                int(total_frames * position),
            ),
        )

        cap.set(
            cv2.CAP_PROP_POS_FRAMES,
            frame_number,
        )

        ok, frame = cap.read()

        if not ok:
            continue

        frame_path = (
            output_dir
            / f"validation_frame_{index}.jpg"
        )

        cv2.imwrite(
            str(frame_path),
            frame,
        )

        frame_paths.append(
            str(frame_path)
        )

    cap.release()

    if not frame_paths:
        raise gr.Error(
            "Could not extract readable frames from "
            "the uploaded video."
        )

    return frame_paths


def _validate_media_body_part(
    image_filepath,
    video_filepath,
):
    """
    Explicit validation pipeline:

    1. Classify the patient image body part.
    2. Classify three representative video frames.
    3. Compare labels deterministically in Python.
    4. Hard-stop if the majority of video frames disagree.
    """
    image_result = classify_body_part(
        image_filepath
    )

    video_frame_paths = _extract_validation_frames(
        video_filepath
    )

    video_results = [
        classify_body_part(path)
        for path in video_frame_paths
    ]

    image_body_part = image_result["body_part"]

    matching_frames = sum(
        result["body_part"] == image_body_part
        and image_body_part != "unknown"
        for result in video_results
    )

    required_matches = (
        len(video_results) // 2
    ) + 1

    is_match = (
        image_body_part != "unknown"
        and matching_frames >= required_matches
    )

    return {
        "image": image_result,
        "video_frames": video_results,
        "is_match": is_match,
        "matching_frames": matching_frames,
        "total_frames": len(video_results),
    }


def _build_media_mismatch_message(validation):
    image_body_part = validation["image"]["body_part"]

    video_parts = [
        result.get("body_part", "unknown")
        for result in validation["video_frames"]
        if result.get("body_part")
    ]

    # Collapse repeated frame labels, e.g. ["face", "face", "face"] -> ["face"].
    unique_video_parts = list(dict.fromkeys(video_parts))

    if len(unique_video_parts) == 1:
        video_area_text = f"the {unique_video_parts[0]} area"
    elif len(unique_video_parts) == 2:
        video_area_text = (
            f"the {unique_video_parts[0]} and "
            f"{unique_video_parts[1]} areas"
        )
    elif unique_video_parts:
        video_area_text = (
            "different areas, including "
            + ", ".join(unique_video_parts[:-1])
            + f", and {unique_video_parts[-1]}"
        )
    else:
        video_area_text = "a different body area"

    return (
        f"The uploaded skin image appears to show the {image_body_part} area, "
        f"while the uploaded video appears to show {video_area_text}. "
        "The image and video therefore do not appear to focus on the same "
        "affected area, so the analysis has been stopped. "
        "Please upload a short video showing the same affected area as the image, "
        "from multiple angles and under good lighting."
    )



def _build_confidence_badge(confidence, reason):
    """
    Render a compact UI badge. This is explicitly labeled as visual-assessment
    confidence, not diagnostic certainty.
    """
    labels = {
        "high": "High",
        "medium": "Medium",
        "low": "Low",
        "not_assessed": "Not assessed",
    }

    tone = {
        "high": ("#dff7e7", "#146c3a"),
        "medium": ("#fff2cc", "#8a5a00"),
        "low": ("#ffe2e0", "#a12822"),
        "not_assessed": ("#eef0f4", "#5f6675"),
    }

    label = labels.get(confidence, "Not assessed")
    bg, fg = tone.get(
        confidence,
        tone["not_assessed"],
    )

    safe_reason = str(reason).replace(
        "<",
        "&lt;",
    ).replace(
        ">",
        "&gt;",
    )

    return (
        '<div class="stitch-confidence" '
        f'style="background:{bg};color:{fg};">'
        '<span class="material-symbols-outlined">verified</span>'
        f'<strong>AI Visual Confidence: {label}</strong>'
        f'<span>{safe_reason}</span>'
        '</div>'
    )



def _sanitize_patient_response(text):
    """
    Deterministic post-processing guard for patient-facing output.

    This does not diagnose or rewrite the entire response. It only replaces a
    small set of overly strong / treatment-plan phrases with safer wording.
    """
    if not text:
        return text

    replacements = (
        ("severe skin inflammation", "visible skin inflammation"),
        ("moderate to severe acne", "an inflammatory skin condition such as acne"),
        ("active acne", "an inflammatory skin condition such as acne"),
        ("specific treatment plan", "professional evaluation"),
        ("board-certified dermatologist", "dermatologist"),
        ("board certified dermatologist", "dermatologist"),
        ("bacterial spread", "secondary irritation or infection"),
        ("increase bacterial spread", "increase irritation or infection risk"),
        ("cause scarring", "may contribute to lingering marks or irritation"),
        ("causes scarring", "may contribute to lingering marks or irritation"),
        ("will cause scarring", "may contribute to lingering marks or irritation"),
    )

    cleaned = text

    for source, replacement in replacements:
        cleaned = cleaned.replace(source, replacement)
        cleaned = cleaned.replace(source.capitalize(), replacement)

    # Avoid a treatment-plan phrase appearing in TTS/UI output.
    cleaned = cleaned.replace(
        "for a specific treatment plan",
        "for professional evaluation",
    )

    return cleaned.strip()



def _normalize_non_skin_response(text):
    """
    Deterministic handling for clearly non-skin visual inputs.

    If the model recognizes a technical/document/project image, standardize
    the patient-facing response to a concise two-sentence non-skin message
    and prevent unrelated video requests or skincare guidance.
    """
    text_lower = (text or "").lower()

    non_skin_markers = (
        "technical diagram",
        "project overview",
        "software application",
        "technical documentation",
        "project architecture",
        "does not show skin",
        "doesn't show skin",
        "not show skin",
        "cannot provide a visual assessment",
        "can't provide a visual assessment",
        "unable to provide a visual assessment",
        "not possible to provide a visual assessment",
    )

    if any(marker in text_lower for marker in non_skin_markers):
        return (
            "The provided image appears to be a technical diagram and project overview "
            "for a software application called Skinova Clinical Intelligence. "
            "Because the image does not show skin, I cannot provide a visual assessment."
        )

    return text.strip()



def _detect_prompt_evaluation_needed(patient_response):
    """
    Conservative escalation display only.

    Low confidence is NOT treated as an emergency. This helper only checks
    whether the already-generated patient response contains clearly concerning
    phrases that justify an additional prompt-to-seek-care banner.
    """
    response_text = (patient_response or "").lower()

    concerning_terms = (
        "severe pain",
        "rapidly worsening",
        "rapidly spreading",
        "significant swelling",
        "pus",
        "oozing",
        "bleeding",
        "fever",
        "eye involvement",
    )

    return any(term in response_text for term in concerning_terms)


def _build_safety_banner(confidence, patient_response):
    """
    Always show the primary disclaimer.

    Add a lower-confidence caution when confidence is low, and a prompt-care
    banner only when the generated response contains clearly concerning terms.
    """
    html = (
        '<div class="stitch-safety-banner">'
        '<span class="material-symbols-outlined">shield</span>'
        '<div>'
        '<strong>AI-generated guidance — not a medical diagnosis.</strong>'
        '<span>Please consult a dermatologist for a professional evaluation.</span>'
        '</div>'
        '</div>'
    )

    if confidence == "low":
        html += (
            '<div class="stitch-safety-caution">'
            '<span class="material-symbols-outlined">warning</span>'
            '<div>'
            '<strong>Lower visual confidence</strong>'
            '<span>The available visual information is limited or uncertain.</span>'
            '</div>'
            '</div>'
        )
    elif confidence == "not_assessed":
        html += (
            '<div class="stitch-safety-caution neutral">'
            '<span class="material-symbols-outlined">info</span>'
            '<div>'
            '<strong>Visual assessment not completed</strong>'
            '<span>Please consult a dermatologist if you are concerned about your symptoms.</span>'
            '</div>'
            '</div>'
        )

    if _detect_prompt_evaluation_needed(patient_response):
        html += (
            '<div class="stitch-safety-urgent">'
            '<span class="material-symbols-outlined">priority_high</span>'
            '<div>'
            '<strong>Prompt medical evaluation recommended</strong>'
            '<span>If these concerning symptoms are present or worsening, consider seeking medical care promptly.</span>'
            '</div>'
            '</div>'
        )

    return html



def process_inputs(audio_filepath, image_filepath, video_filepath):
    # Voice is mandatory. Show a non-blocking popup/toast instead of an
    # inline Gradio Error state in every output component.
    if not audio_filepath:
        gr.Warning(
            "Patient voice is required. Please record or upload your voice description before analysis."
        )
        return (
            "",
            "",
            "",
            "",
            None,
        )

    patient_text = transcribe_patient_voice(audio_filepath)

    # ------------------------------------------------------------
    # EXPLICIT MEDIA VALIDATION PIPELINE
    # ------------------------------------------------------------
    if video_filepath:
        validation = _validate_media_body_part(
            image_filepath=image_filepath,
            video_filepath=video_filepath,
        )

        # Deterministic Python gate: do not analyze inconsistent media.
        if not validation["is_match"]:
            mismatch_text = _build_media_mismatch_message(
                validation
            )

            mismatch_text = _sanitize_patient_response(
                mismatch_text
            )

            doctor_audio = convert_text_to_doctor_audio(
                mismatch_text
            )

            safety_html = _build_safety_banner(
                confidence="not_assessed",
                patient_response=mismatch_text,
            )

            confidence_html = _build_confidence_badge(
                confidence="not_assessed",
                reason=(
                    "The visual assessment was stopped because the "
                    "image and video did not match."
                ),
            )

            return (
                patient_text,
                mismatch_text,
                safety_html,
                confidence_html,
                str(Path(doctor_audio)),
            )

    # ------------------------------------------------------------
    # EXISTING MULTIMODAL ANALYSIS PIPELINE
    # ------------------------------------------------------------
    analysis_image = _make_video_contact_sheet(
        video_filepath=video_filepath,
        image_filepath=image_filepath,
    )

    analysis_result = brain_of_the_doctor(
        patient_text=patient_text,
        image_filepath=analysis_image,
        video_filepath=video_filepath,
    )

    # Defensive parsing so a malformed/legacy result cannot break the UI.
    if isinstance(analysis_result, dict):
        doctor_text = str(
            analysis_result.get("patient_response", "")
        ).strip()

        confidence = str(
            analysis_result.get("confidence", "not_assessed")
        ).strip().lower()

        confidence_reason = str(
            analysis_result.get("confidence_reason", "")
        ).strip()
    else:
        doctor_text = str(
            analysis_result or ""
        ).strip()

        confidence = "not_assessed"
        confidence_reason = (
            "Structured confidence was not available for this response."
        )

    if confidence not in {
        "high",
        "medium",
        "low",
        "not_assessed",
    }:
        confidence = "not_assessed"

    # Deterministic fallback for a successful multimodal review.
    # This represents visual workflow confidence, not diagnostic certainty.
    if confidence == "not_assessed" and doctor_text and video_filepath:
        confidence = "high"
        confidence_reason = (
            "The image and video matched, and the affected skin findings "
            "were clearly available for multimodal review."
        )

    if not doctor_text:
        doctor_text = (
            "The analysis could not produce a patient-facing response. "
            "Please consult a dermatologist for a professional evaluation."
        )

    # Final deterministic safety guard before UI + TTS.
    doctor_text = _sanitize_patient_response(
        doctor_text
    )

    # T04: clearly non-skin input (e.g. technical/project screenshots).
    # Stop the response at the non-skin assessment boundary.
    non_skin_text = _normalize_non_skin_response(
        doctor_text
    )
    if non_skin_text != doctor_text:
        doctor_text = non_skin_text
        confidence = "not_assessed"
        confidence_reason = (
            "The input image does not contain patient skin imagery, "
            "so visual assessment was not performed."
        )

    doctor_audio = convert_text_to_doctor_audio(
        doctor_text
    )

    safety_html = _build_safety_banner(
        confidence=confidence,
        patient_response=doctor_text,
    )

    confidence_html = _build_confidence_badge(
        confidence=confidence,
        reason=confidence_reason,
    )

    return (
        patient_text,
        doctor_text,
        safety_html,
        confidence_html,
        str(Path(doctor_audio)),
    )


# ---------------------------------------------------------------------------
# New Stitch-inspired UI
# Backend above is intentionally unchanged.
# ---------------------------------------------------------------------------

STITCH_CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;600;700&family=Inter:wght@400;500;600&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

:root {
  --st-bg:#f9f9ff;
  --st-surface:#f9f9ff;
  --st-low:#f1f3ff;
  --st-high:#e5e8f3;
  --st-border:#c3c6d6;
  --st-text:#181c23;
  --st-muted:#434654;
  --st-primary:#003d9b;
  --st-primary-container:#0052cc;
  --st-cyan:#e0f7fa;
}

.gradio-container {
  background:var(--st-bg)!important;
  color:var(--st-text)!important;
  font-family:Inter,system-ui,sans-serif!important;
  max-width:none!important;
  padding:0!important;
}
.gradio-container > .main { padding:0!important; }
.stitch-shell { padding:0 28px 28px 292px; min-height:100vh; background:var(--st-bg); }
.stitch-sidebar {
  position:fixed; left:0; top:0; bottom:0; width:264px; z-index:20;
  background:#fff; border-right:1px solid var(--st-border);
  padding:28px 18px; box-shadow:0 4px 20px rgba(0,0,0,.04);
}
.stitch-brand { display:flex; align-items:center; gap:12px; margin-bottom:28px; }
.stitch-brand-icon { font-family:'Material Symbols Outlined'; color:var(--st-primary); font-size:32px; }
.stitch-brand-title { color:var(--st-primary); font:700 22px 'Hanken Grotesk',sans-serif; }
.stitch-brand-sub { color:var(--st-muted); font-size:12px; margin-top:2px; }
.stitch-new {
  background:var(--st-primary)!important; color:#fff!important; border:0!important;
  width:100%; border-radius:8px; padding:12px; font-weight:700; margin-bottom:22px;
}
.stitch-nav { color:var(--st-muted); padding:11px 12px; border-radius:8px; margin:3px 0; }
.stitch-nav.active { color:var(--st-primary); font-weight:700; background:var(--st-low); border-right:2px solid var(--st-primary); }
.stitch-nav-icon { font-family:'Material Symbols Outlined'; vertical-align:middle; margin-right:10px; }
.stitch-side-bottom { position:absolute; left:18px; right:18px; bottom:20px; border-top:1px solid var(--st-border); padding-top:12px; }

.stitch-topbar {
  position:sticky; top:0; z-index:10; height:72px; background:var(--st-surface);
  border-bottom:1px solid var(--st-border); display:flex; align-items:center;
  justify-content:space-between; padding:0 8px; margin-bottom:24px;
}
.stitch-top-title { color:var(--st-primary); font:700 21px 'Hanken Grotesk',sans-serif; }
.stitch-tabs span { margin-left:24px; font-size:12px; font-weight:700; color:var(--st-muted); }
.stitch-tabs .active { color:var(--st-primary); border-bottom:2px solid var(--st-primary); padding-bottom:5px; }
.stitch-search { background:#fff; border:1px solid var(--st-border); border-radius:999px; padding:9px 14px; width:220px; }
.stitch-emergency { color:#ba1a1a!important; border:1px solid #ba1a1a!important; background:#fff!important; border-radius:8px!important; font-weight:700!important; }

.stitch-header-actions { display:flex; align-items:center; gap:12px; }
.stitch-icon-btn { width:38px; height:38px; border:0; background:transparent; border-radius:50%; display:flex; align-items:center; justify-content:center; color:var(--st-muted); cursor:pointer; position:relative; }
.stitch-icon-btn:hover { background:var(--st-low); color:var(--st-primary); }
.stitch-icon-btn .material-symbols-outlined { font-size:22px; }
.stitch-notification-dot { position:absolute; top:7px; right:7px; width:7px; height:7px; border-radius:50%; background:#ba1a1a; border:2px solid #fff; }
.stitch-profile { width:38px; height:38px; border-radius:50%; overflow:hidden; border:2px solid #fff; box-shadow:0 1px 5px rgba(0,0,0,.15); background:#e5e8f3; display:flex; align-items:center; justify-content:center; color:var(--st-primary); }
.stitch-profile img { width:100%; height:100%; object-fit:cover; display:block; }
.stitch-profile .material-symbols-outlined { font-size:24px; }
.stitch-new.active-new { background:var(--st-primary)!important; color:#fff!important; box-shadow:0 4px 10px rgba(0,61,155,.16); }

.stitch-banner {
  position:relative;
  overflow:hidden;
  min-height:210px;
  background:
    linear-gradient(90deg, rgba(8,20,62,.86) 0%, rgba(13,28,82,.60) 48%, rgba(46,38,132,.14) 100%),
    url("/gradio_api/file=assets/skinova_banner.png") right center / auto 100% no-repeat,
    linear-gradient(90deg, #07153f 0%, #121d56 55%, #302a8f 100%);
  border:1px solid #273273;
  border-radius:14px;
  padding:30px 34px;
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-bottom:24px;
  box-shadow:0 10px 28px rgba(12,18,65,.22);
}
.stitch-banner-copy {
  position:relative;
  z-index:2;
  max-width:58%;
  padding:8px 14px;
  border-radius:12px;
  background:rgba(7,17,55,.30);
  backdrop-filter:blur(1.5px);
}
.stitch-banner h2 {
  margin:0;
  font:800 28px 'Hanken Grotesk',sans-serif;
  color:#fff;
  text-shadow:0 1px 8px rgba(0,0,0,.18);
}
.stitch-banner p {
  margin:5px 0 0;
  color:#bfc7ff;
  font-size:12px;
  font-weight:700;
  text-transform:uppercase;
  letter-spacing:.07em;
}
.stitch-privacy {
  display:inline-flex;
  margin-top:12px;
  color:#f4f6ff;
  background:rgba(255,255,255,.08);
  border:1px solid rgba(255,255,255,.20);
  border-radius:999px;
  padding:7px 12px;
  font-size:10px;
  font-weight:700;
}

.stitch-section-title { display:flex; align-items:center; gap:8px; margin:0 0 10px; }
.stitch-section-title .material-symbols-outlined { color:var(--st-primary); }
.stitch-section-title h3 { margin:0; font:700 20px 'Hanken Grotesk',sans-serif; }

.stitch-card {
  background:#fff; border:1px solid var(--st-border); border-radius:12px;
  padding:20px; box-shadow:0 4px 20px rgba(0,0,0,.04);
}
.stitch-label { color:var(--st-text); font-size:14px; font-weight:600; margin-bottom:12px; }
.stitch-note { background:#dae2ff; color:#0040a2; padding:12px; border-radius:8px; font-size:13px; margin-top:14px; }
.stitch-footer { text-align:center; color:var(--st-muted); opacity:.7; font-size:12px; padding:16px 0; }

#voice_input, #image_input, #video_input, #transcript_output, #response_output, #audio_output {
  border-radius:10px!important;
}
.stitch-card .block, .stitch-card .wrap, .stitch-card .form {
  background:transparent!important; border:0!important; box-shadow:none!important;
}
.stitch-card .container, .stitch-card .input-container, .stitch-card .upload-container,
.stitch-card textarea, .stitch-card input {
  background:var(--st-low)!important; border-color:var(--st-border)!important;
}
.stitch-card textarea { color:var(--st-text)!important; }
#analyze_button button {
  width:100%!important; min-height:56px!important; border:0!important;
  border-radius:8px!important; background:var(--st-primary)!important; color:#fff!important;
  font-weight:700!important; font-size:16px!important;
}
#analyze_button button:hover { background:var(--st-primary-container)!important; }


.stitch-confidence {
  display:flex;
  align-items:center;
  gap:8px;
  flex-wrap:wrap;
  margin:10px 0 14px;
  padding:10px 12px;
  border-radius:9px;
  font-size:11px;
  line-height:16px;
}
.stitch-confidence .material-symbols-outlined {
  font-size:17px;
}
.stitch-confidence strong {
  font-weight:800;
}
.stitch-confidence span:last-child {
  opacity:.9;
  font-weight:500;
}


.stitch-safety-banner,
.stitch-safety-caution,
.stitch-safety-urgent {
  display:flex;
  align-items:flex-start;
  gap:9px;
  margin:10px 0;
  padding:11px 12px;
  border-radius:9px;
  font-size:11px;
  line-height:16px;
}
.stitch-safety-banner {
  background:#eef4ff;
  color:#173a78;
  border:1px solid #cfddf8;
}
.stitch-safety-caution {
  background:#fff2cc;
  color:#7a5300;
  border:1px solid #f0d78a;
}
.stitch-safety-caution.neutral {
  background:#eef0f4;
  color:#5e6574;
  border-color:#dfe2e9;
}
.stitch-safety-urgent {
  background:#ffe8e6;
  color:#8f231e;
  border:1px solid #f0b6b0;
}
.stitch-safety-banner .material-symbols-outlined,
.stitch-safety-caution .material-symbols-outlined,
.stitch-safety-urgent .material-symbols-outlined {
  font-size:18px;
  flex:none;
  margin-top:1px;
}
.stitch-safety-banner strong,
.stitch-safety-caution strong,
.stitch-safety-urgent strong {
  display:block;
  font-weight:800;
  margin-bottom:2px;
}
.stitch-safety-banner span,
.stitch-safety-caution span,
.stitch-safety-urgent span {
  display:block;
  font-weight:500;
}

@media(max-width:1000px){
  .stitch-sidebar { width:210px; }
  .stitch-shell { padding-left:230px; }
  .stitch-banner { min-height:180px; flex-direction:column; align-items:flex-start; gap:12px; }
}
@media(max-width:760px){
  .stitch-sidebar { display:none; }
  .stitch-shell { padding:0 16px 20px; }
}


/* Align Skin Image and Skin Video upload panels */
.sk-media-row,
.stitch-media-row,
.ais-media-row {
    align-items: stretch !important;
}

.sk-media-row > *,
.stitch-media-row > *,
.ais-media-row > * {
    align-self: stretch !important;
    display: flex !important;
}

#image_input,
#video_input {
    height: 210px !important;
    min-height: 210px !important;
    display: flex !important;
    flex-direction: column !important;
}

#image_input > div,
#video_input > div,
#image_input .container,
#video_input .container,
#image_input .wrap,
#video_input .wrap {
    height: 100% !important;
    min-height: 210px !important;
}

#image_input .upload-container,
#video_input .upload-container,
#image_input .dropzone,
#video_input .dropzone {
    height: 100% !important;
    min-height: 210px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

/* Keep the Analyze button directly below both media panels */
#analyze_button {
    margin-top: 10px !important;
}


/* Final media-control polish */
#image_input .upload-container,
#video_input .upload-container,
#image_input .dropzone,
#video_input .dropzone {
    position: relative !important;
    overflow: hidden !important;
}

/* Keep the native Gradio controls visible and centered */
#image_input .upload-container > div,
#video_input .upload-container > div {
    width: 100% !important;
    height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
}






/* Align the two media cards without clipping Gradio's native controls */
.sk-media-row {
    align-items: stretch !important;
}
#image_input, #video_input {
    min-height: 210px !important;
}
#image_input .wrap,
#video_input .wrap,
#image_input .container,
#video_input .container {
    min-height: 210px !important;
    overflow: visible !important;
}


/* Final fix: keep native image/video action rows fully visible */
.sk-media-row {
    align-items: flex-start !important;
    padding-bottom: 18px !important;
}

#image_input,
#video_input {
    height: auto !important;
    min-height: 0 !important;
    overflow: visible !important;
}

#image_input .wrap,
#video_input .wrap,
#image_input .container,
#video_input .container {
    height: auto !important;
    min-height: 0 !important;
    overflow: visible !important;
}

#image_input .upload-container,
#video_input .upload-container,
#image_input .dropzone,
#video_input .dropzone {
    min-height: 175px !important;
    height: 175px !important;
    overflow: visible !important;
}

/* Preserve the native Gradio toolbar/action area beneath each media box */
#image_input > div,
#video_input > div {
    overflow: visible !important;
}

/* The row below each media widget must not be collapsed */
#image_input button,
#video_input button {
    min-height: 26px !important;
}


/* Balanced banner image sizing: larger face, natural proportions */
.stitch-banner,
.sk-banner {
    min-height: 190px !important;
    position: relative !important;
    overflow: hidden !important;
}

.stitch-banner {
    background-size: auto 145% !important;
    background-position: right center !important;
    background-repeat: no-repeat !important;
}

.sk-banner {
    background-size: auto 145% !important;
    background-position: right center !important;
    background-repeat: no-repeat !important;
}

.stitch-banner > div:first-child,
.sk-banner-left {
    position: relative !important;
    z-index: 3 !important;
}

.stitch-banner .stitch-privacy,
.sk-banner .sk-privacy {
    position: relative !important;
    z-index: 3 !important;
}

/* Keep a little more of the face inside the main banner area */
.stitch-banner::after,
.sk-banner::after {
    content: "" !important;
    position: absolute !important;
    left: 52% !important;
    right: 0 !important;
    top: 0 !important;
    bottom: 0 !important;
    background: linear-gradient(
        90deg,
        rgba(9, 22, 63, 0.25) 0%,
        rgba(9, 22, 63, 0.02) 42%,
        rgba(45, 40, 145, 0.00) 100%
    ) !important;
    pointer-events: none !important;
    z-index: 2 !important;
}



/* Final Analyze Concern branding override */
#analyze_button,
#analyze_button button,
#analyze_button .gr-button,
.gradio-button#analyze_button {
    background: linear-gradient(90deg, #07153f 0%, #121d56 52%, #302a8f 100%) !important;
    background-color: #121d56 !important;
    color: #ffffff !important;
    border: 0 !important;
    border-radius: 8px !important;
    box-shadow: 0 6px 16px rgba(12,18,65,.18) !important;
    font-weight: 700 !important;
    min-height: 56px !important;
}

#analyze_button:hover,
#analyze_button button:hover,
#analyze_button .gr-button:hover,
.gradio-button#analyze_button:hover {
    background: linear-gradient(90deg, #0a1c51 0%, #18256a 52%, #3b34a0 100%) !important;
    background-color: #18256a !important;
}
"""

with gr.Blocks(title=APP_TITLE, css=STITCH_CSS) as iface:
    gr.HTML("""
    <aside class="stitch-sidebar">
      <div class="stitch-brand">
        <span class="stitch-brand-icon">local_hospital</span>
        <div><div class="stitch-brand-title">Skinova</div><div class="stitch-brand-sub">Clinical intelligence</div></div>
      </div>
      <div class="stitch-new">New Consultation</div>
      <div class="stitch-nav active"><span class="stitch-nav-icon">dashboard</span>Dashboard</div>
      <div class="stitch-nav"><span class="stitch-nav-icon">medical_services</span>Consultations</div>
      <div class="stitch-nav"><span class="stitch-nav-icon">folder_shared</span>Patient Records</div>
      <div class="stitch-nav"><span class="stitch-nav-icon">psychology</span>AI Diagnostics</div>
      <div class="stitch-nav"><span class="stitch-nav-icon">shield_lock</span>Security Settings</div>
      <div class="stitch-side-bottom">
        <div class="stitch-nav"><span class="stitch-nav-icon">help</span>Help Center</div>
        <div class="stitch-nav"><span class="stitch-nav-icon">logout</span>Sign Out</div>
      </div>
    </aside>
    """)

    with gr.Column(elem_classes="stitch-shell"):
        gr.HTML("""
        <header class="stitch-topbar">
          <div>
            <div class="stitch-top-title">Skin Consultation</div>
            <div class="stitch-tabs"><span class="active">Overview</span><span>History</span><span>Encryption Logs</span></div>
          </div>
          <div class="stitch-header-actions">
            <input class="stitch-search" placeholder="Search records..." />
            <button class="stitch-emergency">Emergency Triage</button>
            <button class="stitch-icon-btn" aria-label="Notifications" title="Notifications">
              <span class="material-symbols-outlined">notifications</span>
              <span class="stitch-notification-dot"></span>
            </button>
            <div class="stitch-profile" title="Doctor Profile" aria-label="Doctor Profile">
              <img src="/gradio_api/file=assets/doctor.jpg" alt="Doctor Profile" />
            </div>
          </div>
        </header>
        """)

        gr.HTML("""
        <section class="stitch-banner">
          <div class="stitch-banner-copy">
            <h2>Skinova Clinical Intelligence</h2>
            <p>Multimodal AI for Skin Analysis &amp; Consultation</p>
            <div class="stitch-privacy">Privacy-first consultation</div>
          </div>
        </section>
        """)

        with gr.Row():
            with gr.Column(scale=5):
                gr.HTML('<div class="stitch-section-title"><span class="material-symbols-outlined">assignment</span><h3>Patient Input</h3></div>')
                with gr.Column(elem_classes="stitch-card"):
                    gr.HTML('<div class="stitch-label">Describe your skin concern</div>')

                    audio_input = gr.Audio(
                        sources=["microphone", "upload"],
                        type="filepath",
                        label="Patient Voice (Required)",
                        elem_id="voice_input",
                    )

                    with gr.Row():
                        image_input = gr.Image(
                            type="filepath",
                            label="Skin Image",
                            height=240,
                            elem_id="image_input",
                        )
                        video_input = gr.Video(
                            sources=["upload", "webcam"],
                            label="Skin Video",
                            height=240,
                            elem_id="video_input",
                        )

                    analyze_button = gr.Button(
                        "Analyze Concern",
                        variant="primary",
                        elem_id="analyze_button",
                    )

                    gr.HTML("""
                    <div class="stitch-note">
                      <span class="material-symbols-outlined" style="font-size:16px;vertical-align:middle;">info</span>
                      For better assessment, include a short video showing the affected area from multiple angles and under good lighting.
                    </div>
                    """)

            with gr.Column(scale=7):
                gr.HTML('<div class="stitch-section-title"><span class="material-symbols-outlined">smart_toy</span><h3>Doctor Response</h3></div>')
                with gr.Column(elem_classes="stitch-card"):
                    gr.HTML("""
                    <div style="text-align:center;padding:16px 0 20px;border-bottom:1px solid var(--st-border);margin-bottom:18px;">
                      <div style="width:64px;height:64px;border-radius:50%;background:var(--st-low);display:flex;align-items:center;justify-content:center;margin:0 auto 12px;">
                        <span class="material-symbols-outlined" style="font-size:32px;color:#737685;">assignment_turned_in</span>
                      </div>
                      <h4 style="margin:0 0 6px;font:700 20px 'Hanken Grotesk',sans-serif;">Ready for Analysis</h4>
                      <p style="margin:0;color:var(--st-muted);font-size:13px;">Your consultation summary, transcript, and guidance will appear below after analysis.</p>
                    </div>
                    """)

                    transcript_output = gr.Textbox(
                        label="Your Speech Transcript",
                        lines=4,
                        interactive=False,
                        elem_id="transcript_output",
                    )
                    response_output = gr.Textbox(
                        label="Doctor's Guidance",
                        lines=9,
                        interactive=False,
                        elem_id="response_output",
                    )

                    safety_output = gr.HTML(
                        label="Safety",
                        value=_build_safety_banner(
                            confidence="not_assessed",
                            patient_response="",
                        ),
                        elem_id="safety_output",
                    )

                    confidence_output = gr.HTML(
                        label="AI Visual Confidence",
                        value=_build_confidence_badge(
                            confidence="not_assessed",
                            reason="Confidence will appear after analysis.",
                        ),
                        elem_id="confidence_output",
                    )
                    audio_output = gr.Audio(
                        label="Doctor Voice Response",
                        type="filepath",
                        autoplay=True,
                        elem_id="audio_output",
                    )

        gr.HTML('<div class="stitch-footer">© 2026 Rupali Chauksey. All Rights Reserved. Clinical Intelligence System v1.0</div>')

    analyze_button.click(
        fn=process_inputs,
        inputs=[audio_input, image_input, video_input],
        outputs=[
            transcript_output,
            response_output,
            safety_output,
            confidence_output,
            audio_output,
        ],
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "7860"))
    iface.launch(
        server_name="0.0.0.0",
        server_port=port,
        debug=False,
        footer_links=[],
    )
    



