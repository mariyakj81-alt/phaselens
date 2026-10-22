#!/usr/bin/env python3
"""Minimal PhaseLens Raman-mode to Materials Project phonon export.

The default is the silicon proof of concept. It only emits animation frames
from real MP eigendisplacements and only after a non-ambiguous mode match.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np


THZ_TO_CM1 = 33.3564
VISUALIZATION_AMPLITUDE_ANGSTROM = 0.08
FRAME_COUNT = 12

# MP IDs are phase-specific. These are explicit; the script does not identify
# a material from Raman data.
MATERIAL_PROJECT_IDS = {
    "pristine diamond-cubic Si-I": "mp-149",
    "quartz": "mp-7000",             # alpha quartz
    "calcite (CaCO3)": "mp-3953",
    "anatase (TiO2)": "mp-390",
    "molybdenum disulfide": "mp-2815",  # bulk 2H-MoS2
}


class DataBlocker(RuntimeError):
    pass


_INACTIVE_ACTIVITY = {"second-order", "silent", "inactive"}


def _frequency_cm(mode: dict[str, Any]) -> float | None:
    for key in ("position_cm-1", "position_cm1", "frequency_cm-1"):
        value = mode.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        return float(value)
    return None


def _raman_listed(mode: dict[str, Any]) -> bool:
    """True for a Raman-active row in either card shape.

    Schema 2.1 curated rows omit ``raman_activity`` and mean active.
    Quartz uses boolean ``raman_active`` instead of the string ``raman_activity``.
    """
    if mode.get("raman_active") is False:
        return False
    activity = mode.get("raman_activity")
    if isinstance(activity, str) and activity.casefold() in _INACTIVE_ACTIVITY:
        return False
    if mode.get("raman_active") is True:
        return True
    if isinstance(activity, str):
        return activity.casefold() == "active"
    return "symmetry" in mode


def _inactive_ids(card: dict[str, Any]) -> set[str]:
    found: set[str] = set()
    for mode in card.get("modes") or []:
        if not isinstance(mode, dict) or _raman_listed(mode):
            continue
        for key in ("mode", "id"):
            value = mode.get(key)
            if isinstance(value, str) and value:
                found.add(value)
    return found


def active_peaks(card: dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize the two existing mode-card shapes. Frequency-less rows are omitted."""
    return card_peak_rows(card)[0]


