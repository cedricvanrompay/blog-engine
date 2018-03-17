import re
from types import SimpleNamespace
import unicodedata
import os

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

def render_article(title, body):
    env = Environment(
        loader=FileSystemLoader('templates'),
    )
    template = env.get_template('article.html')
    return template.render(title=title, body=body)

def render_index(article_list):
    # XXX environment could be created once
    env = Environment(
        loader=FileSystemLoader('templates'),
    )
    template = env.get_template('index.html')
    article_list.sort(key = lambda x:x.pub_date, reverse=True)
    return template.render(article_list=article_list)

# from https://stackoverflow.com/a/517974/3025740
def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def slugify(x):
    xx = re.sub('\W', '-', x)
    xxx = remove_accents(xx)
    return xxx.lower()

def build_page(path_to_source):
    with open(path_to_source) as f:
        source = f.read()

    article = extract_article_data(source)
    body = render_markdown(article.text)
    page = render_article(article.title, body)
    if "slug" in article.metadata:
        slug = article.metadata["slug"]
    else:
        slug = slugify(article.title)
    article.filename = str(article.pub_date) + '-' + slug + '.html'
    article.href = article.filename

    return (page, article)

def remove_all_html_files(path_to_dir):
    for name in os.listdir(path_to_dir):
        if name.endswith('.html'):
            os.remove(path_to_dir+'/'+name)
            

def build_blog(path_to_sources, path_to_destination):
    if not os.path.isdir(path_to_sources):
        raise Exception('not a directory: "%s"' % path_to_sources)
    
    remove_all_html_files(path_to_destination)

    article_list = list()
    for source_file in os.listdir(path_to_sources):
        page, article = build_page(path_to_sources+'/'+source_file)
        article_list.append(article)
        with open(path_to_destination+'/'+article.filename, 'w') as f:
            f.write(page)

    index = render_index(article_list)
    with open(path_to_destination+'/'+'index.html', 'w') as f:
        f.write(index)
