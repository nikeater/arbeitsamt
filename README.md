Dieses Projekt ermöglicht derzeit das Abgreifen sämtlicher Stellenbeschreibungen der Agentur für Arbeit,
woraufhin diese per LLM automatisch auf Passung (anhand CV) analysiert werden. Das Ergebnis wird in einer
SQLite3 Datenbank gespeichert, und steht dann zur Auswahl durch den Kandidaten zur Verfügung. Für als interessant
markierte Stellen wird im nächsten Schritt per LLM ein Anschreiben formuliert, welches automatisch als Latex-File
gerendert wird.
