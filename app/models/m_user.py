class User(object):

    role = None
    caller = None
    system_token = None
    email = None
    description = "no description"

    def __init__(
        self,
        role,
        system_token=None,
        email=None,
        description=None,
        caller=None,
        *args,
        **kwargs,
    ):
        self.role = role
        if system_token:
            self.system_token = system_token
        if email:
            self.email = email
        if description:
            self.description = description
        if caller:
            self.caller = caller

    def __repr__(self):
        if self.system_token or self.email:
            if self.system_token:
                if self.caller:
                    return f"<User [SYSTEM] {self.system_token[0:30]}... role: {self.role} caller: {self.caller} {self.description}>"
                else:
                    return f"<User [SYSTEM] {self.system_token[0:30]}... role: {self.role} {self.description}>"
            if self.email:
                if self.caller:
                    return f"<User [USER] {self.email} role: {self.role} caller: {self.caller} {self.description}>"
                else:
                    return f"<User [USER] {self.email} role: {self.role} {self.description}>"
        else:
            return f"<User {self.role}>"
