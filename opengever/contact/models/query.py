from opengever.contact.models import Contact
from opengever.contact.models import Organization
from opengever.contact.models import OrgRole
from opengever.contact.models import Person
from opengever.ogds.models.query import BaseQuery
from opengever.ogds.models.query import extend_query_with_textfilter
from sqlalchemy.orm import contains_eager


class ContactQuery(BaseQuery):

    def polymorphic_by_searchable_text(self, text_filters=[]):
        """Query all Contacts by searchable text.

        If the function of a Persons OrgRole matches, only the matching
        OrgRoles will be returned.

        """
        # we need to join manually instead of using `options.joinedload` to be
        # able to filter by OrgRole.function below.
        query = self.outerjoin(Person.organizations)
        query = query.options(contains_eager(Person.organizations))
        return extend_query_with_textfilter(
            query,
            [Person.firstname, Person.lastname, Organization.name,
             OrgRole.function],
            text_filters,
        )

Contact.query_cls = ContactQuery