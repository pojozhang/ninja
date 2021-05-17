import unittest
import feishu
import configparser

cp = configparser.ConfigParser()
cp.read("config.ini")
config = cp['feishu']


class TestCase(unittest.TestCase):

    def testSendText(self):
        client = feishu.Client(config)
        client.send_text("""this
                        is
                        a
                        test
                        msg""")


if __name__ == '__main__':
    unittest.main()
