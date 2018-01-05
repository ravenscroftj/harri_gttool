import click
import ujson

from flask import current_app
from .services.news import import_news_json

def register_cli_functions(app):

    @app.cli.command()
    @click.argument("jsonfile", type=click.File(mode='r'))
    def import_articles(jsonfile):
        """Import articles into database"""

        click.echo('Importing articles from JSON')

        for i, line in enumerate(jsonfile):
            try:
                article = ujson.loads(line)

                print("Import article #{idx} {title}"
                      .format(idx=i, **article['_source']))

                import_news_json(article['_source'])

            except ValueError as e:
                print("Could not parse article on line {}".format(i+1))
