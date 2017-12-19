#!/usr/env/bin python

import shutil
import jinja2.exceptions
import os

from gull.gullreader import GullReader
from gull.entity import Entity

class Writer(object):

    def __init__(self):
        self.config = GullReader.get_instance().config
        self.basepath = self.config['filesystem']['base']


    def mkdirs(self):
        try:
            shutil.rmtree(self.basepath)
        except OSError:
            pass

        fsconfig = self.config['filesystem']

        os.makedirs(os.path.join(
            self.basepath,
            self.config['filesystem']['blog']
        ))
        for path in [fsconfig['blog'], fsconfig['medias'], fsconfig['assets']]:
            try:
                os.makedirs(os.path.join(
                    self.basepath,
                    path
                ))
            except FileExistsError:
                pass




    def write(self):
        self.mkdirs()
        self.write_assets()

        greader = GullReader.get_instance()
        for item in greader.articles:
            entity = Entity(greader.getcommit(item))
            self.write_item(entity)


    def write_assets(self):
        assets_path = os.path.join(
            self.basepath,
            self.config['filesystem']['assets']
        )

        greader = GullReader.get_instance()
        templates = greader.template.list_templates()
        for templatename in templates:
            if templatename.startswith(self.config['filesystem']['assets']):
                template = greader.template.get_template(templatename)
                # XXX Surelly buggy
                path = os.path.join(
                    self.basepath,
                    templatename
                )
                self.write_file(path, template.render())


    def write_item(self, item, section=None):
        if section is None:
            if item.section[-1] == 's':
                section = item.section[0:-1]
            else:
                section = item.section

        template_name = '{}.html'.format(section)
        greader = GullReader.get_instance()
        try:
            renderer = greader.template.get_template(template_name)
        except jinja2.exceptions.TemplateNotFound:
            renderer = self._gullreader.template.get_template(
                greader.config['default_template']
            )

        with item(greader.config):
            self.write_attachments(item.attachments)

            for path in item.urls:
                path = os.path.join(
                    self.basepath,
                    self.config['filesystem']['blog'],
                    path
                )

                itemdict = {
                    'item': item.__dict__,
                    'urls': self.config['filesystem'],
                    'site': self.config['website']
                }
                html = self.render(itemdict, section, renderer)
                self.write_file(path, html)


    def write_attachments(self, attachments):
        for attachment in attachments.values():
            for path in attachment.paths:
                try:
                    os.makedirs(os.path.dirname(path))
                except FileExistsError:
                    pass

                attachment.copyfile(path)


    def write_file(self, filepath, content):
        try:
            os.makedirs(os.path.dirname(filepath))
        except FileExistsError:
            pass

        with open(filepath, 'w') as fh:
            fh.write(content)
            fh.close()



    def render(self, item, section, renderer):
        return renderer.render(**item)

