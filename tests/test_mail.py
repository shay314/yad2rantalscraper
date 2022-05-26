
from yad2.yad2.spiders.email import Mail

def test_creation():
    Mail()


def test_load_config():
    m = Mail()
    username, password = m.load_config()