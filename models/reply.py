from google.appengine.ext import db
from post import SecurePost


# reply of the post whose parent is the post itself
class ReplyPost(db.Model):
    posts = db.ReferenceProperty(SecurePost, collection_name='comments')
    reply = db.TextProperty(required=True)
    reply_user_name = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    # @classmethod
    # def by_parentname(cls, value):
    #     u = ReplyPost.all()
    #     return u

    def render(self):
        self._render_text = self.reply.replace('\n', '<br>')
        return self
