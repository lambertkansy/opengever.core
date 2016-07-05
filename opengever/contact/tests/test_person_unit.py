from ftw.builder import Builder
from ftw.builder import create
from opengever.contact.models import Contact
from opengever.testing import MEMORY_DB_LAYER
import unittest2


class TestPerson(unittest2.TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestPerson, self).setUp()
        self.session = self.layer.session

    def test_adding(self):
        person = create(Builder('person')
                       .having(firstname=u'Peter', lastname=u'M\xfcller'))

    def test_is_contact(self):
        person = create(Builder('person')
                       .having(firstname=u'Peter', lastname=u'M\xfcller'))

        self.assertTrue(isinstance(person, Contact))
        self.assertEquals('person', person.contact_type)

    def test_person_can_have_multiple_addresses(self):
        peter = create(Builder('person')
                       .having(firstname=u'Peter', lastname=u'M\xfcller'))

        address1 = create(Builder('address')
                          .for_contact(peter)
                          .labeled(u'Work')
                          .having(street=u'Dammweg 9', zip_code=u'3013',
                                  city=u'Bern'))

        address2 = create(Builder('address')
                          .for_contact(peter)
                          .labeled(u'Home')
                          .having(street=u'Musterstrasse 283',
                                  zip_code=u'1700',
                                  city=u'Fribourg'))

        self.assertEquals([address1, address2], peter.addresses)

    def test_person_can_have_multiple_mail_addresses(self):
        peter = create(Builder('person')
                       .having(firstname=u'Peter', lastname=u'M\xfcller'))

        home = create(Builder('mailaddress')
                      .for_contact(peter)
                      .labeled(u'Home')
                      .having(address=u'peter@example.com'))

        work = create(Builder('mailaddress')
                      .for_contact(peter)
                      .labeled(u'Work')
                      .having(address=u'm.peter@example.com'))

        self.assertEquals([home, work], peter.mail_addresses)
        self.assertEquals([u'peter@example.com', u'm.peter@example.com'],
                          [mail.address for mail in peter.mail_addresses])

    def test_person_can_have_multiple_phonenumbers(self):
        peter = create(Builder('person')
                       .having(firstname=u'Peter', lastname=u'M\xfcller'))

        home = create(Builder('phonenumber')
                      .for_contact(peter)
                      .labeled(u'Home')
                      .having(phone_number=u'+41791234566'))

        work = create(Builder('phonenumber')
                      .for_contact(peter)
                      .labeled(u'Work')
                      .having(phone_number=u'0315110000'))

        self.assertEquals([home, work], peter.phonenumbers)
        self.assertEquals([u'+41791234566', u'0315110000'],
                          [phone.phone_number for phone in peter.phonenumbers])

    def test_fullname_is_firstname_and_lastname_separated_with_a_space(self):
        peter = create(Builder('person')
                       .having(firstname=u'Peter', lastname=u'M\xfcller'))

        self.assertEquals(u'Peter M\xfcller', peter.fullname)

    def test_title_is_fullname(self):
        peter = create(Builder('person')
                       .having(firstname=u'Peter', lastname=u'M\xfcller'))
        self.assertEquals(u'Peter M\xfcller', peter.get_title())