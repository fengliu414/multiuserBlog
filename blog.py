import utils
import webapp2
from models.reply import ReplyPost
from models.post import SecurePost
from models.user import User
from google.appengine.ext import db


# wrapper function for checking post exists
def post_exists(func):
    def wrapper(self, post_id):
        key = db.Key.from_path('SecurePost', int(post_id),
                               parent=utils.blog_key())
        post = db.get(key)
        if post:
            return func(self, post_id, post)
        else:
            self.error(404)
            return
    return wrapper


# wrapper function for checking login
def login_required(func):
    """
    A decorator to confirm a user is logged in or redirect as needed.
    """
    def login(self, *args, **kwargs):
        # Redirect to login if user not logged in, else execute func.
        if not self.user:
            self.redirect("/login")
        else:
            func(self, *args, **kwargs)
    return login


# base handler function
class Handler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def render_str(self, template, **params):
        return utils.render_str(template, **params)

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def set_secure_cookie(self, name, val):
        cookie_val = utils.make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and utils.check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))


# main page handler
class MainPage(Handler):
    def get(self):
        self.render("mainpage.html")


# user signup page base handler
class Signup(Handler):
    def get(self):
        self.render("signup-form.html")

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username=self.username,
                      email=self.email)

        if not utils.valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not utils.valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not utils.valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError


# user registration handler that inherits Signup handler
class Register(Signup):
    def done(self):
        # make sure the user does not exist
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username=msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('welcome')


# welcome page handler after user user successfully signed up
class Welcome(Handler):
    def get(self):
        if self.user:
            self.render('welcome.html', username=self.user.name)
        else:
            self.redirect('/signup')


# main page handler that displays all the posts and comments
class BlogFront(Handler):
    @login_required
    def get(self):
        # db.delete(db.Query(keys_only=True)) //clear whole database
        posts = SecurePost.all().order('-created')
        self.render('front.html', posts=posts)


# reply handler when the reply button is pressed
class ReplyHandler(Handler):
    @login_required
    @post_exists
    def get(self, post_id, post):
        reply_content = self.request.get('content')
        if reply_content:
            rp = ReplyPost(posts=post, reply=reply_content,
                           reply_user_name=self.user.name)
            rp.put()
        self.redirect('/blog/?')


# like handler when user liked one post
class LikeHandler(Handler):
    @login_required
    def likes_update(self, post):
        post.liked_user.append(str(self.user.key().id()))
        post.put()

    @login_required
    @post_exists
    def get(self, post_id, post):
        post_owner = post.post_owner
        replyposts = post.comments
        if self.user.name == post_owner.name:
            self.write("You can't like your own comment")
        else:
            if str(self.user.key().id()) not in post.liked_user:
                self.render("post.html", p=post,
                            r=replyposts, likes=post.likes+1)
                self.likes_update(post)
            self.redirect('/blog/?')


# unlike handler when user disliked one post
class UnLikeHandler(LikeHandler):
    @login_required
    def likes_update(self, post):
        post.unliked_user.append(self.user.name)
        post.put()


# handler for editing the comments
class EditReplyHandler(Handler):
    @login_required
    def get(self, post_id):
        rp = utils.check_comment_exists(self, post_id)
        if not rp:
            return
        if self.user.name == rp.reply_user_name:
            p = rp.posts
            self.render('reply.html', p=p, reply=rp.reply)
        else:
            self.write("You can only edit your own comment")

    @login_required
    def post(self, post_id):

        rp = utils.check_comment_exists(self, post_id)
        if not rp:
            return
        if self.user.name == rp.reply_user_name:
            if self.request.get('button_name') == "delete":
                rp.delete()
                self.redirect('/blog/?')

            elif self.request.get('button_name') == "cancel":
                self.redirect('/blog/?')

            else:
                rp.reply = self.request.get('content')
                rp.put()
                self.redirect('/blog/?')
        else:
            self.write("You can only edit your own comment")


# handler for creating new post
class NewPost(Handler):

    @login_required
    def get(self):
        self.render("newpost.html")

    @login_required
    def post(self):
        # decide which button in the form is clicked
        if self.request.get('button_name') == "delete":
            self.redirect('/blog/?')
        elif self.request.get('button_name') == "cancel":
            self.redirect('/blog/?')
        else:
            subject = self.request.get('subject')
            content = self.request.get('content')
            if subject and content:
                p = SecurePost(parent=utils.blog_key(),
                               post_owner=self.user, subject=subject,
                               content=content)
                p.put()
                self.redirect('/blog/')
            else:
                error = "Please enter subject and content!"
                self.render('newpost.html', subject=subject, content=content,
                            error=error)


# handler for individual posts that supports modification
class PostPage(Handler):
    @login_required
    @post_exists
    def get(self, post_id, post):
        if self.user.key().id() == post.post_owner.key().id():
            self.render('newpost.html', subject=post.subject,
                        content=post.content)
        else:
            self.write("You can only edit your own content!")

    @login_required
    @post_exists
    def post(self, post_id, post):
        # decide which button in the form is clicked
        if self.request.get('button_name') == "delete":
            if self.user.key().id() == post.post_owner.key().id():
                # get all the reply based from a post
                replyposts = post.comments
                for rp in replyposts:
                    rp.delete()
                post.delete()
            self.redirect('/blog/?')
        elif self.request.get('button_name') == "cancel":
            self.redirect('/blog/?')
        else:
            subject = self.request.get('subject')
            content = self.request.get('content')
            if subject and content:
                if self.user.key().id() == post.post_owner.key().id():
                    post.subject = subject
                    post.content = content
                else:
                    self.write('You can only edit your own post!')
                    return
                post.put()
                self.redirect('/blog/')
            else:
                error = "Please enter subject and content!"
                self.render('newpost.html', subject=subject, content=content,
                            error=error)


# login handler
class Login(Handler):
    def get(self):
        self.render('login-form.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/blog/?')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error=msg)


# logout handler
class Logout(Handler):
    def get(self):
        self.logout()
        self.redirect('/')


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/blog/?', BlogFront),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/newpost', NewPost),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/welcome', Welcome),
                               ('/like/([0-9]+)', LikeHandler),
                               ('/unlike/([0-9]+)', UnLikeHandler),
                               ('/reply/([0-9]+)', ReplyHandler),
                               ('/edit_reply/([0-9]+)', EditReplyHandler),
                               ],
                              debug=True)
