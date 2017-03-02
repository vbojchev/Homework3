import os
import re
from string import letters

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class BaseHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

#def blog_key(name = 'default'):
#    return db.Key.from_path('blogs', name)

class BlogPost(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

    def render(self):
        self._render_text = self.content.replace('\n' , '<br>')
        return render_str('new_post.html', post=self)

class NewPost(BaseHandler):
    def render_front(self, subject="", content="", error="" ):
        blogs = db.GqlQuery=("SELECT * FROM BlogPost ORDER BY created DESC")
        self.render("new_post.html", subject=subject, content=content, error=error, blogs=blogs)

    def get(self):
        self.render_front()

    def post(self):
        content = self.request.get('content')
        subject = self.request.get('subject')
        params = dict(subject = subject, content = content)
        if not (content and subject):
            params['error']="Subject and content are mandatory"
            self.render('new_post.html', **params)
        else:
            p = BlogPost(subject = subject, content=content)
            p.put()
            self.redirect('/unit2/%s' % str(p.key().id()))

class BlogFront(BaseHandler):
    def get(self):
        blogs = db.GqlQuery=("select * from BlogPost")
        self.render('front.html', blogs = blogs)

class PostPage(BaseHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id))
        post = db.get(key)

        self.render('permalink.html' , post=post)


app = webapp2.WSGIApplication([('/unit2/newpost', NewPost),
                               ('/unit2/?', BlogFront),
                               ('/unit2/([0-9]+)', PostPage)],
                              debug=True)
