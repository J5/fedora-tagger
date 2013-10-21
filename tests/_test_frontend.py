""" Selenium tests.

Disabled for now.

"""

import rube.core

import time
import os
import signal
import subprocess
import sys
import random

from nose.tools import eq_
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from fedoratagger.lib import model

db_filename = "/var/tmp/tagger-tests.db"
db_url = "sqlite:///" + db_filename
port = random.randint(5000, 50000)
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
    time.sleep(1)


def tearDown():
    global _server
    os.kill(_server.pid, signal.SIGTERM)
    rube.core.tearDown()


class _Base(rube.core.RubeTest):
    realm = "FAS"


class TestFrontend(_Base):
    base = "http://localhost:%i" % port
    logout_url = base + "/logout"
    title = "lol Fedora Tagger lolol"

    def setUp(self):
        # Logout out of tagger
        super(TestFrontend, self).setUp()
        # ALSO try logging out of openid, just for laughs.
        try:
            self.driver.get("https://id.fedoraproject.org/logout")
        except Exception:
            pass

    def tearDown(self):
        # Logout out of tagger
        super(TestFrontend, self).tearDown()
        # ALSO log out of openid
        try:
            self.driver.get("https://id.fedoraproject.org/logout")
        except Exception:
            pass

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

    def assert_gritter(self, value):
        elem = self.driver.find_element_by_css_selector(".gritter-item p")
        eq_(elem.text, value)
        elem = self.driver.find_element_by_css_selector('.gritter-item')
        hover = ActionChains(self.driver).move_to_element(elem)
        hover.perform()
        elem = self.driver.find_element_by_css_selector('.gritter-close')
        elem.click()

    def test_add_tag_and_change_vote(self):
        self.test_login()
        elem = self.driver.find_element_by_css_selector(".center div.plus")
        elem.click()
        elem = self.driver.find_element_by_css_selector("#add_box")
        elem.send_keys("q")
        elem.send_keys(Keys.RETURN)
        self.assert_gritter('Tag "q" added to the package "mattd"')

        self.driver.get(self.base + "/mattd")

        elem = self.driver.find_element_by_css_selector(".center .down")
        elem.click()
        self.assert_gritter('Vote changed on the tag "q" of the package "mattd"')
        time.sleep(1)  # Sorry, @lmacken
        elem.click()
        self.assert_gritter(
            'Your vote on the tag "q" for the package "mattd" did not change'
        )
