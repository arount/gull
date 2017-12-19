
import parse
import dateutil.parser
from jinja2 import Environment
from markdown2 import markdown

from gull.gullreader import GullReader
from gull.attachment import Attachment
from gull.loader import DictLoader


class Entity(object):
    '''
    An entity is basicaly a commit message and metadata.
    In Gull, it's a page or blog article.
    '''

    _commit_format = '''commit {commit_id}
Author: {author}
Date:   {date}

{description}'''


    def __init__(self, raw_commit_str):
        '''
        Initialize almost all meta data possible.
        What is defined as "not possible" is URLs, paths and html output
        of the entity because it needs access to `GullReader.config` instance.

        To avoid conflicts, these last meta data are computed within context:
            entity = Entity(raw_commit_string)
            with entity(config):
                print(entity.paths)

            raw_commit_str    Raw commit string (meta + description)
        '''

        self.raw = raw_commit_str
        values = parse.parse(self._commit_format, self.raw).__dict__['named']

        self.id = values['commit_id']
        self.commit_id = values['commit_id']

        # Clean description from whitespaces
        description = []
        for line in values['description'].splitlines():
            description.append(line[4:])
        self.description = '\n'.join(description)

        # Compute datetime
        self.raw_data = values['date']
        self.datetime = dateutil.parser.parse(values['date'])

        self.author = values['author']
        self.author_name = ' '.join(values['author'].split(' ')[:-1])
        self.author_email = values['author'].split(' ')[-1][1:-1]

        greader = GullReader.get_instance()
        # Compute commited files
        # At this point files are not attachment, only list of filenames
        self.files = greader.listfiles(commit=self.id)

        self.branch = greader.getbranch(self.id)
        self.section = self.branch.split('/')[0]

        self.shorten = greader.shorten(self.id)
        self.slug = '/'.join(self.branch.split('/')[1:])


    def __enter__(self):
        return self


    def __call__(self, config):
        '''
        Compute URLs and paths + HTML content.
        '''
        # compute urls according to config
        self.urls = []
        for url in config['urls']['entities']:
            self.urls.append(url.format(**self.__dict__))

        # same for attachments
        self.attachments = {}
        for filename in self.files:
            self.attachments[filename] = Attachment(
                filename,
                self
            )

        # jinja computed raw description
        self.text = None
        loader = DictLoader({"base": self.description})
        env = Environment(loader=loader)
        text = env.get_template('base').render(
            urls=config['urls'],
            site=config['website'],
            this=self.__dict__
        )
        self.content = text
        # text to html
        self.html = markdown(text)
        return self


    def __exit__(self, exception_type, exception_value, traceback):
        '''
        Negate __enter__.
        '''
        self.urls = None
        self.attachments = None
        self.text = None
        self.html = None


    @classmethod
    def from_commit_id(cls, commit_id):
        '''
        Kind of factory from commit hash instead of whole commit
        '''
        greader = GullReader.get_instance()
        return cls(greader.getcommit(commit_id))


