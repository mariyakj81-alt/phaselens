import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import backend_adapter as ba

    return ba, mo, pd


@app.cell
def _(ba, mo):
    examples = ba.list_examples()
    dropdown = mo.ui.dropdown(options=examples, value=examples[0], label="Built-in example")
    upload = mo.ui.file(kind="area", filetypes=[".csv"], label="Or upload a CSV (shift, intensity)")
    model_answer = mo.ui.text_area(
        label="Model answer JSON (optional). Leave empty: the model is not called and peaks stay unassigned.",
        full_width=True,
    )
    mo.vstack([
        mo.md("# PhaseLens\nRaman peak symmetry assignment"),
        mo.md("## 1. Input"),
        dropdown,
        upload,
        model_answer,
    ])
    return dropdown, model_answer, upload


@app.cell
def _(ba, dropdown, mo):
    cards = ba.list_mode_cards()
    default = ba.default_card(dropdown.value)
    if cards and default not in cards:
        default = cards[0]
    card = mo.ui.dropdown(options=cards, value=default, label="Mode card")
    mo.vstack([
        mo.md("The checker and the atomic picture use this card. Changing the example resets it."),
        card,
    ])
    return (card,)


@app.cell
def _(ba, card, dropdown, mo, model_answer, upload):
    try:
        pasted = (model_answer.value or "").strip() or None
        if upload.value:
            data, filename = ba.read_upload(upload)
            loaded = ba.parse_uploaded_csv(data, filename)
            record = None
        else:
            loaded, record = ba.load_example(dropdown.value)
        result = ba.analyze_spectrum(loaded, mode_card=card.value, record=record, model_text=pasted)
    except Exception as exc:
        mo.stop(True, mo.callout(f"Could not run this example: {exc}", kind="danger"))
    return (result,)


@app.cell
def _(mo, result):
    assignment = result.get("assignment") or {}
    notes = [mo.callout(warning, kind="warn") for warning in result["warnings"]]
    mo.vstack([
        mo.md(
            f"**Showing:** `{result['name']}` | **Card:** `{result.get('mode_card')}` | "
            f"**Status:** `{result['status']}` | **Assignment:** `{assignment.get('source')}` | "
            f"**Checker passed:** `{assignment.get('checker_passed')}`"
        ),
        *notes,
    ])
    return


@app.cell
def _(mo, result):
    import plotly.graph_objects as go

    curve = result["spectrum"]
    corrected = curve["corrected"] if curve["corrected"] is not None else []
    fig = go.Figure()
    fig.add_scatter(x=curve["shift"], y=curve["raw"], name="Raw", line=dict(width=1))
    fig.add_scatter(x=curve["shift"], y=corrected, name="Background-corrected")
    for peak in result["peaks"]:
        if peak["is_artifact"]:
            fig.add_vline(
                x=peak["position_cm1"],
                line_dash="dot",
                line_color="gray",
                annotation_text="artifact",
                annotation_position="top",
            )
    fig.update_layout(
        xaxis_title="Raman shift (cm^-1)",
        yaxis_title="Intensity (a.u.)",
        height=420,
        margin=dict(t=30),
    )
    mo.vstack([
        mo.md("## 2. Spectrum"),
        fig,
        mo.md(f"*Background correction: {curve['corrected_source']}*"),
    ])
    return


@app.cell
def _(mo, pd, result):
    peak_rows = [{
        "Position (cm^-1)": round(peak["position_cm1"], 2),
        "Intensity": None if peak["intensity"] is None else round(float(peak["intensity"]), 4),
        "Symmetry": peak["symmetry"],
        "Artifact?": (
            ("artifact: " + peak["artifact_reason"]) if peak["is_artifact"]
            else (peak.get("artifact_hint") or "")
        ),
    } for peak in result["peaks"]]
    table = mo.ui.table(pd.DataFrame(peak_rows), selection=None) if peak_rows else mo.md("_No peaks found._")
    mo.vstack([mo.md("## 3 & 4. Peak results and checker labels"), table])
    return


@app.cell
def _(mo, result):
    interpretation = result["interpretation"]
    interpretation_body = (
        mo.md(f"**{interpretation['label']}:** {interpretation['value']}  \n{interpretation.get('note', '')}")
        if interpretation
        else mo.md("_No layer-number or strain result available for this spectrum._")
    )
    mo.vstack([mo.md("## 5. Material interpretation"), interpretation_body])
    return


@app.cell
def _(mo, pd, result):
    visualization = result["visualization"]
    blocks = [mo.md("## 6. Atomic visualization")]
    for note in visualization.get("notes") or []:
        blocks.append(mo.callout(note, kind="warn"))
    if visualization.get("image_path"):
        blocks.append(mo.image(src=visualization["image_path"]))
    mode_rows = []
    plotly_ui = getattr(mo.ui, "plotly", None)
    for mode in visualization.get("modes") or []:
        frequency = mode.get("frequency_cm-1")
        calculated = mode.get("calculated_frequency_cm-1")
        mode_rows.append({
            "Mode": mode.get("label") or "",
            "Symmetry": mode.get("symmetry"),
            "Card cm^-1": None if frequency is None else round(float(frequency), 2),
            "Calculated cm^-1": None if calculated is None else round(float(calculated), 2),
            "Picture": "drawn from retrieved eigenvalues" if mode.get("available") else (mode.get("reason") or "unavailable"),
        })
        if mode.get("available") and mode.get("figure") is not None:
            blocks.append(mo.md(f"**{mode.get('symmetry')}** at {frequency:g} cm^-1"))
            if mode.get("caption"):
                blocks.append(mo.md(mode["caption"]))
            blocks.append(plotly_ui(mode["figure"]) if plotly_ui else mode["figure"])
    blocks.append(mo.ui.table(pd.DataFrame(mode_rows), selection=None) if mode_rows else mo.md("_No card modes with a frequency._"))
    mo.vstack(blocks)
    return


@app.cell
def _(mo, result):
    refs = result["references"]
    reference_body = (
        mo.md("\n".join(f"- {ref['citation']} {ref.get('doi', '')}" for ref in refs))
        if refs
        else mo.md("_No citation on this mode card._")
    )
    mo.vstack([mo.md("## 7. References"), reference_body])
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
