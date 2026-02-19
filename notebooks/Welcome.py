import marimo

__generated_with = "0.19.11"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # Welcome to Kitsune

        Kitsune is your AI-powered data science workspace. The AI assistant on the left
        can create, edit, and run cells in this notebook on your behalf.

        ## Getting started

        - **Chat** with the assistant to explore data, build visualizations, or run analysis
        - **Add cells** manually using the `+` button or keyboard shortcuts
        - **Switch notebooks** using the tabs at the top of this panel

        ## Quick reference

        | Action | Shortcut |
        |---|---|
        | Run cell | `Ctrl+Enter` |
        | Run all | `Ctrl+Shift+Enter` |
        | Add cell below | `Alt+Enter` |
        | Toggle code | `Ctrl+Y` |
        """
    )
    return ()


if __name__ == "__main__":
    app.run()
