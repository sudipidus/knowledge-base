import typer

app = typer.Typer(
    name="wiki",
    help="Personal LLM-powered knowledge base CLI",
    no_args_is_help=True,
)


@app.command()
def init():
    """Initialize a new knowledge base."""
    typer.echo("wiki init - not yet implemented")


@app.command()
def ingest(source: str = typer.Argument(None), inbox: bool = False, ref: bool = False):
    """Ingest a source into the knowledge base."""
    typer.echo("wiki ingest - not yet implemented")


@app.command()
def reingest(source: str = typer.Argument(...)):
    """Re-fetch and update a previously ingested source."""
    typer.echo("wiki reingest - not yet implemented")


@app.command()
def query(question: str = typer.Argument(None), save: bool = False, interactive: bool = typer.Option(False, "-i")):
    """Query the knowledge base."""
    typer.echo("wiki query - not yet implemented")


@app.command()
def lint(fix: bool = False, deep: bool = False):
    """Run health checks on the wiki."""
    typer.echo("wiki lint - not yet implemented")


@app.command()
def publish(preview: bool = False):
    """Build and publish the wiki with Quartz."""
    typer.echo("wiki publish - not yet implemented")


if __name__ == "__main__":
    app()
