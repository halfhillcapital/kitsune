import marimo

__generated_with = "0.19.11"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md("""
    # Sample Notebook

    This is a sample marimo notebook served in **run mode**.
    """)
    return


if __name__ == "__main__":
    app.run()
