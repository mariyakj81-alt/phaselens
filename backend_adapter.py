"""
backend_adapter.py  --  the only file the marimo page calls.

``analyze_spectrum`` runs the peak finder, then the checker when a model
answer is present, then the phonon drawer. ``call_assignment_model`` is the
one function a Hugging Face deployment should point at a model. With no
``PHASELENS_ASSIGN_URL`` it returns no text and does not invent a Qwen answer.

The drawer reads saved eigendisplacements from ``data/generated``. It does not
call Materials Project and it does not turn a CIF or a null motion field into
atoms.
"""
from __future__ import annotations

import importlib.machinery
import importlib.util
import io
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from scripts.checker import (  # noqa: E402
    FREQUENCY_TOLERANCE_CM,
    artifact_block,
    card_is_silicon,
    check_assignment,
    load_card,
    material_is_silicon,
    plasma_lines,
    retry_prompt,
    silicon_line,
)
from scripts.make_prompt import build_prompt, load_card_text  # noqa: E402
from scripts.qwen_config import ARTIFACT_LABEL, IGNORED_LABEL  # noqa: E402
from scripts.qwen_zeroshot import coerce_parsed_labels, parse_model_output  # noqa: E402
from scripts.si_mp149_phonon_poc import draw_modes  # noqa: E402

IMAGES_DIR = HERE / "images"
PLACEHOLDER_NAME = "PLACEHOLDER (no saved examples found)"
# name, spectrum file, mode card. Silicon is first so the page opens on a drawable mode.
BUILTIN = (
    ("silicon", "data/train/00499_silicon.json", "silicon.json"),
    ("quartz", "data/train/00498_quartz.json", "quartz.json"),
    ("anatase", "data/train/00490_anatase_simplified.json", "anatase_simplified.json"),
    ("calcite", "data/test/00496_calcite_simplified.json", "calcite_simplified.json"),
    ("mos2", "data/train/00497_mos2.json", "mos2.json"),
)


def empty_result(name: str = "") -> dict:
    """The output dict app.py displays."""
    return {
        "name": name,
        "mode_card": None,
        "status": "none",
        "spectrum": {"shift": [], "raw": [], "corrected": None, "corrected_source": None},
        "peaks": [],
        "assignment": {"source": "not_called", "checker_passed": False, "reasons": [], "retry": False},
        "interpretation": None,
        "visualization": {"available": False, "image_path": None, "modes": [], "notes": []},
        "references": [],
        "warnings": [],
    }


def _builtin_rows() -> list[tuple[str, Path, str]]:
    rows = []
    for name, relative, card in BUILTIN:
        path = HERE / relative
        if path.is_file():
            rows.append((name, path, card))
    return rows


def list_examples() -> list[str]:
    names = [name for name, _path, _card in _builtin_rows()]
    return names or [PLACEHOLDER_NAME]


def list_mode_cards() -> list[str]:
    folder = HERE / "mode_cards"
    if not folder.is_dir():
        return []
    return sorted(path.name for path in folder.glob("*.json") if "comprehensive" not in path.name.casefold())


def default_card(example: str | None) -> str:
    for name, _path, card in _builtin_rows():
        if name == example:
            return card
    cards = list_mode_cards()
    return cards[0] if cards else "silicon.json"


def _synthetic() -> pd.DataFrame:
    shift = np.linspace(100, 1200, 800)
    intensity = 50 + 0.02 * shift
    for center, height in ((250, 300), (520.7, 1500), (800, 200)):
        intensity = intensity + height * np.exp(-0.5 * ((shift - center) / 6) ** 2)
    return pd.DataFrame({"shift": shift, "intensity": intensity})


def load_example(name: str) -> tuple[pd.DataFrame, dict | None]:
    """Return a spectrum frame and its context. Gold answers are dropped."""
    for key, path, card in _builtin_rows():
        if key != name:
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError(f"{path.name} is not a JSON object")
        spec = payload.get("spectrum") if isinstance(payload.get("spectrum"), dict) else {}
        shift = spec.get("shift_cm-1")
        intensity = spec.get("intensity")
        if not isinstance(shift, list) or not isinstance(intensity, list) or len(shift) != len(intensity):
            raise ValueError(f"{path.name} has no shift and intensity columns")
        frame = pd.DataFrame({"shift": shift, "intensity": intensity})
        frame.attrs["name"] = name
        frame.attrs["source_file"] = path.name
        frame.attrs["mode_card"] = card
        context = payload.get("context") if isinstance(payload.get("context"), dict) else {}
        context = dict(context)
        context["mode_card"] = context.get("mode_card") or card
        return frame, {"context": context, "file": path.name}
    frame = _synthetic()
    frame.attrs["name"] = name
    return frame, None


