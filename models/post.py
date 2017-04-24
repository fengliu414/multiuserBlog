from google.appengine.ext import db
# from reply import ReplyPost
import utils
from user import User


class SecurePost(db.Model):
    post_owner = db.ReferenceProperty(User, collection_name='posts')
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    # user_name = db.StringProperty(required=True)
    # likes = db.IntegerProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    # last_modified = db.DateTimeProperty(auto_now=True)
    liked_user = db.StringListProperty()
    unliked_user = db.StringListProperty()

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        replyposts = self.comments

        if not replyposts:
            return utils.render_str("post.html", p=self, likes=self.likes)
        else:
            return utils.render_str("post.html", p=self, r=replyposts,
                                    likes=self.likes)

    @property
    def likes(self):
        return len(self.liked_user) - len(self.unliked_user)
