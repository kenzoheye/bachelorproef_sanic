from __future__ import absolute_import
from sanic.log import logger


def format_error(args, domain=None, detail=None, code=None):

   error = {}
   error.update({"domain": domain})

   if isinstance(args, tuple) and args:
       logger.warning(str(args))
       error.update({"msg": str(args)})
   elif isinstance(args, dict) and args:
       error.update({"msg": args})
   elif isinstance(args, str) and args:
       error.update({"msg": args})
   else:
       error.update({"msg": str(args)})

   if detail is not None:
       error.update({"detail": detail})
   else:
       error.update({"detail": None})

   if args and hasattr(args, "code"):
       error.update({"code": args.code})
   elif code is not None:
       error.update({"code": code})
   else:
       error.update({"code": 400})

   return error


class EmptyValueException(Exception):
   def __init__(self):
       super().__init__()


class DuplicateEntryError(Exception):
   def __init__(self, msg):
       # Call the base class constructor with the parameters it needs
       super().__init__(msg)
       # Now for your custom code...
       # self.response = response
       self.code = 409
       self.msg = msg


class FormattedException(Exception):
   def __init__(self, msg, domain=None, detail=None, code=None):
       # Call the base class constructor with the parameters it needs
       if hasattr(msg, "args"):

           msg = msg.args

       if isinstance(msg, tuple) and msg:

           msg = msg[0]

       super().__init__(msg)
       # Now for your custom code...
       self.domain = domain
       self.detail = detail
       self.code = code

       self.formatted = format_error(msg, domain=domain, detail=detail, code=code)