def load_example_spectrum(name: str) -> pd.DataFrame:
    frame, _record = load_example(name)
    return frame


def _clean(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.iloc[:, :2].copy()
    frame.columns = ["shift", "intensity"]
    frame = frame.apply(pd.to_numeric, errors="coerce").dropna().sort_values("shift")
    return frame.reset_index(drop=True)


def read_upload(upload) -> tuple[bytes, str]:
    """Bytes and filename from a marimo file widget."""
    value = getattr(upload, "value", None)
    if not value:
        raise ValueError("no file uploaded")
    item = value[0] if isinstance(value, (list, tuple)) else value
    name = "upload.csv"
    data = item
    if isinstance(item, (list, tuple)) and len(item) >= 2 and isinstance(item[1], (bytes, bytearray)):
        name = str(item[0] or name)
        data = item[1]
    if hasattr(item, "name") and getattr(item, "name"):
        name = str(item.name)
    if hasattr(item, "contents"):
        data = item.contents
    if callable(data):
        data = data()
    if isinstance(data, str):
        data = data.encode("utf-8")
    if not isinstance(data, (bytes, bytearray)):
        raise ValueError("uploaded file has no bytes")
    return bytes(data), name


def parse_uploaded_csv(data: bytes, filename: str = "upload") -> pd.DataFrame:
    """CSV with two columns: Raman shift (cm^-1), intensity. Header optional."""
    try:
        frame = pd.read_csv(io.BytesIO(data))
        first = str(frame.columns[0]).strip()
        numeric_header = pd.to_numeric(pd.Series([first]), errors="coerce").notna().iloc[0]
        if bool(numeric_header):
            frame = pd.read_csv(io.BytesIO(data), header=None)
    except Exception as exc:
        raise ValueError(f"Could not read CSV: {exc}") from exc
    frame = _clean(frame)
    if len(frame) < 10:
        raise ValueError("CSV needs two numeric columns (shift, intensity) with at least 10 rows.")
    frame.attrs["name"] = f"upload:{filename}"
    return frame


def _estimate_baseline(shift: np.ndarray, intensity: np.ndarray, deg: int = 3, iters: int = 30) -> np.ndarray:
    base = intensity.copy()
    for _ in range(iters):
        fit = np.polyval(np.polyfit(shift, base, deg), shift)
        base = np.minimum(base, fit)
    return np.polyval(np.polyfit(shift, base, deg), shift)


def _peak_module():
    name = "phaselens_peak_finder"
    cached = sys.modules.get(name)
    if cached is not None:
        return cached
    path = HERE / "scripts" / "peak_finder"
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    if spec is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    loader.exec_module(module)
    return module


def call_assignment_model(prompt: str) -> dict:
    """The one model call a Hugging Face deployment should point at Qwen.

    Locally this does not call Modal and does not invent a completion.
    Set PHASELENS_ASSIGN_URL to an endpoint that accepts ``{"prompt": "..."}``
    and returns JSON ``{"text": "..."}`` (or a raw JSON list).
    """
    if not isinstance(prompt, str) or not prompt.strip():
        return {"called": False, "text": None, "reason": "The assignment prompt was empty."}
    url = os.environ.get("PHASELENS_ASSIGN_URL", "").strip()
    if not url:
        return {
            "called": False,
            "text": None,
            "reason": (
                "No assignment model is configured. Set PHASELENS_ASSIGN_URL to an HTTP endpoint "
                'that accepts {"prompt": "..."} and returns {"text": "..."}. '
                "Modal was not called, and no Qwen completion was invented."
            ),
        }
    body = json.dumps({"prompt": prompt}).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            raw = response.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        return {
            "called": True,
            "text": None,
            "reason": f"Assignment endpoint failed ({type(exc).__name__}: {exc}). No label was invented.",
        }
    text = raw.strip()
    try:
        loaded = json.loads(raw)
    except json.JSONDecodeError:
        loaded = None
    if isinstance(loaded, dict):
        for key in ("text", "completion", "output", "content"):
            value = loaded.get(key)
            if isinstance(value, str) and value.strip():
                text = value
                break
    elif isinstance(loaded, list):
        text = json.dumps(loaded)
    if not text:
        return {"called": True, "text": None, "reason": "Assignment endpoint returned empty text. No label was invented."}
    return {"called": True, "text": text, "reason": None}


def _artifacts_from_card(card: dict, card_name: str) -> dict:
    block = card.get("artifact_lines") if isinstance(card.get("artifact_lines"), dict) else {}
    silicon = None
    if not card_is_silicon(card_name) and not material_is_silicon(card.get("material")):
        for row in block.get("substrate_raman") or []:
            if not isinstance(row, dict):
                continue
            number = row.get("position_cm-1")
            if isinstance(number, bool) or not isinstance(number, (int, float)):
                continue
            silicon = float(number)
            break
    plasma = []
    for row in block.get("laser_dependent_plasma_or_stray_light") or []:
        if not isinstance(row, dict):
            continue
        number = row.get("position_cm-1")
        if isinstance(number, bool) or not isinstance(number, (int, float)):
            continue
        plasma.append(float(number))
    return {"silicon": silicon, "plasma": plasma}


def _context_for(card_name: str, card: dict, record: dict | None) -> dict:
    file_ctx = None
    if isinstance(record, dict) and isinstance(record.get("context"), dict):
        file_ctx = record["context"]
    if isinstance(file_ctx, dict) and file_ctx.get("mode_card") == card_name:
        context = dict(file_ctx)
        context["mode_card"] = card_name
        return context
    return {
        "material": card.get("material"),
        "mode_card": card_name,
        "laser_nm": None if not isinstance(file_ctx, dict) else file_ctx.get("laser_nm"),
        "substrate": None,
        "known_artifact_lines_cm-1": _artifacts_from_card(card, card_name),
    }


def _artifact_notes(position: float, context: dict, card_name: str) -> list[str]:
    notes = []
    for line in plasma_lines(context):
        if abs(position - line) <= FREQUENCY_TOLERANCE_CM:
            note = f"within {FREQUENCY_TOLERANCE_CM:.1f} cm^-1 of plasma line {line:g}"
            if artifact_block(context).get("plasma_is_placeholder"):
                note += " (placeholder position on the spectrum file)"
            notes.append(note)
    silicon = silicon_line(context)
    if (
        silicon is not None
        and not material_is_silicon(context.get("material"))
        and not card_is_silicon(card_name)
        and abs(position - silicon) <= FREQUENCY_TOLERANCE_CM
    ):
        notes.append(f"within {FREQUENCY_TOLERANCE_CM:.1f} cm^-1 of the silicon substrate line at {silicon:g}")
    return notes


def _missing_cif(card: dict) -> str | None:
    validation = card.get("symmetry_validation")
    structure = validation.get("structure") if isinstance(validation, dict) else None
    if not isinstance(structure, dict):
        return None
    cif = structure.get("cif")
    if not isinstance(cif, str) or not cif.strip() or ".." in cif.replace("\\", "/"):
        return None
    if (HERE / "mode_cards" / cif).is_file():
        return None
    return cif


def _references(card: dict) -> list[dict]:
    refs = []
    citation = card.get("citation")
    if isinstance(citation, dict) and citation.get("primary"):
        refs.append({"citation": str(citation["primary"]), "doi": ""})
    elif isinstance(citation, str) and citation.strip():
        refs.append({"citation": citation.strip(), "doi": ""})
    studies = card.get("studies") if isinstance(card.get("studies"), list) else []
    chosen = None
    for study in studies:
        if isinstance(study, dict) and study.get("source_verified") is True and study.get("citation"):
            chosen = study
            break
    if chosen is None:
        for study in studies:
            if isinstance(study, dict) and study.get("citation"):
                chosen = study
                break
    if chosen is not None:
        text = str(chosen.get("citation"))
        if not any(item["citation"] == text for item in refs):
            refs.append({"citation": text, "doi": str(chosen.get("doi") or "")})
    return refs


def _is_mos2(card_name: str, card: dict) -> bool:
    text = f"{card_name} {card.get('material', '')}".casefold()
    return "mos2" in text or "disulfide" in text


def _interpretation(card_name: str, card: dict, context: dict, adjusted: list) -> dict:
    if not _is_mos2(card_name, card):
        return {
            "label": "Layer number",
            "value": "not applicable",
            "note": "Layer readout runs only for a MoS2 mode card, and only from checker-accepted peaks. Strain was not computed.",
        }
    accepted = [
        row for row in adjusted
        if isinstance(row, dict) and row.get("label") not in (None, IGNORED_LABEL, ARTIFACT_LABEL)
    ]
    if not accepted:
        return {
            "label": "Layer number",
            "value": "unavailable",
            "note": "The checker did not accept an in-plane and an out-of-plane MoS2 mode, so no layer was assigned.",
        }
    try:
        from scripts.layer_readout import STRAIN_REASON, assign_layer, load_mos2_layer_table

        readout = assign_layer(
            {"laser_nm": context.get("laser_nm"), "layer": None, "parsed_labels": adjusted},
            load_mos2_layer_table(),
        )
    except Exception as exc:
        return {"label": "Layer number", "value": "unavailable", "note": f"Layer readout could not run ({type(exc).__name__}: {exc})."}
    predicted = readout.get("predicted_layer")
    strain_note = readout.get("strain_note") or STRAIN_REASON
    if predicted:
        return {
            "label": "Layer number",
            "value": str(predicted),
            "note": "From checker-accepted peaks and the MoS2 layer table for this laser. " + strain_note,
        }
    return {
        "label": "Layer number",
        "value": "unavailable",
        "note": "The checker did not accept both an in-plane and an out-of-plane MoS2 mode, so no layer was assigned. " + strain_note,
    }


def _finite_lattice(lattice) -> bool:
    if not isinstance(lattice, list) or len(lattice) != 3:
        return False
    for row in lattice:
        if not isinstance(row, list) or len(row) != 3:
            return False
        for value in row:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                return False
    return True


def _cell_trace(lattice):
    import plotly.graph_objects as go

    vectors = [np.asarray(row, dtype=float) for row in lattice]
    index = {}
    corners = []
    for i in (0, 1):
        for j in (0, 1):
            for k in (0, 1):
                index[(i, j, k)] = len(corners)
                corners.append(i * vectors[0] + j * vectors[1] + k * vectors[2])
    xs: list[float | None] = []
    ys: list[float | None] = []
    zs: list[float | None] = []
    for i, j, k in index:
        for step in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
            nxt = (i + step[0], j + step[1], k + step[2])
            if nxt not in index:
                continue
            start = corners[index[(i, j, k)]]
            end = corners[index[nxt]]
            xs.extend([float(start[0]), float(end[0]), None])
            ys.extend([float(start[1]), float(end[1]), None])
            zs.extend([float(start[2]), float(end[2]), None])
    return go.Scatter3d(
        x=xs, y=ys, z=zs, mode="lines", line=dict(color="#9aa0a6", width=3), name="cell", hoverinfo="skip"
    )


def figure_from_scene(mode: dict):
    """Plotly figure for one verified scene. None if plotly is missing or the scene is empty."""
    scene = mode.get("scene") if isinstance(mode, dict) else None
    frames = scene.get("frames") if isinstance(scene, dict) else None
    if not isinstance(frames, list) or not frames:
        return None
    try:
        import plotly.graph_objects as go
    except ImportError:
        return None
    species = scene.get("species") if isinstance(scene.get("species"), list) else []
    first = frames[0].get("cartesian_coordinates_angstrom")
    if not isinstance(first, list) or not first:
        return None
    labels = []
    for index in range(len(first)):
        element = species[index] if index < len(species) else "atom"
        labels.append(f"{element} {index + 1}")

    def atoms(coords):
        xs, ys, zs = zip(*coords)
        return go.Scatter3d(
            x=xs,
            y=ys,
            z=zs,
            mode="markers+text",
            text=labels,
            textposition="top center",
            marker=dict(size=9, color="#1f4b99"),
            name="atoms",
            hovertemplate="%{text}<br>%{x:.3f}, %{y:.3f}, %{z:.3f}<extra></extra>",
        )

    data = [atoms(first)]
    lattice = scene.get("lattice_angstrom")
    if _finite_lattice(lattice):
        data.append(_cell_trace(lattice))
    figure = go.Figure(data=data)
    figure.frames = [
        go.Frame(data=[atoms(frame["cartesian_coordinates_angstrom"])], name=str(index), traces=[0])
        for index, frame in enumerate(frames)
        if isinstance(frame, dict) and isinstance(frame.get("cartesian_coordinates_angstrom"), list)
    ]
    frequency = mode.get("frequency_cm-1")
    title = f"{mode.get('symmetry')} at {frequency:g} cm^-1" if isinstance(frequency, (int, float)) else str(mode.get("symmetry"))
    calculated = mode.get("calculated_frequency_cm-1")
    if isinstance(calculated, (int, float)) and not isinstance(calculated, bool):
        title += f" (calculated {float(calculated):.1f})"
    figure.update_layout(
        title=title,
        height=480,
        margin=dict(l=0, r=0, t=48, b=0),
        scene=dict(aspectmode="data", xaxis_title="x (A)", yaxis_title="y (A)", zaxis_title="z (A)"),
        updatemenus=[
            {
                "type": "buttons",
                "direction": "left",
                "x": 0.0,
                "y": 0.0,
                "buttons": [
                    {
                        "label": "Play",
                        "method": "animate",
                        "args": [None, {"frame": {"duration": 90, "redraw": True}, "fromcurrent": True}],
                    }
                ],
            }
        ],
    )
    return figure


def _caption(mode: dict) -> str:
    scene = mode.get("scene") if isinstance(mode.get("scene"), dict) else {}
    frequency = mode.get("frequency_cm-1")
    freq = f"{float(frequency):g}" if isinstance(frequency, (int, float)) and not isinstance(frequency, bool) else "?"
    text = (
        f"{mode.get('symmetry')} at {freq} cm^-1, retrieved eigendisplacements"
        f" ({scene.get('material_id') or 'saved export'})."
    )
    calculated = mode.get("calculated_frequency_cm-1")
    if isinstance(calculated, (int, float)) and not isinstance(calculated, bool):
        text += f" Calculated frequency {float(calculated):.2f} cm^-1."
    text += " This picture is not a model assignment and not a new phonon calculation."
    check = mode.get("symmetry_check")
    if isinstance(check, str) and check.strip():
        text += " " + check.strip()
    return text


def _visualization(card: dict, example_name: str) -> dict:
    drawn = draw_modes(card)
    modes = []
    any_picture = False
    figure_error = False
    for mode in drawn["modes"]:
        available = mode.get("status") == "verified" and isinstance(mode.get("scene"), dict)
        figure = figure_from_scene(mode) if available else None
        reason = mode.get("reason")
        if available and figure is None:
            available = False
            figure_error = True
            reason = "eigenvalues are stored, but a 3D figure could not be built"
        if available:
            any_picture = True
        modes.append(
            {
                "symmetry": mode.get("symmetry"),
                "label": mode.get("label"),
                "frequency_cm-1": mode.get("frequency_cm-1"),
                "calculated_frequency_cm-1": mode.get("calculated_frequency_cm-1"),
                "available": available,
                "reason": None if available else reason,
                "caption": _caption(mode) if available else None,
                "figure": figure,
                "scene": mode.get("scene"),
            }
        )
    notes = list(drawn.get("notes") or [])
    if figure_error:
        notes.append("Plotly did not build a figure for a mode that has eigenvalues.")
    image = IMAGES_DIR / f"{example_name}.png"
    image_path = str(image) if image.is_file() else None
    return {
        "available": any_picture or image_path is not None,
        "image_path": image_path,
        "modes": modes,
        "notes": notes,
    }


def analyze_spectrum(spectrum: pd.DataFrame, mode_card=None, cif=None, record=None, model_text=None) -> dict:
    """Peak finder, checker, and phonon drawer for one spectrum.

    ``model_text`` is an optional model answer (a JSON list). It is not treated
    as Qwen unless ``call_assignment_model`` actually returned it. Gold labels
    on ``record`` are ignored.
    """
    attrs = getattr(spectrum, "attrs", {}) or {}
    name = attrs.get("name", "")
    res = empty_result(name)
    source_file = attrs.get("source_file")
    if source_file:
        res["name"] = f"{name} ({source_file})"
    if isinstance(record, dict):
        record = {key: value for key, value in record.items() if key != "answers"}
    try:
        shift = spectrum["shift"].to_numpy(float)
        intensity = spectrum["intensity"].to_numpy(float)
    except Exception as exc:
        res["status"] = "error"
        res["warnings"].append(f"Spectrum needs shift and intensity columns ({exc}).")
        return res
    res["spectrum"]["shift"] = shift.tolist()
    res["spectrum"]["raw"] = intensity.tolist()

    card_name = mode_card or attrs.get("mode_card")
    if not isinstance(card_name, str) or not card_name.strip():
        file_ctx = record.get("context") if isinstance(record, dict) else None
        if isinstance(file_ctx, dict) and isinstance(file_ctx.get("mode_card"), str):
            card_name = file_ctx["mode_card"]
        else:
            card_name = default_card(name)
    res["mode_card"] = card_name
    try:
        card = load_card(card_name)
        card_text = load_card_text(card_name)
    except SystemExit as exc:
        res["status"] = "error"
        res["warnings"].append(str(exc))
        return res

    if cif:
        res["warnings"].append(
            "A CIF was supplied. The drawer does not calculate phonons from a CIF. "
            "It only shows eigendisplacements that were already retrieved."
        )
    missing_cif = _missing_cif(card)
    if missing_cif:
        res["warnings"].append(
            f"Mode card points at mode_cards/{missing_cif}, which is not in the tree. "
            "Phonons were not calculated from it."
        )

    try:
        found = _peak_module().find_raman_peaks(shift, intensity)
    except Exception as exc:
        found = {}
        res["warnings"].append(f"Peak finder failed ({type(exc).__name__}: {exc}). No peaks were invented.")
    raw_peaks = found.get("peaks") if isinstance(found, dict) else None
    if not isinstance(raw_peaks, list):
        raw_peaks = []
    corrected = found.get("corrected") if isinstance(found, dict) else None
    if isinstance(corrected, list) and len(corrected) == len(shift):
        res["spectrum"]["corrected"] = corrected
        res["spectrum"]["corrected_source"] = found.get("baseline") or "pybaselines.Baseline.arpls"
    else:
        res["spectrum"]["corrected"] = (intensity - _estimate_baseline(shift, intensity)).tolist()
        res["spectrum"]["corrected_source"] = "polynomial estimate (peak finder did not return a baseline)"

    public_peaks = []
    for peak in raw_peaks:
        if not isinstance(peak, dict):
            continue
        position = peak.get("position_cm-1")
        if isinstance(position, bool) or not isinstance(position, (int, float)):
            continue
        public_peaks.append(
            {
                "position_cm-1": float(position),
                "height": peak.get("height"),
                "fwhm_cm-1": peak.get("fwhm_cm-1"),
            }
        )

    context = _context_for(card_name, card, record if isinstance(record, dict) else None)
    prompt = build_prompt({"peaks": public_peaks}, card_text)
    pasted = isinstance(model_text, str) and bool(model_text.strip())
    retry = False
    if pasted:
        raw = model_text.strip()
        source = "pasted"
        model_reason = None
    else:
        model = call_assignment_model(prompt)
        raw = model.get("text") if isinstance(model.get("text"), str) and model.get("text").strip() else None
        model_reason = model.get("reason")
        if model.get("called") and raw:
            source = "endpoint"
        elif model.get("called"):
            source = "endpoint_failed"
        else:
            source = "not_called"
    parsed = coerce_parsed_labels(parse_model_output(raw)) if isinstance(raw, str) else None
    labels_for_checker = parsed if source in {"pasted", "endpoint"} else None
    outcome = check_assignment(public_peaks, labels_for_checker, card, context)
    if source == "endpoint" and not outcome.passed:
        retry_model = call_assignment_model(retry_prompt(prompt, outcome.reasons))
        retry = True
        retry_text = retry_model.get("text") if isinstance(retry_model.get("text"), str) else None
        if retry_text:
            outcome = check_assignment(
                public_peaks,
                coerce_parsed_labels(parse_model_output(retry_text)),
                card,
                context,
            )
            source = "endpoint_retry"
        elif retry_model.get("reason"):
            res["warnings"].append(retry_model["reason"])

    if source == "not_called":
        if model_reason:
            res["warnings"].append(model_reason)
        res["warnings"].append(
            f"Checker ran on {len(public_peaks)} peak(s) with no model answer. "
            "Every peak is unassigned. Nothing here is a Qwen label."
        )
    elif source == "endpoint_failed":
        if model_reason:
            res["warnings"].append(model_reason)
        res["warnings"].append("Checker left every peak unassigned because the endpoint returned no usable answer.")
    elif source == "pasted" and parsed is None:
        res["warnings"].append("The pasted text was not a JSON list of labels. The checker left every peak unassigned.")
        res["warnings"].extend(outcome.reasons)
    else:
        res["warnings"].extend(outcome.reasons)

    adjusted = outcome.adjusted_labels if isinstance(outcome.adjusted_labels, list) else []
    for index, peak in enumerate(public_peaks):
        label_row = adjusted[index] if index < len(adjusted) and isinstance(adjusted[index], dict) else {}
        label = label_row.get("label")
        if not isinstance(label, str) or not label.strip():
            label = IGNORED_LABEL
        notes = _artifact_notes(float(peak["position_cm-1"]), context, card_name)
        is_artifact = label.casefold() == ARTIFACT_LABEL.casefold()
        res["peaks"].append(
            {
                "position_cm1": float(peak["position_cm-1"]),
                "position_cm-1": float(peak["position_cm-1"]),
                "intensity": peak.get("height"),
                "symmetry": label,
                "is_artifact": is_artifact,
                "artifact_reason": "; ".join(notes) if is_artifact and notes else ("labeled artifact" if is_artifact else ""),
                "artifact_hint": "" if is_artifact or not notes else "; ".join(notes) + ". A model label other than artifact would be rejected.",
            }
        )
    res["assignment"] = {
        "source": source,
        "checker_passed": bool(outcome.passed) and source not in {"not_called", "endpoint_failed"},
        "reasons": list(outcome.reasons),
        "retry": retry,
    }
    res["status"] = "no_model" if source == "not_called" else "checked"
    res["interpretation"] = _interpretation(card_name, card, context, adjusted)
    res["visualization"] = _visualization(card, name)
    res["references"] = _references(card)
    return res


def glue_demo() -> int:
    """Run one built-in silicon example through the finder, checker, and drawer."""
    failures: list[str] = []
    silicon_card = load_card("silicon.json")
    drawn = draw_modes(silicon_card)
    verified = [mode for mode in drawn["modes"] if mode.get("status") == "verified" and mode.get("scene")]
    if len(verified) != 1 or verified[0].get("symmetry") != "F2g":
        failures.append(f"silicon drawer {[(m.get('symmetry'), m.get('status'), m.get('reason')) for m in drawn['modes']]}")
    else:
        frames = verified[0]["scene"]["frames"]
        disp = frames[0]["displacements_angstrom"]
        if len(frames) != 12 or len(disp) != 2:
            failures.append(f"silicon scene shape frames={len(frames)} atoms={len(disp)}")
        else:
            residual = max(abs(disp[0][axis] + disp[1][axis]) for axis in range(3))
            if residual > 1e-4:
                failures.append(f"silicon displacements are not opposed ({residual})")
    quartz = draw_modes(load_card("quartz.json"))
    if not quartz["modes"] or any(mode.get("scene") for mode in quartz["modes"]):
        failures.append(f"quartz drawer count={len(quartz['modes'])}")
    elif not all("eigenvalue" in (mode.get("reason") or "") for mode in quartz["modes"]):
        failures.append(f"quartz reason {quartz['modes'][0].get('reason')}")
    if any(mode.get("label") == "2nu2" for mode in draw_modes(load_card("calcite_simplified.json"))["modes"]):
        failures.append("calcite second-order 2nu2 was offered as a drawable phonon")

    frame, record = load_example("silicon")
    plain = analyze_spectrum(frame, mode_card="silicon.json", record=record)
    if plain["assignment"]["source"] != "not_called":
        failures.append(f"source {plain['assignment']['source']}")
    if any(peak["symmetry"] != IGNORED_LABEL for peak in plain["peaks"]):
        failures.append(f"no-model labels {[peak['symmetry'] for peak in plain['peaks']]}")
    pictures = [mode for mode in plain["visualization"]["modes"] if mode.get("available") and mode.get("figure") is not None]
    if len(pictures) != 1:
        failures.append(f"silicon figures {len(pictures)}")
    target = min(plain["peaks"], key=lambda peak: abs(peak["position_cm-1"] - 520.2), default=None)
    if target is None or abs(target["position_cm-1"] - 520.2) > FREQUENCY_TOLERANCE_CM:
        failures.append(f"finder missed silicon {target}")
    else:
        bad = [
            {
                "position_cm-1": peak["position_cm-1"],
                "label": "Eg" if peak["position_cm-1"] == target["position_cm-1"] else "artifact",
            }
            for peak in plain["peaks"]
        ]
        refused = analyze_spectrum(frame, mode_card="silicon.json", record=record, model_text=json.dumps(bad))
        refused_peak = min(refused["peaks"], key=lambda peak: abs(peak["position_cm-1"] - 520.2))
        if refused_peak["symmetry"] != IGNORED_LABEL:
            failures.append(f"Eg was kept {refused_peak}")
        good = []
        for peak in plain["peaks"]:
            if abs(peak["position_cm-1"] - 520.2) <= FREQUENCY_TOLERANCE_CM:
                label = "F2g"
            elif peak.get("artifact_hint"):
                label = "artifact"
            else:
                label = "artifact"
            good.append({"position_cm-1": peak["position_cm-1"], "label": label})
        accepted = analyze_spectrum(frame, mode_card="silicon.json", record=record, model_text=json.dumps(good))
        kept = min(accepted["peaks"], key=lambda peak: abs(peak["position_cm-1"] - 520.2))
        if kept["symmetry"] != "F2g" or accepted["assignment"]["source"] != "pasted":
            failures.append(f"F2g paste {kept} {accepted['assignment']}")

    context = record["context"] if isinstance(record, dict) else {}
    plasma = plasma_lines(context)
    if plasma:
        plasma_check = check_assignment(
            [{"position_cm-1": 519.19}, {"position_cm-1": plasma[0]}],
            [{"position_cm-1": 519.19, "label": "F2g"}, {"position_cm-1": plasma[0], "label": "F2g"}],
            silicon_card,
            context,
        )
        if plasma_check.adjusted_labels[1]["label"] != IGNORED_LABEL:
            failures.append(f"plasma F2g was kept {plasma_check.adjusted_labels}")
        if plasma_check.adjusted_labels[0]["label"] != "F2g":
            failures.append(f"silicon F2g was dropped {plasma_check.reasons}")

    quartz_frame, quartz_record = load_example("quartz")
    quartz_run = analyze_spectrum(quartz_frame, mode_card="quartz.json", record=quartz_record)
    if any(mode.get("available") for mode in quartz_run["visualization"]["modes"]):
        failures.append("quartz analyze drew a mode")
    if quartz_run["interpretation"]["value"] != "not applicable":
        failures.append(f"quartz layer {quartz_run['interpretation']}")

    mos_frame, mos_record = load_example("mos2")
    mos = analyze_spectrum(mos_frame, mode_card="mos2.json", record=mos_record)
    if mos["interpretation"]["value"] in {"1L", "2L", "3L", "4L", "bulk"}:
        failures.append(f"mos2 layer leaked {mos['interpretation']}")
    if any(mode.get("available") for mode in mos["visualization"]["modes"]):
        failures.append("mos2 drew a mode without eigenvalues")

    anatase_cif = HERE / "mode_cards" / "Qiaomu" / "structures" / "anatase.cif"
    calcite_cif = HERE / "mode_cards" / "Qiaomu" / "structures" / "calcite.cif"
    print(json.dumps({
        "silicon_no_model_peaks": [(peak["position_cm1"], peak["symmetry"]) for peak in plain["peaks"]],
        "silicon_drawn": [(mode["symmetry"], mode["frequency_cm-1"]) for mode in pictures],
        "quartz_modes": len(quartz["modes"]),
        "quartz_refused": quartz["modes"][0]["reason"] if quartz["modes"] else None,
        "mos2_layer": mos["interpretation"]["value"],
        "anatase_cif_present": anatase_cif.is_file(),
        "calcite_cif_present": calcite_cif.is_file(),
        "failures": failures,
    }, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(glue_demo())
