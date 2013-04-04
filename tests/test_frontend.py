import rube.core

import time
import os
import signal
import subprocess
import sys

from selenium.webdriver.common.keys import Keys

from fedoratagger.lib import model

db_filename = "/var/tmp/tagger-tests.db"
db_url = "sqlite:///" + db_filename
port = 33412
_server = None


def setUp():
    global _server

    if os.path.exists(db_filename):
        os.unlink(db_filename)

    session = model.create_tables(db_url, debug=True)
    package = model.Package(id=1, name="mattd", summary="Matt Daemon")
    session.add(package)
    session.commit()

    cmd = "%s tests/_testserver.py %i %s" % (
        sys.executable,
        port,
        db_url
    )
    _server = subprocess.Popen(cmd, shell=True)
    # Let it get setup
    time.sleep(2)


def tearDown():
    global _server
    os.kill(_server.pid, signal.SIGTERM)
    rube.core.tearDown()


class _Base(rube.core.RubeTest):
    realm = "FAS"


class TestFrontend(_Base):
    base = "http://localhost:%i/app" % port
    title = "lol Fedora Tagger lolol"

    # Not tolerant
    def test_login(self):
        self.driver.get(self.base)
        elem = self.driver.find_element_by_css_selector("#login_form > input")
        elem.click()

        self.wait_for("asking to authenticate")  # the openid page

        elem = self.driver.find_element_by_name("username")
        elem.send_keys(self.auth[0])
        elem = self.driver.find_element_by_name("password")
        elem.send_keys(self.auth[1])
        elem.send_keys(Keys.RETURN)

        self.wait_for("Review the authorization details")

        elem = self.driver.find_element_by_name("decided_allow")
        elem.click()

        self.wait_for(str(port))

        elem = self.driver.find_element_by_css_selector("input:last-child")
        elem.click()

        # You can only see this text if you have successfully authenticated
        self.wait_for("Add a new tag")
