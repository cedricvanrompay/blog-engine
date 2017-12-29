import re
from types import SimpleNamespace
import unicodedata

import yaml
import markdown
import jinja2
from jinja2 import Environment, FileSystemLoader

PATH_TO_SOURCE = "/home/cedric/repos/blog"
PATH_TO_BUILD = "/home/cedric/repos/cedricvanrompay.github.io/blog"

# from https://github.com/waylan/docdata/blob/master/docdata/yamldata.py
METADATA_RE = re.compile(r'^-{3}[ \t]*\n(.*?\n)(?:\.{3}|-{3})[ \t]*\n', re.UNICODE|re.DOTALL)

Article = SimpleNamespace

def extract_article_data(source):
    raw_metadata = METADATA_RE.match(source)
    metadata = yaml.safe_load(raw_metadata.group(1))

    pub_date = metadata.pop('publication date')

    text = source[raw_metadata.end():].lstrip()

    title = re.match(r'^#{1}([^#].*)\n?',text).group(1).strip()

    return Article(title=title, pub_date=pub_date, text=text, metadata=metadata)

def render_markdown(text):
    return markdown.markdown(text)

def build_article(title, body):
    env = Environment(
        loader=FileSystemLoader('templates'),
    )
    template = env.get_template('article.html')
    return template.render(title=title, body=body)

# from https://stackoverflow.com/a/517974/3025740
def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def slugify(x):
    xx = re.sub('\W', '-', x)
    xxx = remove_accents(xx)
    return xxx.lower()

with open('data-for-test/article.md') as f:
    source = f.read()

article = extract_article_data(source)
body = render_markdown(article.text)
page = build_article(article.title, body)
slug = slugify(article.title)
