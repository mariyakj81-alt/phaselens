import marimo

__generated_with = "0.25.2"


app = marimo.App(width="full")


@app.cell
def _():
    import json
    import os
    from pathlib import Path

    import marimo as mo

    root = Path(__file__).resolve().parents[1]
    data_path = Path(os.environ.get("PHASELENS_ANIMATION_JSON", root / "data/phonon_animations/silicon.json"))
    payload = json.loads(data_path.read_text())
    viewable = []
    for _mode_entry in payload.get("modes", []):
        if _mode_entry.get("status") == "verified" and "animation" in _mode_entry:
            viewable.append((_mode_entry, None))
        elif _mode_entry.get("status") == "frequency_based_candidate":
            for _candidate_entry in _mode_entry.get("candidates", []):
                if "animation" in _candidate_entry:
                    viewable.append((_mode_entry, _candidate_entry))
    options = {}
    for index, (_mode_entry, _candidate_entry) in enumerate(viewable):
        _calculated = _candidate_entry or _mode_entry
        _state = "confirmed" if _candidate_entry is None else "frequency candidate — symmetry unverified"
        options[f"{_mode_entry.get('label') or _mode_entry.get('symmetry')} · {_calculated['calculated_frequency_cm-1']:.3f} cm⁻¹ (Δ {_calculated['frequency_delta_cm-1']:.3f}) · {_state}"] = str(index)
    options = options or {"No visualizable modes": "-1"}
    mode_selector = mo.ui.dropdown(options=options, value=next(iter(options.values())), label="Phonon mode")
    amplitude = mo.ui.slider(start=0.25, stop=2.0, step=0.25, value=1.0, label="Visualization amplitude ×")
    speed = mo.ui.slider(start=50, stop=500, step=50, value=150, label="Frame duration (ms)")
    mo.vstack([
        mo.md("# PhaseLens phonon viewer\nThe viewer performs no API calls or recalculation; it reads the saved phonon-animation JSON."),
        mo.hstack([mode_selector, amplitude, speed], justify="start"),
    ])
    return amplitude, data_path, mode_selector, payload, speed, viewable


