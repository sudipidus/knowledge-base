from pathlib import Path

import typer

app = typer.Typer(
    name="wiki",
    help="Personal LLM-powered knowledge base CLI",
    no_args_is_help=True,
)


@app.command()
def init(
    path: str = typer.Argument(".", help="Path to initialize the knowledge base"),
):
    """Initialize a new knowledge base."""
    from wiki_cli.commands.init_cmd import run_init
    run_init(Path(path))


@app.command()
def ingest(
    source: str = typer.Argument(None, help="File path or URL to ingest"),
    inbox: bool = typer.Option(False, help="Process all files in the inbox"),
    ref: bool = typer.Option(False, help="Save as reference only"),
    description: str = typer.Option("", help="Description for reference entries"),
):
    """Ingest a source into the knowledge base."""
    from wiki_cli.commands.ingest import IngestPipeline
    from wiki_cli.config import load_config
    from wiki_cli.wiki_manager import WikiManager

    config = load_config(Path("wiki.yaml"))
    vault_path = config.vault_path

    # Build provider from config
    if config.provider == "ollama":
        from wiki_cli.providers.ollama import OllamaProvider
        provider = OllamaProvider(**config.provider_config)
    elif config.provider == "claude":
        from wiki_cli.providers.claude import ClaudeProvider
        provider = ClaudeProvider(**config.provider_config)
    elif config.provider == "openai":
        from wiki_cli.providers.openai_provider import OpenAIProvider
        provider = OpenAIProvider(**config.provider_config)
    else:
        typer.echo(f"Unknown provider: {config.provider}")
        raise typer.Exit(1)

    wiki_mgr = WikiManager(vault_path)
    pipeline = IngestPipeline(wiki_mgr, provider, vault_path)

    if inbox:
        results = pipeline.run_inbox()
        for r in results:
            if r.success:
                typer.echo(f"Ingested: {r.title} ({r.pages_created} created, {r.pages_updated} updated)")
            else:
                typer.echo(f"Failed: {r.error}")
    elif ref:
        if not source:
            typer.echo("Error: URL required for reference mode")
            raise typer.Exit(1)
        result = pipeline.run_reference(source, description or source)
        if result.success:
            typer.echo(f"Reference saved: {result.title}")
        else:
            typer.echo(f"Failed: {result.error}")
    else:
        if not source:
            typer.echo("Error: source argument required (or use --inbox)")
            raise typer.Exit(1)
        result = pipeline.run(source)
        if result.success:
            typer.echo(f"Ingested: {result.title} ({result.pages_created} created, {result.pages_updated} updated)")
        else:
            typer.echo(f"Failed: {result.error}")


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
