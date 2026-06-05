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
    from wiki_cli.commands.reingest import ReingestPipeline
    from wiki_cli.config import load_config
    from wiki_cli.wiki_manager import WikiManager

    config = load_config(Path("wiki.yaml"))
    vault_path = config.vault_path

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
    pipeline = ReingestPipeline(wiki_mgr, provider, vault_path)
    result = pipeline.run(source)

    if result.success:
        if result.title == "(unchanged)":
            typer.echo(f"Source unchanged, skipping: {source}")
        else:
            typer.echo(f"Reingested: {result.title} ({result.pages_created} created, {result.pages_updated} updated)")
    else:
        typer.echo(f"Failed: {result.error}")


@app.command()
def query(
    question: str = typer.Argument(None, help="Question to ask the knowledge base"),
    save: bool = typer.Option(False, "--save", help="Save the answer as an exploration page"),
    interactive: bool = typer.Option(False, "-i", help="Interactive mode: ask multiple questions"),
):
    """Query the knowledge base."""
    from wiki_cli.commands.query import QueryEngine
    from wiki_cli.config import load_config
    from wiki_cli.wiki_manager import WikiManager

    config = load_config(Path("wiki.yaml"))
    vault_path = config.vault_path

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
    engine = QueryEngine(wiki_mgr, provider)

    if interactive:
        typer.echo("Interactive query mode (type 'exit' to quit)")
        while True:
            q = input("\n> ")
            if q.strip().lower() in ("exit", "quit", "q"):
                break
            answer = engine.ask(q, save=save)
            typer.echo(f"\n{answer}")
    else:
        if not question:
            typer.echo("Error: question argument required (or use -i for interactive mode)")
            raise typer.Exit(1)
        answer = engine.ask(question, save=save)
        typer.echo(answer)


@app.command()
def lint(fix: bool = False, deep: bool = False):
    """Run health checks on the wiki."""
    from wiki_cli.commands.lint import WikiLinter
    from wiki_cli.config import load_config
    from wiki_cli.wiki_manager import WikiManager

    config = load_config(Path("wiki.yaml"))
    wiki_mgr = WikiManager(config.vault_path)
    linter = WikiLinter(wiki_mgr)
    report = linter.run_all()

    typer.echo(f"Wiki Lint Report: {report['total_issues']} issue(s) found\n")
    for check_name, issues in report["by_check"].items():
        typer.echo(f"  {check_name}: {len(issues)}")
        for issue in issues:
            typer.echo(f"    - [{issue['page']}] {issue['detail']}")


@app.command()
def publish(preview: bool = False):
    """Build and publish the wiki with Quartz."""
    from wiki_cli.commands.publish import run_publish
    run_publish(preview=preview)


if __name__ == "__main__":
    app()
