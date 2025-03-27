<b>Necessary Python modules for manual execution:</b>
- PyQt6 (pip install pyqt6)
- BeautifulSoup (pip install beautifulsoup4)
- easygui (pip install easygui)

Otherwise, check the dist folder for runnable Executable files! Currently has the following features:
- The ability to parse and create a sum of occurrences per unique entity ID in a set of rooms.
- The ability to add images representing each enemy with a matching value found from a Basement Renovator entity registry XML.
- The ability to filter the list of loaded enemies via a searchbar (available by default) and two separate lists of filters (available with Basement Renovator integration)

Currently allows you to load multiple roomlists (XML versions) and view what placeable objects occur in each roomlist, how many occur, and you can search for and filter entities. You can greatly enhance the experience by integrating https://github.com/Basement-Renovator/basement-renovator entity definition files. These XML files will add names, images, and up to two categories per placeable object that you can now filter! 
