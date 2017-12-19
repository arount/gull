
from gull.gitreader import GitReader
from gull.loader import DictLoader
import gull.mime as mime

from jinja2 import Environment
import yaml
import os


class GullReader(GitReader):

    template = None
    config = None
    _meta_branches = {
        "config": "_gull/config",
        "template": "_gull/template"
    }
    _initialized = None


    def __init__(self, *args):
        super(GullReader, self).__init__(*args)

        config_commitid = self.lastcommit(self._meta_branches['config'])
        yaml_str = '\n'.join(self.getcommit(config_commitid).splitlines()[4:])
        self.config = yaml.load(yaml_str)

        template_commitid = self.lastcommit(self._meta_branches['template'])
        template_files = self.listfiles(template_commitid)
        envdict = {}
        for filename in template_files:
            path = os.path.join(self.repo.working_dir, filename)
            envdict[filename] = self.getfile(filename, template_commitid)

        loader = DictLoader(envdict)
        self.template = Environment(loader=loader)


    def getsection(self, section):
        branches = [p for p in self.branches if p.startswith('{}/'.format(section))]
        return [self.lastcommit(b)for b in branches]


    @property
    def pages(self):
        return self.getsection('pages')


    @property
    def articles(self):
        return self.getsection('articles')

