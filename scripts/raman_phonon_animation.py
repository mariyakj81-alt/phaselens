#!/usr/bin/env python3
"""Conservative Raman JSON -> Materials Project phonon-animation payload.

This is a viewer-data adapter, not material identification or a phonon solver.
It uses only stored Raman assignments and real Materials Project eigenvectors.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


THZ_TO_CM1 = 33.3564
FRAME_COUNT = 12
BASE_VISUALIZATION_AMPLITUDE_ANGSTROM = 0.08
FREQUENCY_TOLERANCE = "max(12 cm^-1, 5% of the accepted Raman shift)"


@dataclass(frozen=True)
class MaterialSpec:
    mp_id: str
    formula: str
    space_group_number: int
    phase: str
    bulk_only: bool = False


# Verified against the MP structures before this general adapter was added.
# MoS2 is intentionally bulk-only: an MP bulk structure is never substituted
# for a card/result that names a supported monolayer or few-layer sample.
MATERIALS = {
    "pristine diamond-cubic Si-I": MaterialSpec("mp-149", "Si", 227, "Si-I"),
    "quartz": MaterialSpec("mp-7000", "SiO2", 152, "alpha-quartz"),
    "calcite (CaCO3)": MaterialSpec("mp-3953", "CaCO3", 167, "calcite"),
    "anatase (TiO2)": MaterialSpec("mp-390", "TiO2", 141, "anatase"),
    "molybdenum disulfide": MaterialSpec("mp-2815", "MoS2", 194, "2H bulk", bulk_only=True),
}


class CannotVisualize(RuntimeError):
    """Expected, user-actionable absence of a safe visualization."""


def cannot(reason: str, **details: Any) -> dict[str, Any]:
    return {"status": "Cannot visualize this mode", "reason": reason, **details}


def card_peaks(card: dict[str, Any]) -> list[dict[str, Any]]:
    peaks: list[dict[str, Any]] = []
    for entry in card.get("curated_expected_modes", []):
        if (entry.get("raman_activity", "active") != "active" and not entry.get("raman_active")) or entry.get("position_cm-1") is None:
            continue
        peaks.append({"frequency_cm-1": float(entry["position_cm-1"]), "symmetry": entry.get("symmetry"), "label": entry.get("mode"), "source": "mode_card"})
    for entry in card.get("modes", []):
        if (entry.get("raman_activity") != "active" and not entry.get("raman_active")) or entry.get("position_cm1") is None:
            continue
        peaks.append({"frequency_cm-1": float(entry["position_cm1"]), "symmetry": entry.get("symmetry"), "label": entry.get("id", entry.get("mode")), "source": "mode_card"})
    return peaks


def accepted_result_peaks(result: dict[str, Any]) -> list[dict[str, Any]]:
    """Read only assigned non-artifact peaks from the existing result schema."""
    answers = {
        round(float(answer["position_cm-1"]), 4): answer
        for answer in result.get("answers", [])
        if answer.get("source") == "mode" and answer.get("label") not in {None, "artifact", "unassigned"}
    }
    peaks = []
    for peak in result.get("peaks", []):
        shift = float(peak["position_cm-1"])
        answer = answers.get(round(shift, 4))
        if answer:
            peaks.append({"frequency_cm-1": shift, "symmetry": answer["label"], "label": answer["label"], "source": "result_json"})
    return peaks


def input_descriptor(card: dict[str, Any], result: dict[str, Any] | None) -> tuple[str, str | None, str | None, str | None, list[dict[str, Any]]]:
    material = card.get("material")
    if not material:
        raise CannotVisualize("lookup_failure: mode card has no material name")
    card_phases = {entry.get("phase") for entry in card.get("curated_expected_modes", []) if entry.get("phase")}
    phase = next(iter(card_phases)) if len(card_phases) == 1 else None
    layer = None
    peaks = card_peaks(card)
    if result:
        context = result.get("context", {})
        if context.get("material") and context["material"] != material:
            raise CannotVisualize(f"input_mismatch: result material {context['material']!r} does not match mode card {material!r}")
        phase = context.get("phase")
        layer = context.get("layer")
        peaks = accepted_result_peaks(result)
    if not peaks:
        raise CannotVisualize("no accepted Raman-active peaks in input")
    return material, card.get("formula"), phase, layer, peaks


def resolve_material(material: str, phase: str | None, layer: str | None) -> MaterialSpec:
    spec = MATERIALS.get(material)
    if not spec:
        raise CannotVisualize(f"lookup_failure: no verified Materials Project mapping for {material!r}")
    if spec.bulk_only and layer not in {None, "bulk"}:
        raise CannotVisualize(f"lookup_failure: no monolayer/few-layer MP mapping for {material!r}; bulk was not substituted for {layer}")
    if spec.bulk_only and phase and phase != "2H":
        raise CannotVisualize(f"lookup_failure: requested phase {phase!r} is not the verified 2H bulk mapping")
    return spec


def to_pmg(phonon_bs: Any) -> Any:
    return phonon_bs.to_pmg if phonon_bs is not None and not hasattr(phonon_bs, "bands") and hasattr(phonon_bs, "to_pmg") else phonon_bs


def cache_path(cache_dir: Path, material_id: str) -> Path:
    return cache_dir / f"{material_id}_dfpt.json"


def load_or_retrieve(spec: MaterialSpec, cache_dir: Path, force_refresh: bool) -> tuple[Any, Any, str]:
    """Cache only a fully retrieved MP structure + DFPT bandstructure pair."""
    from monty.json import MontyDecoder, MontyEncoder

    path = cache_path(cache_dir, spec.mp_id)
    if path.exists() and not force_refresh:
        cached = json.loads(path.read_text(), cls=MontyDecoder)
        return cached["mp_structure"], cached["phonon_structure"], "cache"

    api_key = os.getenv("MP_API_KEY")
    if not api_key:
        raise CannotVisualize("api_configuration_error: MP_API_KEY is not set")
    try:
        from mp_api.client import MPRester

        with MPRester(api_key) as mpr:
            mp_structure = mpr.get_structure_by_material_id(spec.mp_id)
            raw_bs = mpr.materials.phonon.get_bandstructure_from_material_id(spec.mp_id, "dfpt")
    except Exception as exc:
        message = f"{type(exc).__name__}: {exc}"
        if any(token in message.lower() for token in ("connection", "timeout", "dns", "network")):
            raise CannotVisualize(f"api_or_network_error: {message}") from exc
        raise CannotVisualize(f"phonon_retrieval_error: {message}") from exc
    phonon_bs = to_pmg(raw_bs)
    if mp_structure is None or phonon_bs is None or phonon_bs.structure is None:
        raise CannotVisualize("phonon_data_unavailable: MP response lacks structure or DFPT bandstructure")
    cache_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"mp_structure": mp_structure, "phonon_structure": phonon_bs}, cls=MontyEncoder, indent=2) + "\n")
    return mp_structure, phonon_bs, "dfpt_api"


def verify_structure(mp_structure: Any, phonon_bs: Any, spec: MaterialSpec) -> None:
    from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

    if mp_structure.composition.reduced_formula != spec.formula:
        raise CannotVisualize(f"lookup_failure: MP composition {mp_structure.composition.reduced_formula} does not match {spec.formula}")
    phonon_structure = phonon_bs.structure
    if phonon_structure.composition.reduced_formula != spec.formula:
        raise CannotVisualize("phonon_data_inconsistent: phonon structure composition differs from mapped material")
    space_group = SpacegroupAnalyzer(phonon_structure, symprec=0.1).get_space_group_number()
    if space_group != spec.space_group_number:
        raise CannotVisualize(f"lookup_failure: MP space group #{space_group} differs from verified mapping #{spec.space_group_number}")


def gamma_index(phonon_bs: Any) -> int:
    norms = [float(np.linalg.norm(qpoint.frac_coords)) for qpoint in phonon_bs.qpoints]
    index = int(np.argmin(norms))
    if norms[index] > 1e-7:
        raise CannotVisualize(f"phonon_data_unavailable: no Gamma q-point (closest norm {norms[index]:.3e})")
    return index


def frames_from_eigenvector(phonon_bs: Any, band: int, gamma: int) -> tuple[list[dict[str, Any]], list[list[float]], list[list[float]]]:
    eigenvector = np.asarray(phonon_bs.eigendisplacements[band, gamma], dtype=complex)
    atom_count = len(phonon_bs.structure)
    if eigenvector.shape != (atom_count, 3) or not np.isfinite(eigenvector.real).all() or not np.isfinite(eigenvector.imag).all():
        raise CannotVisualize("phonon_data_inconsistent: eigendisplacement shape/values do not match phonon structure")
    maximum = float(np.max(np.linalg.norm(eigenvector, axis=1)))
    if not math.isfinite(maximum) or maximum <= 0:
        raise CannotVisualize("phonon_data_unavailable: selected eigenvector is zero")
    equilibrium = np.asarray(phonon_bs.structure.cart_coords, dtype=float)
    scaled = eigenvector / maximum * BASE_VISUALIZATION_AMPLITUDE_ANGSTROM
    frames = []
    for frame in range(FRAME_COUNT):
        phase = 2 * math.pi * frame / FRAME_COUNT
        displacement = np.real(scaled * np.exp(1j * phase))
        frames.append({"phase_radians": phase, "displacements_angstrom": displacement.tolist(), "cartesian_coordinates_angstrom": (equilibrium + displacement).tolist()})
    return frames, eigenvector.real.tolist(), eigenvector.imag.tolist()


def animation_for_band(phonon_bs: Any, band: int, gamma: int) -> dict[str, Any]:
    """Export one real MP eigenvector without changing its atom ordering."""
    frames, eigen_real, eigen_imag = frames_from_eigenvector(phonon_bs, band, gamma)
    displacement = np.asarray([frame["displacements_angstrom"] for frame in frames], dtype=float)
    checks = {
        "vectors_match_atoms": displacement.shape[1] == len(phonon_bs.structure),
        "displacements_finite_nonzero": bool(np.isfinite(displacement).all() and np.any(abs(displacement) > 0)),
        "oscillates_about_equilibrium": bool(np.allclose(displacement[0], -displacement[FRAME_COUNT // 2], atol=1e-8)),
    }
    if not all(checks.values()):
        raise CannotVisualize("eigenvector_animation_validation_failed")
    return {
        "eigenvector_real": eigen_real,
        "eigenvector_imaginary": eigen_imag,
        "animation": {
            "amplitude_angstrom": BASE_VISUALIZATION_AMPLITUDE_ANGSTROM,
            "amplitude_note": "visualization-only; normalized from the saved real eigenvector",
            "frames": frames,
        },
        "validation": checks,
    }


def degenerate_groups(indices: list[int], frequencies: np.ndarray) -> list[list[int]]:
    """Keep numerically degenerate Γ modes together, never as silent alternatives."""
    groups: list[list[int]] = []
    for index in sorted(indices, key=lambda value: float(frequencies[value])):
        if groups and abs(frequencies[index] - frequencies[groups[-1][0]]) < 0.1:
            groups[-1].append(index)
        else:
            groups.append([index])
    return groups


def match_peak(peak: dict[str, Any], phonon_bs: Any, spec: MaterialSpec) -> dict[str, Any]:
    if not bool(getattr(phonon_bs, "has_eigendisplacements", False)):
        return {**peak, **cannot("real_eigendisplacements_unavailable")}
    gamma = gamma_index(phonon_bs)
    frequencies = np.asarray(phonon_bs.bands, dtype=float)[:, gamma] * THZ_TO_CM1
    optical = np.arange(len(frequencies)) >= 3
    band = int(np.argmin(np.where(optical, abs(frequencies - peak["frequency_cm-1"]), np.inf)))
    delta = float(abs(frequencies[band] - peak["frequency_cm-1"]))
    tolerance = max(12.0, 0.05 * peak["frequency_cm-1"])
    result = {**peak, "gamma_band_index_zero_based": band, "calculated_frequency_cm-1": float(frequencies[band]), "frequency_delta_cm-1": delta, "frequency_tolerance_cm-1": tolerance, "frequency_tolerance_rule": FREQUENCY_TOLERANCE}
    if delta > tolerance:
        return {**result, **cannot("no Gamma optical mode within frequency tolerance")}
    degenerate = [index for index, frequency in enumerate(frequencies) if abs(frequency - frequencies[band]) < 0.1]
    # MP does not serialize irreps. Silicon is the one existing card with a
    # literature-backed F2g assignment and a uniquely consistent optical triplet.
    if spec.mp_id == "mp-149" and peak.get("symmetry") in {"F2g", "T2g"} and len(phonon_bs.structure) == 2 and len(degenerate) == 3:
        exported = animation_for_band(phonon_bs, band, gamma)
        displacement = np.asarray([frame["displacements_angstrom"] for frame in exported["animation"]["frames"]], dtype=float)
        checks = {**exported["validation"], "opposite_silicon_sublattices": bool(np.allclose(displacement[:, 0], -displacement[:, 1], atol=1e-8))}
        if not all(checks.values()):
            return {**result, **cannot("eigenvector_animation_validation_failed"), "validation": checks}
        return {
            **result,
            "status": "verified",
            "symmetry_check": "consistent with the card's literature-backed F2g assignment: diamond Fd-3m Si and a threefold Gamma optical set; MP itself provides no irrep label",
            "degenerate_band_indices_zero_based": degenerate,
            **exported,
            "validation": checks,
        }
    candidate_indices = [index for index, frequency in enumerate(frequencies) if optical[index] and abs(frequency - peak["frequency_cm-1"]) <= tolerance]
    candidates = []
    for group in degenerate_groups(candidate_indices, frequencies):
        representative = min(group, key=lambda index: abs(frequencies[index] - peak["frequency_cm-1"]))
        try:
            exported = animation_for_band(phonon_bs, representative, gamma)
        except CannotVisualize as exc:
            return {**result, **cannot(str(exc))}
        candidates.append({
            "gamma_band_index_zero_based": representative,
            "degenerate_band_indices_zero_based": group,
            "calculated_frequency_cm-1": float(frequencies[representative]),
            "frequency_delta_cm-1": float(abs(frequencies[representative] - peak["frequency_cm-1"])),
            **exported,
        })
    return {
        **result,
        "status": "frequency_based_candidate",
        "assignment_label": "Frequency-based candidate; Raman activity and symmetry unverified.",
        "symmetry_check": "MP DFPT bandstructure has no irrep labels; frequency proximity is not a symmetry assignment.",
        "candidate_count": len(candidates),
        "candidates": candidates,
    }


def make_payload(card_path: Path, result_path: Path | None, output: Path, cache_dir: Path, force_refresh: bool) -> dict[str, Any]:
    card = json.loads(card_path.read_text())
    result = json.loads(result_path.read_text()) if result_path else None
    try:
        material, formula, phase, layer, peaks = input_descriptor(card, result)
        spec = resolve_material(material, phase, layer)
        mp_structure, phonon_bs, retrieval_source = load_or_retrieve(spec, cache_dir, force_refresh)
        verify_structure(mp_structure, phonon_bs, spec)
        phonon_structure = phonon_bs.structure  # Never mix this order with the MP structure order.
        modes = [match_peak(peak, phonon_bs, spec) for peak in peaks]
        payload = {
            "schema_version": "phaselens-phonon-animation-2.0",
            "status": "ready" if any(mode["status"] in {"verified", "frequency_based_candidate"} for mode in modes) else "Cannot visualize this mode",
            "input": {"mode_card": str(card_path), "result_json": str(result_path) if result_path else None, "material": material, "formula": formula or spec.formula, "phase": phase, "layer": layer},
            "material_id": spec.mp_id,
            "retrieval_source": retrieval_source,
            "structure": {"source": "Materials Project DFPT phonon structure", "species": [str(site.specie) for site in phonon_structure], "lattice_angstrom": phonon_structure.lattice.matrix.tolist(), "fractional_coordinates": phonon_structure.frac_coords.tolist(), "equilibrium_cartesian_coordinates_angstrom": phonon_structure.cart_coords.tolist(), "atom_count": len(phonon_structure)},
            "modes": modes,
        }
    except CannotVisualize as exc:
        payload = {"schema_version": "phaselens-phonon-animation-2.0", **cannot(str(exc)), "input": {"mode_card": str(card_path), "result_json": str(result_path) if result_path else None}, "modes": []}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
    return payload


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode-card", type=Path, required=True)
    parser.add_argument("--result-json", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--cache-dir", type=Path, default=root / "data" / "phonon_cache")
    parser.add_argument("--force-refresh", action="store_true")
    args = parser.parse_args()
    output = args.output or root / "data" / "phonon_animations" / f"{args.mode_card.stem}.json"
    payload = make_payload(args.mode_card, args.result_json, output, args.cache_dir, args.force_refresh)
    summaries = []
    for mode in payload["modes"]:
        summary = {key: value for key, value in mode.items() if key not in {"animation", "eigenvector_real", "eigenvector_imaginary", "candidates"}}
        if "candidates" in mode:
            summary["candidates"] = [{key: value for key, value in candidate.items() if key not in {"animation", "eigenvector_real", "eigenvector_imaginary"}} for candidate in mode["candidates"]]
        summaries.append(summary)
    print(json.dumps({"status": payload["status"], "output": str(output), "material_id": payload.get("material_id"), "retrieval_source": payload.get("retrieval_source"), "modes": summaries}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