@app.cell
def _(amplitude, mo, mode_selector, payload, speed, viewable):
    from itertools import product

    import numpy as np
    import plotly.graph_objects as go

    selected = int(mode_selector.value)
    mo.stop(selected < 0 or not viewable, mo.callout(f"Cannot visualize this mode: {payload.get('reason', 'the input contains no usable real-eigenvector mode')}", kind="warn"))

    parent_mode, selected_candidate = viewable[selected]
    selected_mode = {**parent_mode, **(selected_candidate or {})}
    animation = selected_mode["animation"]
    structure = payload["structure"]
    species = structure["species"]
    lattice = np.asarray(structure["lattice_angstrom"], dtype=float)
    equilibrium = np.asarray(
        structure.get("equilibrium_cartesian_coordinates_angstrom")
        or np.asarray(structure["fractional_coordinates"], dtype=float) @ lattice,
        dtype=float,
    )
    saved_displacements = np.asarray([frame["displacements_angstrom"] for frame in animation["frames"]], dtype=float)
    # The multiplier is a display-only control applied to saved displacements;
    # no new motion, coordinate transform, or atom reordering is introduced.
    displacements = saved_displacements * amplitude.value
    coordinates = equilibrium[None, :, :] + displacements

    bit_corners = list(product((0, 1), repeat=3))
    corners = np.asarray([np.asarray(bits) @ lattice for bits in bit_corners])
    edge_x, edge_y, edge_z = [], [], []
    for left, bits in enumerate(bit_corners):
        for axis in range(3):
            if bits[axis] == 0:
                other = list(bits)
                other[axis] = 1
                right = bit_corners.index(tuple(other))
                edge_x += [corners[left, 0], corners[right, 0], None]
                edge_y += [corners[left, 1], corners[right, 1], None]
                edge_z += [corners[left, 2], corners[right, 2], None]

    extent_points = np.vstack([corners, coordinates.reshape(-1, 3)])
    center = (extent_points.min(axis=0) + extent_points.max(axis=0)) / 2
    half_width = float(np.max(extent_points.max(axis=0) - extent_points.min(axis=0)) / 2 + 0.2)
    axis_range = [[center[axis] - half_width, center[axis] + half_width] for axis in range(3)]

    def atoms_trace(points):
        return go.Scatter3d(
            x=points[:, 0], y=points[:, 1], z=points[:, 2], mode="markers+text",
            text=[f"{element} {index + 1}" for index, element in enumerate(species)], textposition="top center",
            marker={"size": 10, "color": "#d99620", "line": {"color": "#522e00", "width": 1}}, name="atoms",
            hovertemplate="%{text}<br>x=%{x:.5f} Å<br>y=%{y:.5f} Å<br>z=%{z:.5f} Å<extra></extra>",
        )

    def arrow_lines(displacement):
        values = []
        for start, vector in zip(equilibrium, displacement, strict=True):
            values.extend([start, start + vector, [None, None, None]])
        values = np.asarray(values, dtype=object)
        return go.Scatter3d(x=values[:, 0], y=values[:, 1], z=values[:, 2], mode="lines", line={"color": "#2563eb", "width": 5}, name="saved displacement", hoverinfo="skip")

    def arrow_heads(displacement):
        return go.Cone(
            x=equilibrium[:, 0], y=equilibrium[:, 1], z=equilibrium[:, 2],
            u=displacement[:, 0], v=displacement[:, 1], w=displacement[:, 2],
            anchor="tail", sizemode="absolute", sizeref=0.035, showscale=False,
            colorscale=[[0, "#2563eb"], [1, "#2563eb"]], name="displacement direction", hoverinfo="skip",
        )

    figure_frames = [
        go.Frame(name=str(index), data=[atoms_trace(point), arrow_lines(vector), arrow_heads(vector)], traces=[0, 1, 2])
        for index, (point, vector) in enumerate(zip(coordinates, displacements, strict=True))
    ]
    steps = [
        {"label": str(index), "method": "animate", "args": [[str(index)], {"mode": "immediate", "frame": {"duration": 0, "redraw": True}, "transition": {"duration": 0}}]}
        for index in range(len(figure_frames))
    ]
    figure = go.Figure(
        data=[
            atoms_trace(coordinates[0]),
            arrow_lines(displacements[0]),
            arrow_heads(displacements[0]),
            go.Scatter3d(x=edge_x, y=edge_y, z=edge_z, mode="lines", line={"color": "#64748b", "width": 3}, name="saved primitive cell", hoverinfo="skip"),
        ],
        frames=figure_frames,
    )
    figure.update_layout(
        title="Saved Materials Project Γ optical eigenvector",
        height=700, margin={"l": 0, "r": 0, "b": 0, "t": 50}, uirevision=f"mode-{selected}",
        scene={
            "aspectmode": "cube",
            "xaxis": {"title": "x (Å)", "range": axis_range[0]},
            "yaxis": {"title": "y (Å)", "range": axis_range[1]},
            "zaxis": {"title": "z (Å)", "range": axis_range[2]},
            "camera": {"eye": {"x": 1.55, "y": 1.55, "z": 1.2}, "up": {"x": 0, "y": 0, "z": 1}},
        },
        updatemenus=[{"type": "buttons", "showactive": False, "x": 0.05, "y": 0.0, "buttons": [
            {"label": "▶ Play", "method": "animate", "args": [None, {"fromcurrent": True, "frame": {"duration": speed.value, "redraw": True}, "transition": {"duration": 0}}]},
            {"label": "❚❚ Pause", "method": "animate", "args": [[None], {"mode": "immediate", "frame": {"duration": 0, "redraw": False}, "transition": {"duration": 0}}]},
        ]}],
        sliders=[{"active": 0, "currentvalue": {"prefix": "Frame: "}, "pad": {"t": 45}, "steps": steps}],
    )
    mo.vstack([
        mo.md(f"**Experimental:** {selected_mode['frequency_cm-1']:.3f} cm⁻¹ · **Calculated:** {selected_mode['calculated_frequency_cm-1']:.3f} cm⁻¹ · **Mode:** Γ optical, bands {selected_mode.get('degenerate_band_indices_zero_based', [selected_mode['gamma_band_index_zero_based']])} ({selected_mode.get('symmetry')})\n\n{'**Frequency-based candidate; Raman activity and symmetry unverified.**' if selected_candidate else '**Confirmed assignment.**'} Blue arrows show the saved displacement vectors. The base amplitude is **{animation['amplitude_angstrom']:.2f} Å**; the amplitude and speed controls are visualization-only."),
        mo.ui.plotly(figure),
    ])
    return


if __name__ == "__main__":
    app.run()
