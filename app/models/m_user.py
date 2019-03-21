class User(object):

    role = None
    system_token = None
    email = None
    description = "no description"

    def __init__(
        self, role, system_token=None, email=None, description=None, *args, **kwargs
    ):
        self.role = role
        if system_token:
            self.system_token = system_token
        if email:
            self.email = email
        if description:
            self.description = description

    def __repr__(self):
        if self.system_token or self.email:
            if self.system_token:
                return f"<User [SYSTEM] {self.system_token[0:30]}... {self.role} {self.description}>"
            if self.email:
                return f"<User [USER] {self.email} {self.role} {self.description}>"
        else:
            return f"<User {self.role}>"
