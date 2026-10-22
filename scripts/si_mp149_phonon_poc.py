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


def active_peaks(card: dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize the two existing mode-card shapes."""
    peaks = []
    for mode in card.get("curated_expected_modes", []):
        frequency = mode.get("position_cm-1")
        if frequency is not None and mode.get("raman_activity", "active") == "active":
            peaks.append({"frequency_cm-1": float(frequency), "symmetry": mode.get("symmetry"), "label": mode.get("mode")})
    for mode in card.get("modes", []):
        frequency = mode.get("position_cm1")
        if frequency is not None and mode.get("raman_activity") == "active":
            peaks.append({"frequency_cm-1": float(frequency), "symmetry": mode.get("symmetry"), "label": mode.get("id", mode.get("mode"))})
    return peaks


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
