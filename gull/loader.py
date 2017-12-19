import jinja2

class DictLoader(jinja2.loaders.BaseLoader):

    def __init__(self, envdict):
        self._envdict = envdict

    def get_source(self, environment, template):
        try:
            return (self._envdict[template], template, lambda: True)
        except KeyError:
            raise jinja2.TemplateNotFound(template)

    def list_templates(self):
        return self._envdict.keys()


class AttachmentsLoader(jinja2.loaders.BaseLoader):

    def __init__(self, attachments_dict):
        self._attachments = attachments_dict

    def get_source(self, environment, templatename):
        try:
            return (
                self._attachments[templatename].read(),
                templatename,
                lambda: True
            )
        except KeyError:
            raise jinja2.TemplateNotFound(templatename)

