Seriendruckfelder
-----------------

Pro Gremium können die folgenden Wordvorlagen hinterlegt werden:

- Sitzungseinladung / Traktandenliste (geplant)
- Protokoll
- Protokollauszug

Diese Vorlagen werden vom Modul „Sitzungs- und Protokollverwaltung“ verwendet,
um automatisiert die entsprechenden Dokumente zu einer Sitzung zu erzeugen.
Damit dies möglich ist, verwenden die Vorlagen Seriendruckfelder, um Daten aus
der Sitzung direkt in die Wordvorlage zu übertragen und so ein neues
Worddokument zu erzeugen.

Die folgenden Seriendruckfelder können standardmässig verwendet werden:

Metadaten zur Sitzung:
~~~~~~~~~~~~~~~~~~~~~~

- ``mandant.name``

  Titel der OneGov GEVER Installation (String)

- ``protocol.type``

  Art des Protokolls („Protokoll“, „Protokollauszug“)

- ``committee.name``

  Name des Gremiums

- ``meeting.date``

  Datum der Sitzung

- ``meeting.location``

  Standort der Sitzung


- ``meeting.start_time``

  Beginn der Sitzung (Uhrzeit)

- ``meeting.end_time``

  Ende der Sitzung (Uhrzeit)

- ``meeting.number``

  Sitzungsnummer. Beginnt am Anfang einer Sitzungsperiode (üblicherweise ein
  Kalenderjahr) immer mit 1. Die Sitzungsnummer wird von OneGov GEVER erst
  vergeben, wenn mindestens 1 Traktandum (oder die ganze Sitzung)
  abgeschlossen wurde.

- ``participants.presidency``

  Vorsitz der Sitzung (Participant)

- ``participants.secretary``

  Sekretär der Sitzung (Participant)

- ``participants.members``

  Liste aller Teilnehmenden (Liste von Participant, siehe unten)

- ``participants.other``

  Liste aller weiteren Teilnehmenden/Gäste (Liste von Strings)

- ``participants.members``

  Liste aller Teilnehmenden zur Sitzung (Liste von Participant). Über diese
  Liste wird typischer-weise iteriert, um die Namen darzustellen (siehe weiter
  unten).

- ``agenda_items``

  Liste von Traktanden (Liste von AgendaItem)


Metadaten zu einem Sitzungsteilnehmer (Participant):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``member.fullname``

  Vollständiger Name eines Teilnehmers (String). Dabei ist member eine
  Laufvariable, die für die Iteration über alle Elemente von
  ``participants.members`` verwendet wird.

- ``member.role``

  Definierte Rolle des Teilnehmers innerhalb der Sitzung (String). Dabei ist
  member eine Laufvari-able, die für die Iteration über alle Elemente von
  ``participants.members`` verwendet wird.

- ``member.email``

  Die E-Mail Adresse eines Teilnehmers (String).


Metadaten zu einem Traktandum (AgendaItem):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``repository_folder_title``

  Titel der Ordnungsposition zum aktuellen Traktandum (String). Je nach
  definierter Sprache des Antrags wird hier der deutsche oder französische
  OP-Titel zurückgegeben

- ``title``

  Titel des Antrags (String).

- ``number``

  Traktandennummer (startet bei jeder neuen Sitzung wieder bei 1).

- ``dossier_reference_number``

  Aktenzeichen des Dossiers (String), in der sich der Antrag befindet.

- ``decision_number``

  Beschlussnummer (String). Diese Nummer wird von der Sitzungs- und
  Protokollverwaltung auto-matisch vergeben, wobei die Nummerierung jeweils
  bei Anfang einer neuen Sitzungsperiode (üb-licherweise ein Kalendarjahr)
  wieder bei 1 beginnt.

- ``is_paragraph``

  Gibt an, ob es sich um einen Abschnitt handelt oder nicht (Boolean).

- ``legal_basis``

  Rechtsgrundlage des Antrags (Text).

- ``initial_position``

  Ausgangslage des Antrags (Text).

- ``considerations``

  Erwägungen zum Antrag (Text).

- ``proposed_action``

  Text des Antrags (Text).

- ``discussion``

  Diskussion während der Sitzung zum Antrag (Text).

- ``decision``

  Beschluss zum Antrag gemäss Sitzung (Text).

- ``disclose_to``

  Zu eröffnen an (Text).

- ``copy_for_attention``

  Kopie geht an (Text).

- ``publish_in``

  Zu veröffentlichen in (Text).

- ``attachments``

  Liste von Anhängen des Antrags (Liste von Attachment).


Metadaten zu einem Anhang eines Antrags (Attachment):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``title``

  Titel des Dokumentes (Text).

- ``filename``

  Dateiname der Datei (Text).


Metadaten zu einer Inhaltsverzeichnis-Gruppe:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``group_title``

  Titel/Name des Elementes nach dem das Inhaltsverzeichnis gruppiert wurde. Entweder der erste Buchstabe des Antrags/Traktandums oder der Name der Ordnungsposition (Text).

- ``contents``

  Liste aller der Inhaltsverzeichnis-Elemente aller Traktanden/Anträge (Liste von Inhaltsverzeichnis-Elementen, siehe unten)


Metadaten zu einem Inhaltsverzeichnis-Element:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``title``

  Titel des Antrags/Traktandums (Text).

- ``dossier_reference_number``

  Aktenzeichen des Dossiers eines Antrags (Text).

- ``repository_folder_title``

  Titel der Ordnungsposition eines Antrags (Text).

- ``decision_number``

  Beschlussnummer des Antrags/Traktandums (Text).

- ``has_proposal``

  Gibt an, ob es sich um ein Traktandum mit oder ohne Antrag handelt (Boolean).

- ``meeting_date``

  Datum der Sitzung des Antrags/Traktandums (Text).

- ``meeting_start_page_number``

  Start-Seitenzahl der Sitzung (Text).

.. disqus::