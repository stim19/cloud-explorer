from flask_login import UserMixin
USERS = {
	"a": {"password":"a"}
}

class User(UserMixin):

	def __init__(self, username):
		self.id = username

	@staticmethod
	def validate(username, password):
		user = USERS.get(username)
		if user and user['password']==password:
			return User(username)
		return None
