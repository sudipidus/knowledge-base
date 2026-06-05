from pathlib import Path

import typer

app = typer.Typer(
    name="wiki",
    help="Personal LLM-powered knowledge base CLI",
    no_args_is_help=True,
)


def _load_deps():
    """Load config, provider, and wiki manager."""
    from wiki_cli.config import load_config
    from wiki_cli.providers import get_provider
    from wiki_cli.wiki_manager import WikiManager

    config = load_config(Path("wiki.yaml"))
    provider = get_provider(config.provider, config.provider_config)
    wiki_mgr = WikiManager(config.vault_path)
    return config, provider, wiki_mgr


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

    config, provider, wiki_mgr = _load_deps()
    pipeline = IngestPipeline(wiki_mgr, provider, config.vault_path)

    if inbox:
        results = pipeline.run_inbox()
        succeeded = sum(1 for r in results if r.success)
        failed = sum(1 for r in results if not r.success)
        typer.echo(f"Inbox: {succeeded} succeeded, {failed} failed")
        for r in results:
            if not r.success:
                typer.echo(f"  FAILED: {r.error}", err=True)
    elif ref:
        if not source:
            typer.echo("Error: source URL required with --ref", err=True)
            raise typer.Exit(1)
        result = pipeline.run_reference(source, description or source)
        typer.echo(f"Reference saved: {result.title}" if result.success else f"Error: {result.error}")
    else:
        if not source:
            typer.echo("Error: provide a source or use --inbox", err=True)
            raise typer.Exit(1)
        result = pipeline.run(source)
        if result.success:
            typer.echo(f'Ingested: "{result.title}" (+{result.pages_created}, ~{result.pages_updated} updated)')
        else:
            typer.echo(f"Error: {result.error}", err=True)


@app.command()
def reingest(
    source: str = typer.Argument(..., help="URL or file path to re-ingest"),
):
    """Re-fetch and update a previously ingested source."""
    from wiki_cli.commands.reingest import ReingestPipeline

    config, provider, wiki_mgr = _load_deps()
    pipeline = ReingestPipeline(wiki_mgr, provider, config.vault_path)
    result = pipeline.run(source)

    if result.success:
        if result.title == "(unchanged)":
            typer.echo("No changes detected. Skipping.")
        else:
            typer.echo(f'Re-ingested: "{result.title}" (+{result.pages_created}, ~{result.pages_updated} updated)')
    else:
        typer.echo(f"Error: {result.error}", err=True)


@app.command()
def query(
    question: str = typer.Argument(None, help="Question to ask the knowledge base"),
    save: bool = typer.Option(False, "--save", help="Save the answer as an exploration page"),
    interactive: bool = typer.Option(False, "-i", help="Interactive mode"),
):
    """Query the knowledge base."""
    from wiki_cli.commands.query import QueryEngine

    _, provider, wiki_mgr = _load_deps()
    engine = QueryEngine(wiki_mgr, provider)

    if interactive:
        typer.echo("Interactive mode. /save to save last answer, /quit to exit.")
        last_answer = ""
        while True:
            q = typer.prompt("wiki")
            if q == "/quit":
                break
            if q == "/save" and last_answer:
                engine._save_exploration("interactive-query", last_answer)
                typer.echo("Saved.")
                continue
            last_answer = engine.ask(q)
            typer.echo(f"\n{last_answer}\n")
    else:
        if not question:
            typer.echo("Error: provide a question or use -i", err=True)
            raise typer.Exit(1)
        answer = engine.ask(question, save=save)
        typer.echo(answer)
        if save:
            typer.echo("\n(Saved to explorations)")


@app.command()
def lint(
    fix: bool = typer.Option(False, "--fix", help="Auto-fix repairable issues"),
    deep: bool = typer.Option(False, "--deep", help="LLM-powered deep analysis"),
):
    """Run health checks on the wiki."""
    from wiki_cli.commands.lint import WikiLinter
    from wiki_cli.config import load_config
    from wiki_cli.wiki_manager import WikiManager

    config = load_config(Path("wiki.yaml"))
    wiki_mgr = WikiManager(config.vault_path)
    linter = WikiLinter(wiki_mgr)
    report = linter.run_all()

    total = report["total_issues"]
    pages = len(wiki_mgr.list_pages())
    typer.echo(f"Wiki Health Report\n==================\n{pages} pages scanned\n")

    if total == 0:
        typer.echo("All checks passed!")
    else:
        for check_name, issues in report["by_check"].items():
            sym = "x" if issues else "v"
            typer.echo(f"  [{sym}] {check_name}: {len(issues)}")
            for issue in issues[:5]:
                typer.echo(f"      - {issue['page']}: {issue['detail']}")
            if len(issues) > 5:
                typer.echo(f"      ... and {len(issues) - 5} more")

    typer.echo(f"\nTotal: {total} issues")


@app.command()
def publish(
    preview: bool = typer.Option(False, "--preview", help="Start local dev server"),
):
    """Build and publish the wiki with Quartz."""
    from wiki_cli.commands.publish import run_publish
    run_publish(preview=preview)


if __name__ == "__main__":
    app()
