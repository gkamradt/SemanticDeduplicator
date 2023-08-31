"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Semantic Deduplicator."""


if __name__ == "__main__":
    main(prog_name="semantic-deduplicator")  # pragma: no cover
