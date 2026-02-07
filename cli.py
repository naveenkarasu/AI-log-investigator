import json
from pathlib import Path
import requests
import typer

app = typer.Typer(help="AI Log Investigator CLI")

API_URL = "http://127.0.0.1:8000"


def analyze_text(log_text: str) -> dict:
    """
    Send log text to the local API and return JSON response.
    """
    resp = requests.post(
        f"{API_URL}/analyze",
        json={"log_text": log_text},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


@app.command("health")
def health():
    """
    Check if API is running.
    """
    resp = requests.get(f"{API_URL}/health", timeout=10)
    typer.echo(json.dumps(resp.json(), indent=2))


@app.command("analyze")
def analyze(
    file: Path = typer.Argument(..., exists=True, readable=True, help="Path to a log file"),
):
    """
    Analyze a single log file.
    """
    log_text = file.read_text(encoding="utf-8", errors="ignore")
    result = analyze_text(log_text)
    typer.echo(json.dumps(result, indent=2))


@app.command("analyze-dir")
def analyze_dir(
    log_dir: Path = typer.Argument(..., exists=True, file_okay=False, help="Directory with log files"),
    out_dir: Path = typer.Option(
        Path("reports"),
        "--out",
        help="Directory to save analysis results",
    ),
):
    """
    Analyze all log files in a directory and save reports.
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    log_files = list(log_dir.glob("*.log")) + list(log_dir.glob("*.txt"))

    if not log_files:
        typer.echo("❌ No .log or .txt files found")
        raise typer.Exit(code=1)

    typer.echo(f"🔍 Found {len(log_files)} log files. Starting analysis...\n")

    for idx, log_file in enumerate(log_files, start=1):
        typer.echo(f"[{idx}/{len(log_files)}] Analyzing {log_file.name}")

        try:
            log_text = log_file.read_text(encoding="utf-8", errors="ignore")
            result = analyze_text(log_text)

            out_file = out_dir / f"{log_file.stem}_analysis.json"
            out_file.write_text(json.dumps(result, indent=2))

        except Exception as e:
            typer.echo(f"❌ Failed on {log_file.name}: {e}")

    typer.echo(f"\n✅ Analysis complete. Reports saved to: {out_dir}")


if __name__ == "__main__":
    app()

