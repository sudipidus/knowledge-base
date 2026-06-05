"""wiki publish command — build and serve the wiki with Quartz."""

import subprocess

import typer


def run_publish(preview: bool = False) -> None:
    try:
        subprocess.run(["npx", "quartz", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        typer.echo("Error: Quartz is not installed. Run 'npm install' first.", err=True)
        raise typer.Exit(1)

    if preview:
        typer.echo("Starting Quartz dev server at http://localhost:8080...")
        try:
            subprocess.run(["npx", "quartz", "build", "--serve"], check=True)
        except KeyboardInterrupt:
            typer.echo("\nServer stopped.")
    else:
        typer.echo("Building static site...")
        result = subprocess.run(
            ["npx", "quartz", "build"], capture_output=True, text=True
        )
        if result.returncode == 0:
            typer.echo("Build complete. Output in public/")
        else:
            typer.echo(f"Build failed:\n{result.stderr}", err=True)
            raise typer.Exit(1)