def card_peak_rows(card: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Raman-active rows that have a frequency, plus curated rows that have none."""
    inactive = _inactive_ids(card)
    peaks: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    seen: set[tuple[Any, float, Any]] = set()
    for source in ("curated_expected_modes", "modes"):
        for mode in card.get(source) or []:
            if not isinstance(mode, dict) or not _raman_listed(mode):
                continue
            mode_id = mode.get("mode")
            if isinstance(mode_id, str) and mode_id in inactive:
                continue
            symmetry = mode.get("symmetry")
            if not isinstance(symmetry, str) or not symmetry.strip():
                continue
            frequency = _frequency_cm(mode)
            if frequency is None:
                if source == "curated_expected_modes":
                    label = mode.get("id", mode.get("mode", mode.get("orientation")))
                    skipped.append(
                        {
                            "frequency_cm-1": None,
                            "symmetry": symmetry,
                            "label": label,
                            "motion": mode.get("motion"),
                            "status": "animation_unavailable",
                            "reason": (
                                "this card row has no frequency, so it was not matched to "
                                "eigenvalues and no displacement was invented"
                            ),
                            "scene": None,
                        }
                    )
                continue
            label = mode.get("id", mode.get("mode", mode.get("orientation")))
            key = (symmetry, round(frequency, 4), label)
            if key in seen:
                continue
            seen.add(key)
            peaks.append(
                {
                    "frequency_cm-1": frequency,
                    "symmetry": symmetry,
                    "label": label,
                    "motion": mode.get("motion"),
                }
            )
    return peaks, skipped


def gamma_index(phonon_bs: Any) -> int:
    distances = [float(np.linalg.norm(q.frac_coords)) for q in phonon_bs.qpoints]
    index = int(np.argmin(distances))
    if distances[index] > 1e-7:
        raise DataBlocker(f"no Gamma q-point (closest norm {distances[index]:.3e})")
    return index


def as_pymatgen_bandstructure(phonon_bs: Any) -> Any:
    """mp-api's DFPT route returns an emmet PhononBS; normalize its API."""
    if phonon_bs is not None and not hasattr(phonon_bs, "bands") and hasattr(phonon_bs, "to_pmg"):
        return phonon_bs.to_pmg
    return phonon_bs


def describe_bandstructure(phonon_bs: Any) -> dict[str, Any]:
    """Inspect and explicitly attempt the pymatgen PhononWebsite export."""
    details = {"retrieved": phonon_bs is not None, "has_eigendisplacements": bool(getattr(phonon_bs, "has_eigendisplacements", False))}
    if phonon_bs is None:
        return details
    details["frequencies_shape"] = list(np.asarray(phonon_bs.bands).shape)
    eig = getattr(phonon_bs, "eigendisplacements", None)
    details["eigendisplacements_shape"] = list(np.asarray(eig).shape) if eig is not None else None
    try:
        # The official exporter dereferences real vectors. A failure is recorded,
        # never substituted with synthetic displacements.
        website = phonon_bs.as_phononwebsite()
        details["phononwebsite_export"] = "available"
        details["phononwebsite_vector_shape"] = list(np.asarray(website["vectors"]).shape)
    except Exception as exc:
        details["phononwebsite_export"] = "unavailable"
        details["phononwebsite_blocker"] = f"{type(exc).__name__}: {exc}"
    return details


def matching_record(peak: dict[str, Any], phonon_bs: Any, material_id: str) -> dict[str, Any]:
    """Return a conservative Gamma match; MP bandstructures have no irrep field."""
    if not bool(getattr(phonon_bs, "has_eigendisplacements", False)):
        return {**peak, "status": "animation_unavailable", "reason": "real_eigendisplacements_unavailable"}
    gamma = gamma_index(phonon_bs)
    frequencies_cm1 = np.asarray(phonon_bs.bands, dtype=float)[:, gamma] * THZ_TO_CM1
    optical = np.arange(len(frequencies_cm1)) >= 3
    nearest = int(np.argmin(np.where(optical, abs(frequencies_cm1 - peak["frequency_cm-1"]), np.inf)))
    delta = float(abs(frequencies_cm1[nearest] - peak["frequency_cm-1"]))
    tolerance = max(12.0, 0.05 * peak["frequency_cm-1"])
    record = {
        **peak,
        "gamma_band_index_zero_based": nearest,
        "calculated_frequency_cm-1": float(frequencies_cm1[nearest]),
        "frequency_delta_cm-1": delta,
        "frequency_tolerance_cm-1": tolerance,
        "atom_count": len(phonon_bs.structure),
        "symmetry_check": "MP phonon bandstructure has no irrep labels",
    }
    if delta > tolerance:
        return {**record, "status": "animation_unavailable", "reason": "no_calculated_frequency_within_tolerance"}
    # MP does not serialize irreps. For the Si card, the literature-backed F2g
    # assignment can still be checked for structural consistency: diamond
    # Fd-3m, a two-atom primitive cell, and a threefold optical Gamma set.
    group = [index for index, value in enumerate(frequencies_cm1) if abs(value - frequencies_cm1[nearest]) < 0.1]
    if material_id == "mp-149" and peak.get("symmetry") in {"F2g", "T2g"}:
        from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

        space_group = SpacegroupAnalyzer(phonon_bs.structure, symprec=0.1).get_space_group_number()
        if len(phonon_bs.structure) == 2 and set(str(site.specie) for site in phonon_bs.structure) == {"Si"} and space_group == 227 and len(group) == 3:
            return {
                **record,
                "degenerate_band_indices_zero_based": group,
                "symmetry_check": "consistent with card's literature-backed F2g: Fd-3m (#227) diamond Si and a threefold Gamma optical set; MP does not provide an irrep label",
                "status": "verified",
            }
        return {**record, "status": "animation_unavailable", "reason": "si_structure_or_optical_triplet_not_symmetry_consistent"}
    # Frequency alone is deliberately insufficient to mark other modes verified.
    return {**record, "status": "animation_unavailable", "reason": "symmetry_not_available_to_verify_mode_match"}


def frames_for_verified_mode(phonon_bs: Any, band: int, gamma: int) -> list[dict[str, Any]]:
    eigenvector = np.asarray(phonon_bs.eigendisplacements[band, gamma], dtype=complex)
    norm = float(np.max(np.linalg.norm(eigenvector, axis=1)))
    if not math.isfinite(norm) or norm <= 0:
        raise DataBlocker("selected eigenvector is zero or non-finite")
    equilibrium = np.asarray(phonon_bs.structure.cart_coords, dtype=float)
    frames = []
    for frame in range(FRAME_COUNT):
        phase = 2 * math.pi * frame / FRAME_COUNT
        displacement = np.real(eigenvector / norm * VISUALIZATION_AMPLITUDE_ANGSTROM * np.exp(1j * phase))
        if not np.isfinite(displacement).all():
            raise DataBlocker("selected eigenvector produced non-finite displacement")
        frames.append({"phase_radians": phase, "displacements_angstrom": displacement.tolist(), "cartesian_coordinates_angstrom": (equilibrium + displacement).tolist()})
    return frames


def animation_validation(frames: list[dict[str, Any]], atom_count: int) -> dict[str, bool]:
    displacements = np.asarray([frame["displacements_angstrom"] for frame in frames], dtype=float)
    cancellation = np.max(np.linalg.norm(np.sum(displacements, axis=1), axis=1)) / np.max(np.sum(np.linalg.norm(displacements, axis=2), axis=1))
    return {
        "vectors_match_atom_count": all(len(frame["displacements_angstrom"]) == atom_count for frame in frames),
        "displacements_nonzero_finite": bool(np.any(np.abs(displacements) > 0) and np.isfinite(displacements).all()),
        "optical_sublattices_opposed": bool(cancellation < 1e-5),
        "frames_oscillate_about_equilibrium": bool(np.allclose(displacements[0], -displacements[FRAME_COUNT // 2])),
    }


def _generated_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "generated"


def _finite_rows(rows: Any, width: int) -> bool:
    if not isinstance(rows, list) or not rows:
        return False
    for row in rows:
        if not isinstance(row, list) or len(row) != width:
            return False
        for value in row:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                return False
            if not math.isfinite(float(value)):
                return False
    return True


def _frames_are_real(animation: Any, atom_count: int) -> bool:
    frames = animation.get("frames") if isinstance(animation, dict) else None
    if not isinstance(frames, list) or not frames:
        return False
    nonzero = False
    for frame in frames:
        if not isinstance(frame, dict):
            return False
        coords = frame.get("cartesian_coordinates_angstrom")
        disp = frame.get("displacements_angstrom")
        if not _finite_rows(coords, 3) or not _finite_rows(disp, 3):
            return False
        if atom_count and len(coords) != atom_count:
            return False
        if any(abs(float(component)) > 0 for row in disp for component in row):
            nonzero = True
    return nonzero


def _same_symmetry(left: Any, right: Any) -> bool:
    if left == right and isinstance(left, str) and left:
        return True
    if not isinstance(left, str) or not isinstance(right, str):
        return False
    root = str(Path(__file__).resolve().parents[1])
    if root not in sys.path:
        sys.path.insert(0, root)
    from scripts.label_norm import canonical_label

    canon_left = canonical_label(left)
    return bool(canon_left) and canon_left == canonical_label(right)


def load_saved_exports() -> tuple[dict[str, dict[str, Any]], list[str]]:
    """Read phonon animation JSON already on disk. Does not call Materials Project."""
    found: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    folder = _generated_dir()
    if not folder.is_dir():
        return found, ["data/generated is missing"]
    for path in sorted(folder.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name} is not valid JSON ({exc})")
            continue
        if not isinstance(payload, dict) or payload.get("schema_version") != "phaselens-phonon-animation-1.0":
            continue
        payload = dict(payload)
        payload["_path"] = str(path)
        material = payload.get("material")
        material_id = payload.get("material_id")
        if isinstance(material, str):
            found[material] = payload
        if isinstance(material_id, str):
            found[material_id] = payload
    return found, errors


def _match_saved(peak: dict[str, Any], saved_modes: list[Any]) -> dict[str, Any] | None:
    best: dict[str, Any] | None = None
    best_distance: float | None = None
    for mode in saved_modes:
        if not isinstance(mode, dict) or not _same_symmetry(peak.get("symmetry"), mode.get("symmetry")):
            continue
        frequency = mode.get("frequency_cm-1")
        if isinstance(frequency, bool) or not isinstance(frequency, (int, float)):
            continue
        distance = abs(float(frequency) - float(peak["frequency_cm-1"]))
        if distance > 0.05:
            continue
        if best_distance is None or distance < best_distance:
            best = mode
            best_distance = distance
    return best


def _export_error_for(material: Any, material_id: str | None, errors: list[str]) -> str | None:
    for message in errors:
        low = message.casefold()
        if material_id and material_id.casefold() in low:
            return message
        if isinstance(material, str) and "silicon" in material.casefold() and "silicon" in low:
            return message
    return None


def draw_modes(card: dict[str, Any], exports: dict[str, dict[str, Any]] | None = None, export_errors: list[str] | None = None) -> dict[str, Any]:
    """Structured atomic scenes for one mode card.

    Scenes come only from a saved phonon export. This does not call Materials
    Project, does not run Phonopy, and does not invent displacements.
    """
    if exports is None or export_errors is None:
        loaded, loaded_errors = load_saved_exports()
        if exports is None:
            exports = loaded
        if export_errors is None:
            export_errors = loaded_errors
    peaks, skipped = card_peak_rows(card)
    material = card.get("material") if isinstance(card, dict) else None
    material_id = MATERIAL_PROJECT_IDS.get(material) if isinstance(material, str) else None
    payload = None
    if isinstance(material, str):
        payload = exports.get(material)
    if payload is None and material_id:
        payload = exports.get(material_id)
    parse_error = _export_error_for(material, material_id, export_errors)
    saved_modes = payload.get("modes") if isinstance(payload, dict) else []
    if not isinstance(saved_modes, list):
        saved_modes = []
    structure = payload.get("structure") if isinstance(payload, dict) else {}
    if not isinstance(structure, dict):
        structure = {}
    species = structure.get("species") if isinstance(structure.get("species"), list) else []
    atom_count = structure.get("atom_count")
    if not isinstance(atom_count, int):
        atom_count = len(species)
    notes: list[str] = []
    if skipped:
        named = ", ".join(str(row.get("label") or row.get("symmetry")) for row in skipped)
        notes.append(
            f"{len(skipped)} card row(s) have no frequency ({named}), so they were not drawn and no displacement was invented."
        )
    if any(peak.get("motion") is None for peak in peaks):
        notes.append("One or more mode-card motion fields are null. Those fields were not turned into displacements.")
    modes: list[dict[str, Any]] = []
    for peak in peaks:
        if payload is None:
            reason = parse_error or (
                "no retrieved eigenvalues for this material (Materials Project was not called)"
                if material_id
                else "no retrieved eigenvalues for this material, and no Materials Project id is configured for this card"
            )
            modes.append({**peak, "status": "animation_unavailable", "reason": reason, "scene": None})
            continue
        match = _match_saved(peak, saved_modes)
        if match is None:
            modes.append(
                {
                    **peak,
                    "status": "animation_unavailable",
                    "reason": "no retrieved eigenvalues for this mode",
                    "scene": None,
                }
            )
            continue
        animation = match.get("animation")
        if match.get("status") == "verified" and _frames_are_real(animation, int(atom_count or 0)):
            modes.append(
                {
                    **peak,
                    "status": "verified",
                    "reason": None,
                    "calculated_frequency_cm-1": match.get("calculated_frequency_cm-1"),
                    "symmetry_check": match.get("symmetry_check"),
                    "scene": {
                        "species": species,
                        "lattice_angstrom": structure.get("lattice_angstrom"),
                        "frames": animation["frames"],
                        "amplitude_angstrom": animation.get("amplitude_angstrom"),
                        "source": "retrieved eigendisplacements",
                        "material_id": payload.get("material_id"),
                        "export_path": payload.get("_path"),
                    },
                }
            )
            continue
        reason = match.get("reason") or "eigenvalues were not stored for this mode"
        if not _frames_are_real(animation, int(atom_count or 0)) and match.get("status") == "verified":
            reason = "retrieved frames are missing or not finite; displacements were not invented"
        modes.append({**peak, "status": "animation_unavailable", "reason": reason, "scene": None})
    modes.extend(skipped)
    return {
        "material": material,
        "material_id": material_id,
        "export_path": None if not isinstance(payload, dict) else payload.get("_path"),
        "export_errors": export_errors,
        "skipped_without_frequency": len(skipped),
        "notes": notes,
        "modes": modes,
    }


def build_export(card_path: Path, output: Path) -> dict[str, Any]:
    api_key = os.getenv("MP_API_KEY")
    if not api_key:
        raise DataBlocker("MP_API_KEY is not set in the process environment")
    from mp_api.client import MPRester

    card = json.loads(card_path.read_text())
    material = card["material"]
    material_id = MATERIAL_PROJECT_IDS.get(material)
    if not material_id:
        raise DataBlocker(f"no verified Materials Project ID configured for {material!r}")
    peaks = active_peaks(card)
    if not peaks:
        raise DataBlocker(f"no numeric Raman-active peaks in {card_path}")

    with MPRester(api_key) as mpr:
        structure = mpr.get_structure_by_material_id(material_id)
        phonon_bs = mpr.get_phonon_bandstructure_by_material_id(material_id)
        try:
            # Explicit DFPT bandstructure endpoint, separate from the legacy
            # convenience call above.
            dfpt_bs = mpr.materials.phonon.get_bandstructure_from_material_id(material_id, "dfpt")
            dfpt_error = None
        except Exception as exc:
            dfpt_bs = None
            dfpt_error = f"{type(exc).__name__}: {exc}"

    phonon_bs = as_pymatgen_bandstructure(phonon_bs)
    dfpt_bs = as_pymatgen_bandstructure(dfpt_bs)
    direct_info = describe_bandstructure(phonon_bs)
    dfpt_info = describe_bandstructure(dfpt_bs)
    selected_bs = dfpt_bs if dfpt_info.get("has_eigendisplacements") else phonon_bs
    selected_source = "dfpt" if selected_bs is dfpt_bs else "convenience"
    modes = [matching_record(peak, selected_bs, material_id) for peak in peaks]
    payload = {
        "schema_version": "phaselens-phonon-animation-1.0",
        "material": material,
        "material_id": material_id,
        "mode_card": str(card_path),
        "structure": {
            "atom_count": len(structure),
            "species": [str(site.specie) for site in structure],
            "lattice_angstrom": structure.lattice.matrix.tolist(),
            "fractional_coordinates": structure.frac_coords.tolist(),
        },
        "sources": {
            "convenience_phonon_endpoint": direct_info,
            "dfpt_endpoint": {**dfpt_info, "retrieval_error": dfpt_error},
            "selected": selected_source,
        },
        "modes": modes,
        "marimo_ready": all(mode["status"] == "verified" for mode in modes),
    }
    # This is the only frame-producing path. Current MP records without
    # eigendisplacements never enter it.
    for mode in modes:
        if mode["status"] == "verified":
            gamma = gamma_index(selected_bs)
            frames = frames_for_verified_mode(selected_bs, mode["gamma_band_index_zero_based"], gamma)
            validation = animation_validation(frames, len(selected_bs.structure))
            if not all(validation.values()):
                mode["status"] = "animation_unavailable"
                mode["reason"] = "eigenvector_animation_validation_failed"
            else:
                mode["animation"] = {"amplitude_angstrom": VISUALIZATION_AMPLITUDE_ANGSTROM, "frames": frames}
            mode["animation_validation"] = validation
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parents[1]
    parser.add_argument("--mode-card", type=Path, default=root / "mode_cards" / "silicon.json")
    parser.add_argument("--output", type=Path, default=root / "data/generated/silicon_mp149_raman_modes.json")
    args = parser.parse_args()
    try:
        payload = build_export(args.mode_card, args.output)
    except DataBlocker as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"status": "PASS", "output": str(args.output), "material_id": payload["material_id"], "retrieved_fields": payload["sources"], "modes": payload["modes"], "marimo_ready": payload["marimo_ready"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
