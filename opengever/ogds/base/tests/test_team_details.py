from opengever.testing import IntegrationTestCase
from ftw.testbrowser import browsing


class TestTeamDetails(IntegrationTestCase):

    @browsing
    def test_title(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(self.portal, view='team-details/1')

        self.assertEquals(
            [u'Projekt \xdcberbaung Dorfmatte'], browser.css('h1').text)

    @browsing
    def test_raises_not_found_with_invalid_id(self, browser):
        self.login(self.administrator, browser=browser)

        with browser.expect_http_error(code=404):
            browser.open(self.portal, view='team-details/123')

    @browsing
    def test_metadata_table(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(self.portal, view='team-details/1')

        items = browser.css('.listing').first.lists()
        self.assertEquals(
            ['Assigned org unit', 'Finanzamt'], items[0])
        self.assertEquals(
            ['Group', 'Projekt A'], items[1])

    @browsing
    def test_list_and_link_team_members(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(self.portal, view='team-details/1')

        links = browser.css('.members a')
        self.assertEquals(
            [u'B\xe4rfuss K\xe4thi (kathi.barfuss)',
             'Ziegler Robert (robert.ziegler)'],
            links.text)

        self.assertEquals(
            ['http://nohost/plone/@@user-details/kathi.barfuss',
             'http://nohost/plone/@@user-details/robert.ziegler'],
            [link.get('href') for link in links])
