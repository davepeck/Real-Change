import os
import sys
import webapp2
import jinja2


# Set up jinja templating
template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), './templates'))
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader([template_path], encoding='utf-8'))


# Base handler for all urls
class RealChangeHandler(webapp2.RequestHandler):
    """
    Base class for all handlers in this application.
    Put extremely common functionality here.
    """
    def _breakpoint(self):
        # App-Engine friendly BREAKPOINT
        import pdb
        p = pdb.Pdb(None, sys.__stdin__, sys.__stdout__)
        p.set_trace()

    def _get_template(self, template_name):
        return jinja_env.get_template(template_name)

    def _render_template(self, template, **kwargs):
        return template.render(**kwargs)

    def respond(self, template_name, params, content_type="text/html", status=200):
        template = self._get_template(template_name)
        rendered_template = self._render_template(template, **params)
        self.response.status_int = status
        self.response.headers['Content-Type'] = content_type
        self.response.write(rendered_template)



class HomeHandler(RealChangeHandler):
    def get(self):
        return self.respond('home.dhtml', {})

