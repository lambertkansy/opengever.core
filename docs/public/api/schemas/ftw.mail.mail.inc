.. py:class:: ftw.mail.mail

    Inhaltstyp 'E-Mail'



   .. py:attribute:: message

       :Feldname: :field-title:`Orginalnachricht`
       :Datentyp: ``NamedBlobFile``
       
       
       
       


   .. py:attribute:: classification

       :Feldname: :field-title:`Klassifikation`
       :Datentyp: ``Choice``
       :Pflichtfeld: Ja :required:`(*)`
       :Default: "unprotected"
       :Beschreibung: Grad, in dem die Unterlagen vor unberechtigter Einsicht geschützt werden müssen
       :Wertebereich: ["unprotected", "confidential", "classified"]


   .. py:attribute:: privacy_layer

       :Feldname: :field-title:`Datenschutzstufe`
       :Datentyp: ``Choice``
       :Pflichtfeld: Ja :required:`(*)`
       :Default: "privacy_layer_no"
       :Beschreibung: Markierung, die angibt, ob die Unterlagen besonders schützenswerte Personendaten oder Persönlichkeitsprofile gemäss Datenschutzrecht enthalten
       :Wertebereich: ["privacy_layer_no", "privacy_layer_yes"]


   .. py:attribute:: public_trial

       :Feldname: :field-title:`Öffentlichkeitsstatus`
       :Datentyp: ``Choice``
       :Pflichtfeld: Ja :required:`(*)`
       :Default: "unchecked"
       :Beschreibung: Angabe, ob die Unterlagen gemäss Öffentlichkeitsgesetz zugänglich sind oder nicht
       :Wertebereich: ["unchecked", "public", "limited-public", "private"]


   .. py:attribute:: public_trial_statement

       :Feldname: :field-title:`Bearbeitungsinformation`
       :Datentyp: ``Text``
       
       :Default: ""
       :Beschreibung: Datum Gesuch, Gesuchsteller, Datum Entscheid, Verweis auf GEVER-Gesuchdossier
       


   .. py:attribute:: description

       :Feldname: :field-title:`Beschreibung`
       :Datentyp: ``Text``
       
       
       
       


   .. py:attribute:: keywords

       :Feldname: :field-title:`Schlagworte`
       :Datentyp: ``Tuple``
       
       
       
       


   .. py:attribute:: foreign_reference

       :Feldname: :field-title:`Fremdzeichen`
       :Datentyp: ``TextLine``
       
       
       :Beschreibung: Referenz auf das entsprechende Dossier des Absenders
       


   .. py:attribute:: document_date

       :Feldname: :field-title:`Dokumentdatum`
       :Datentyp: ``Date``
       
       :Default: <Aktuelles Datum>
       :Beschreibung: Datum des Dokuments
       


   .. py:attribute:: receipt_date

       :Feldname: :field-title:`Eingangsdatum`
       :Datentyp: ``Date``
       
       
       :Beschreibung: Datum, an dem das Dokument über den Korrespondenzweg angekommen ist
       


   .. py:attribute:: delivery_date

       :Feldname: :field-title:`Ausgangsdatum`
       :Datentyp: ``Date``
       
       
       :Beschreibung: Datum, an dem das Dokument über den Korrespondenzweg versandt worden ist
       


   .. py:attribute:: document_type

       :Feldname: :field-title:`Dokumenttyp`
       :Datentyp: ``Choice``
       
       
       
       :Wertebereich: ["question", "request", "report", "offer", "protocol", "regulations", "contract", "directive"]


   .. py:attribute:: document_author

       :Feldname: :field-title:`Autor`
       :Datentyp: ``TextLine``
       
       
       :Beschreibung: Nachname Vorname oder ein Benutzerkürzel (wird automatisch nach Nachname Vorname aufgelöst).
       


   .. py:attribute:: digitally_available

       :Feldname: :field-title:`Digital verfügbar`
       :Datentyp: ``Bool``
       
       
       
       


   .. py:attribute:: preserved_as_paper

       :Feldname: :field-title:`In Papierform aufbewahrt`
       :Datentyp: ``Bool``
       
       :Default: true
       :Beschreibung: In Papierform aufbewahrt
       


   .. py:attribute:: archival_file

       :Feldname: :field-title:`Archivierte Datei`
       :Datentyp: ``NamedBlobFile``
       
       
       :Beschreibung: Archivtaugliche Version der Originaldatei
       


   .. py:attribute:: thumbnail

       :Feldname: :field-title:`Kurzbild`
       :Datentyp: ``NamedBlobFile``
       
       
       
       


   .. py:attribute:: preview

       :Feldname: :field-title:`Vorschau`
       :Datentyp: ``NamedBlobFile``
       
       
       :Beschreibung: Online Voransicht des Originaldokuments
       


   .. py:attribute:: title

       :Feldname: :field-title:`Titel`
       :Datentyp: ``TextLine``
       
       
       
       


   .. py:attribute:: changeNote

       :Feldname: :field-title:`Änderungsnotiz`
       :Datentyp: ``TextLine``
       
       
       :Beschreibung: Geben Sie einen Kommentar ein, der die von Ihnen gemachten Änderungen beschreibt.
       