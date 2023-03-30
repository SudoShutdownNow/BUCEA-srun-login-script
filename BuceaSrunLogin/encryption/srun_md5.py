import hmac
import hashlib


def get_md5(password, token):
    return hmac.new(token.encode(), password.encode(), hashlib.md5).hexdigest()


if __name__ == '__main__':
    password = ""
    token = "a1c4b41f574fd2d9dedee5511741336a37c5ae1f062738493bd4a6ca9ccd5533"
    print(get_md5(password, token))
