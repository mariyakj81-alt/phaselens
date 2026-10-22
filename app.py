import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import plotly.graph_objects as go
    import backend_adapter as ba

    return ba, go, mo, pd


@app.cell
def _(ba, mo):
    mo.md("# PhaseLens\nRaman peak symmetry assignment")
    examples = ba.list_examples()
    dropdown = mo.ui.dropdown(options=examples, value=examples[0], label="Built-in example")
    upload = mo.ui.file(kind="area", filetypes=[".csv"], label="Or upload a CSV (shift, intensity)")
    mo.vstack([mo.md("## 1. Input"), dropdown, upload])
    return dropdown, upload


@app.cell
def _(ba, dropdown, mo, upload):
    try:
        if upload.value:
            spectrum = ba.parse_uploaded_csv(upload.contents(), upload.name())
        else:
            spectrum = ba.load_example_spectrum(dropdown.value)
        result = ba.analyze_spectrum(spectrum)
    except Exception as e:
        mo.stop(True, mo.callout(f"Could not load spectrum: {e}", kind="danger"))
    return (result,)


@app.cell
def _(mo, result):
    notes = [mo.callout(w, kind="warn") for w in result["warnings"]]
    mo.vstack([mo.md(f"**Showing:** `{result['name']}`  |  **Status:** `{result['status']}`"), *notes])
    return


@app.cell
def _(go, mo, result):
    s = result["spectrum"]
    fig = go.Figure()
    fig.add_scatter(x=s["shift"], y=s["raw"], name="Raw", line=dict(width=1))
    fig.add_scatter(x=s["shift"], y=s["corrected"], name="Background-corrected")
    for p in result["peaks"]:
        if p["is_artifact"]:
            fig.add_vline(x=p["position_cm1"], line_dash="dot", line_color="gray",
                          annotation_text="artifact", annotation_position="top")
    fig.update_layout(xaxis_title="Raman shift (cm⁻¹)", yaxis_title="Intensity (a.u.)",
                      height=420, margin=dict(t=30))
    mo.vstack([
        mo.md("## 2. Spectrum"),
        fig,
        mo.md(f"*Background correction: {s['corrected_source']}*"),
    ])
    return


@app.cell
def _(mo, pd, result):
    rows = [{
        "Position (cm⁻¹)": round(p["position_cm1"], 1),
        "Intensity": None if p["intensity"] is None else round(float(p["intensity"]), 1),
        "Symmetry": p["symmetry"],
        "Artifact?": ("artifact: " + p["artifact_reason"]) if p["is_artifact"] else "",
    } for p in result["peaks"]]
    table = mo.ui.table(pd.DataFrame(rows), selection=None) if rows else mo.md("_No peaks found._")
    mo.vstack([mo.md("## 3 & 4. Peak results and artifact labels"), table])
    return


@app.cell
def _(mo, result):
    i = result["interpretation"]
    _body = (mo.md(f"**{i['label']}:** {i['value']}  \n{i.get('note', '')}") if i
            else mo.md("_No layer-number or strain result available for this spectrum._"))
    mo.vstack([mo.md("## 5. Material interpretation"), _body])
    return


@app.cell
def _(mo, result):
    v = result["visualization"]
    _body = mo.image(src=v["image_path"]) if v["available"] else mo.md("_Visualization unavailable._")
    mo.vstack([mo.md("## 6. Atomic visualization"), _body])
    return


@app.cell
def _(mo, result):
    refs = result["references"]
    _body = (mo.md("\n".join(f"- {r['citation']} {r.get('doi', '')}" for r in refs)) if refs
            else mo.md("_No citation available (none in the saved result)._"))
    mo.vstack([mo.md("## 7. References"), _body])
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
