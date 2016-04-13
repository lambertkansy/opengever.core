from DateTime import DateTime
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from ZPublisher.Iterators import IStreamIterator
from opengever.disposition.ech0160 import model
from opengever.disposition.ech0160.bindings import arelda
from pyxb.namespace import XMLSchema_instance as xsi
from pyxb.utils.domutils import BindingDOMSupport
from tempfile import TemporaryFile
from zipfile import ZIP_DEFLATED
from zipfile import ZipFile
from zope.component import queryMultiAdapter
from zope.interface import implements
import os.path

schemas_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'ech0160', 'schemas')


class ECH0160ExportView(BrowserView):

    def __call__(self):

        portal_state = queryMultiAdapter((self.context, self.request),
                                         name=u'plone_portal_state')

        sip_folder_name = 'SIP_{}_{}_{}'.format(
            DateTime().strftime('%Y%m%d'),
            portal_state.portal().getId().upper(),
            'MyRef',
        )

        BindingDOMSupport.SetDefaultNamespace(u'http://bar.admin.ch/arelda/v4')

        # Create metadata.xml document
        doc = arelda.paketSIP(schemaVersion=u'4.1')
        doc.paketTyp = 'SIP'
        doc.inhaltsverzeichnis = arelda.inhaltsverzeichnisSIP()

        header = arelda.ordnerSIP(u'header', u'header')
        doc.inhaltsverzeichnis.ordner.append(header)
        xsd = arelda.ordnerSIP(u'xsd', u'xsd')
        header.ordner.append(xsd)
        content = arelda.ordnerSIP(u'content', u'content')
        doc.inhaltsverzeichnis.append(content)

        doc.ablieferung = arelda.ablieferungGeverSIP()
        doc.ablieferung.ablieferungstyp = u'GEVER'
        doc.ablieferung.ablieferndeStelle = u'Amt f\xfcr Beispiele'
        doc.ablieferung.provenienz = arelda.provenienzGeverSIP()
        doc.ablieferung.provenienz.aktenbildnerName = u'Grossrat des Kantons'
        doc.ablieferung.provenienz.registratur = u'Ratsinformationssystem'

        catalog = getToolByName(self.context, 'portal_catalog')
        dossiers = catalog(portal_type='opengever.dossier.businesscasedossier')

        repo = model.Repository()
        for dossier in dossiers:
            repo.add_dossier(model.Dossier(dossier.getObject()))

        doc.ablieferung.ordnungssystem = repo.binding()
        # doc.ablieferung.ordnungssystem = arelda.ordnungssystemGeverSIP()
        # doc.ablieferung.ordnungssystem.name = repo.Title()

        tmpfile = TemporaryFile()
        with ZipFile(tmpfile, 'w', ZIP_DEFLATED, True) as zipfile:

            # add schema files
            for schema in os.listdir(schemas_path):
                filename = os.path.join(schemas_path, schema)
                arcname = os.path.join(sip_folder_name, 'header', 'xsd', schema)
                zipfile.write(filename, arcname)

                xsd.append(arelda.dateiSIP(
                    schema,
                    schema,
                    u'MD5',
                    u'fc855f31a14976b854dfd035bd515721',  # TODO: checksum
                    id=u'abcd',
                ))

            # add dossiers
            # op = arelda.ordnungssystempositionGeverSIP(id=u'abc')
            # op.nummer = u'1'
            # op.titel = u'Position 1'
            # doc.ablieferung.ordnungssystem.ordnungssystemposition.append(op)

            dom = doc.toDOM(element_name='paket')
            dom.documentElement.setAttributeNS(
                xsi.uri(),
                u'xsi:schemaLocation',
                u'http://bar.admin.ch/arelda/v4 xsd/arelda.xsd',
            )
            arcname = os.path.join(sip_folder_name, 'header', 'metadata.xml')
            zipfile.writestr(arcname, dom.toprettyxml(encoding='utf8'))

        size = tmpfile.tell()

        response = self.request.response
        response.setHeader(
            "Content-Disposition",
            'inline; filename="%s.zip"' % sip_folder_name)
        response.setHeader("Content-type", "application/zip")
        response.setHeader("Content-Length", size)

        return TempfileStreamIterator(tmpfile, size)


class TempfileStreamIterator(object):

    implements(IStreamIterator)

    def __init__(self, tmpfile, size, chunksize=1 << 16):
        self.size = size
        tmpfile.seek(0)
        self.file = tmpfile
        self.chunksize = chunksize

    def next(self):
        data = self.file.read(self.chunksize)
        if not data:
            self.file.close()
            raise StopIteration
        return data

    def __len__(self):
        return self.size