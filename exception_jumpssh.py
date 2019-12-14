class Exceptions(Exception):
    pass

class socketerror(Exceptions):
    pass

class BadHostKeyException(Exceptions):
    pass

class AuthenticationFailed(Exceptions):
    pass

class SSHException(Exceptions):
    pass

class OtherError(Exceptions):
    pass

class SshError(Exceptions):
    pass

class HostUnkown(Exceptions):
    pass
