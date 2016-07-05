from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.base.default_values import get_persisted_value_for_field
from opengever.testing import FunctionalTestCase
from opengever.testing.patch import TempMonkeyPatch
from opengever.testing.types import IDummyAnnotationStorageBehavior
from opengever.testing.types import IDummyAttributeStorageBehavior
from opengever.testing.types import IDummySchema
import unittest


class TestZ3CFormFilledInDefaults(FunctionalTestCase):

    def add_object(self, browser):
        browser.login().open()
        factoriesmenu.add('Dummy')
        browser.click_on('Save')
        obj = browser.context
        return obj

    @unittest.skip(
        """Fails because the persisted value is equal to missing value, and
        therefore doesn't get used in the edit form, but gets replaced instead
        with the default value""")
    @browsing
    def test_ann_behavior_with_default_equal_missing_value(self, browser):
        field = IDummyAnnotationStorageBehavior['ann_behavior_int_field']
        assert field.missing_value is None

        with TempMonkeyPatch(field, 'default', None):
            obj = self.add_object(browser)
            initial_value = field.get(field.interface(obj))

            def mydefault():
                return 42

            with TempMonkeyPatch(field, 'defaultFactory', mydefault):
                browser.visit(obj, view='@@edit')
                form = browser.forms['form']
                self.assertEqual(
                    initial_value,
                    int(form.find(field.title).value),
                    'Value %r should have been prefilled' % initial_value)


class TestDVPersistenceBase(FunctionalTestCase):
    """Base class for testcases that default values are persisted on the
    object in all relevant combinations of methods of creation
    (createContentInContainer, invokeFactory, TTW via z3c.form add form) and
    storage (base schema + attribute storage, behavior + attribute storage,
    behavior + annotation storage).
    """

    def add_object(self, browser):
        """Create an object using the creation method under test.
        """
        raise NotImplementedError

    def assert_value_persisted(self, field, initial_default, new_default,
                               browser=None):
        """Create an object (by delegating to add_object() implemented by the
        specific testcase) and assert that a field's default value will
        actually be persisted on the object after creation.

        We do this by
        - first patching the field's defaultFactory to return a known value
        - creating the object using that default
        - modifiying the defaultFactory to return a different default
        - checking that the field value on the object didn't also change
        """
        # We're using the defaultFactory here to be able to distinguish
        # a default of `None` from "no default"
        with TempMonkeyPatch(field, 'defaultFactory', lambda: initial_default):
            obj = self.add_object(browser)
            initial_value = field.get(field.interface(obj))

            with TempMonkeyPatch(field, 'defaultFactory', lambda: new_default):
                current_value = field.get(field.interface(obj))

        self.assertEqual(
            initial_value, current_value,
            'Value %r should have been persisted, got %r instead' % (
                initial_value, current_value))

        # In addition to asserting initial_value == current_value, also check
        # persistence using our own helper function which should raise an
        # AttributeError if no value has been persisted.
        persisted_value = get_persisted_value_for_field(obj, field)
        self.assertEqual(persisted_value, current_value)


class TestDefaultValuePersistenceZ3CForm(TestDVPersistenceBase):

    def add_object(self, browser):
        browser.login().open()
        factoriesmenu.add('Dummy')
        browser.click_on('Save')
        obj = browser.context
        return obj

    @browsing
    def test_base_schema(self, browser):
        field = IDummySchema['int_field']

        self.assert_value_persisted(
            field, initial_default=11, new_default=42, browser=browser)

    @browsing
    def test_base_schema_with_default_equal_missing_value(self, browser):
        field = IDummySchema['int_field']
        assert field.missing_value is None

        self.assert_value_persisted(
            field, initial_default=None, new_default=42, browser=browser)

    @browsing
    def test_attr_behavior(self, browser):
        field = IDummyAttributeStorageBehavior['attr_behavior_int_field']

        self.assert_value_persisted(
            field, initial_default=11, new_default=42, browser=browser)

    @browsing
    def test_attr_behavior_with_default_equal_missing_value(self, browser):
        field = IDummyAttributeStorageBehavior['attr_behavior_int_field']
        assert field.missing_value is None

        self.assert_value_persisted(
            field,
            initial_default=None, new_default=42, browser=browser)

    @browsing
    def test_ann_behavior(self, browser):
        field = IDummyAnnotationStorageBehavior['ann_behavior_int_field']

        self.assert_value_persisted(
            field, initial_default=11, new_default=42, browser=browser)

    @browsing
    def test_ann_behavior_with_default_equal_missing_value(self, browser):
        field = IDummyAnnotationStorageBehavior['ann_behavior_int_field']
        assert field.missing_value is None

        self.assert_value_persisted(
            field, initial_default=None, new_default=42, browser=browser)