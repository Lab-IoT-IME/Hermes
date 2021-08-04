from app.mod_user.models import User, UserSchema

def getUserByEmail(email):
  try:
    userSchema = UserSchema()
    user = User.query.filter_by(email=email).one()
    userJson = userSchema.dump(user)
    del userJson['password']
    return (user, userJson)
  except:
    return None