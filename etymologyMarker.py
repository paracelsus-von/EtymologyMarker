import os
import re
import json
import io
import collections

def getOrigin(word, allWords):
    """ Returns the language origin of a word. """
    return allWords.get(word)

def whitespaceNum(number):
    """ Creates white-space for evenly distributing numbers. """
    if number < 10:
        return ' ' * 2
    elif number < 100:
        return  ' '
    else:
        return ''

def stripForDictionary(splitString, formattedList):
    """ Takes input, strips punctuation, makes lower-case, then appends to formattedList. """
    for word in splitString:
        stripped = re.sub('[^a-zA-Z]+', '', word)
        formattedList.append(stripped.lower())

def lookupInDictionary(formattedList, languages, splitString, allWords, greekRoots):
    """ Looks up words and applies html tags based on language origin. """
    for x, word in enumerate(formattedList):
        origin = getOrigin(word, allWords)
        if origin != None:
            splitString[x] = '<span style="background-color: #' + languages[origin]['colour']  + '">' + splitString[x] + '</span>'
            languages[origin]['word count'] += 1
        elif any(root in word for root in greekRoots):
            splitString[x] = '<span style="background-color: #' + languages['Greek']['colour'] + '">' + splitString[x] + '</span>'
            languages['Greek']['word count'] += 1
    return languages

def removeExtraHTML(formattedList, splitString, allWords):
    """ If two adjacent words are the same colour, 
    removes the first HTML tag from the second word and the second HTML tag from the first word. 
    This keeps the output from looking like a ransom letter.
    """
    for x, word in enumerate(formattedList[:-1]):
        nextWord = formattedList[x+1]
        originW1 = getOrigin(word, allWords)
        originW2 = getOrigin(nextWord, allWords)
        
        if originW1 == originW2 and originW1 != None:
            splitString[x+1] = splitString[x+1].replace('<span style="background-color: #' + languages[originW1]['colour'] + '">', '')
            splitString[x]   = splitString[x].replace('</span>', '')

def removeAffixes(formattedList, allWords):
    """ If the program can't find a word in the dictionary, 
    this function tries removing prefixes and suffixes.
    """
    for x in xrange(len(formattedList)):
        suffix_list = ['es$', 's$',   'est$', 'er$',  'ed$',  'ial$', 
                       'al$', 'ing$', 'ful$', 'age$', 'ist$', 'ism$', 'less$']
        for suffix in suffix_list:
            if getOrigin(formattedList[x], allWords) == None:
                formattedList[x] = re.sub(suffix, '', formattedList[x])
                
        if getOrigin(formattedList[x], allWords) == None:
            formattedList[x] = re.sub('fully$', 'ful', formattedList[x])

        if getOrigin(re.sub('ly$', "le", formattedList[x]), allWords) != None:  # Replaces -ly with -le if that produces a word.
            formattedList[x] = re.sub('ly$', 'le', formattedList[x])    
        else:
            formattedList[x] = re.sub('ly$', '',   formattedList[x])

        if getOrigin(re.sub('$', 'e', formattedList[x]), allWords) != None:     # Adds -e back onto words that had -e removed.
            formattedList[x] = re.sub('$',  'e', formattedList[x])
        elif getOrigin(formattedList[x], allWords) == None:                     # Handles words that end in -y, which gets changed to -ie when a suffix is added.
            formattedList[x] = re.sub('i$', 'y', formattedList[x])

        if getOrigin(formattedList[x], allWords) == None:
            formattedList[x] = re.sub('^re', '', formattedList[x])
            formattedList[x] = re.sub('^un', '', formattedList[x])

        if getOrigin(formattedList[x], allWords) == None:                       # Handles consonants that are doubled before -ed.
            for consonant in ['b', 'p', 'r', 'n', 't', 'd', 'g']:
                suffix = consonant*2 + '$'
                formattedList[x] = re.sub(suffix, consonant, formattedList[x])

def pieChart(legend, colours):
    """ Returns JavaScript for a pie chart using Google Charts API 
    with appropriate colours for languages in legend.
    """
    return """
    <head>
      <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
      <script type="text/javascript">
        google.charts.load('current', {'packages':['corechart']});
        google.charts.setOnLoadCallback(drawChart);
        function drawChart() {

          var data = google.visualization.arrayToDataTable([
            ['Language', 'Number of Words'], """ + legend + """ 
          ]);

          var options = {
            title: 'Language Density',
            slices: [""" + colours + """
          ]};

          var chart = new google.visualization.PieChart(document.getElementById('piechart'));

          chart.draw(data, options);
        }
      </script>
    </head>
    <body>
      <div id="piechart" style="width: 900px; height: 500px;"></div>
    </body>
</html>"""

languages = {'Anglo':    {'colour': '8BC34A', 'word count': 0, 'colour name': 'Green',      'long name': 'Anglo-Saxon' },
             'Germanic': {'colour': '4CAF50', 'word count': 0, 'colour name': 'Dark green', 'long name': 'other Germanic (Old Norse, Scandinavian, German, Dutch)'},
             'French':   {'colour': 'FFC107', 'word count': 0, 'colour name': 'Amber',      'long name': 'French'},
             'Latin':    {'colour': 'F44336', 'word count': 0, 'colour name': 'Red',        'long name': 'Latin'},
             'Arabic':   {'colour': '7B1FA2', 'word count': 0, 'colour name': 'Purple',     'long name': 'Arabic'},
             'Greek':    {'colour': '03A9F4', 'word count': 0, 'colour name': 'Light Blue', 'long name': 'Greek'},
             'Spanish':  {'colour': 'FF5722', 'word count': 0, 'colour name': 'Orange',     'long name': 'Spanish'},
             'Celtic':   {'colour': '009688', 'word count': 0, 'colour name': 'Teal',       'long name': 'other Celtic (Common Brittonic, Gaulish, Irish, Scottish Gaelic, Welsh)'},
             'Italian':  {'colour': 'FFEB3B', 'word count': 0, 'colour name': 'Yellow',     'long name': 'Italian'},
             'Indian':   {'colour': 'E040FB', 'word count': 0, 'colour name': 'Lilac',      'long name': 'Indian'},
             'Malay':    {'colour': '303F9F', 'word count': 0, 'colour name': 'Indigo',     'long name': 'Malay'},
            }
languages = collections.OrderedDict(sorted(languages.items()))

def main():
    directory = raw_input("Input working directory: ")
    if len(directory) < 1:
        directory = 'WORKING DIRECTORY GOES HERE'
    os.chdir(directory)

    fileName = raw_input("Input text file to analyse (Note: must be in UTF-16 format): ")
    if len(fileName) < 1:
        fileName = 'usertext.txt'
        
    stats_marker = raw_input("Do you want the info displayed as a pie chart? (y/n): ").lower()

    with open('etymologyDictionary.json', 'r') as dictionaryfile:                                # Reads in the dictionary and list of Greek roots from .json files.
        allWords = json.load(dictionaryfile)

    with open('greekRootsList.json', 'r') as greekfile:
        greekRoots = json.load(greekfile)

    markedUp = io.open('markedUp.html', encoding='utf-8', mode='w')                              # Opens an output file and adds a legend.
    markedUp.write(unicode('<html>\n<p> Key: </p>'))

    for language in sorted(languages.keys()):                                                    # Writes legend/key to start of html file
        markedUp.write(unicode('<p><span style="background-color: #' 
                               + languages[language]['colour']      + '">' 
                               + languages[language]['colour name'] + '</span> words are of ' 
                               + languages[language]['long name']   + ' origin. </p>\n'))
    markedUp.write(unicode('<br>\n'))

    with io.open(fileName, encoding='utf-16', mode='r') as f:                                    # Opens the user's input file, runs the functions on each line of text,
        usertext = f.readlines()                                                                 # then writes the results to the output file.
        TotalWordCount = 0

        for line in usertext:
            formattedList = []
            splitString = line.split()
            TotalWordCount += len(splitString)
            stripForDictionary(splitString, formattedList)
            removeAffixes(formattedList, allWords)
            lookupInDictionary(formattedList, languages, splitString, allWords, greekRoots)
            removeExtraHTML(formattedList, splitString, allWords)
            joinedString = ' '.join(splitString)
            joinedString = joinedString.replace('</span> ', ' </span>')                          # Highlights spaces between words
            markedUp.write(unicode('<p>' + joinedString + '</p>'))

    legend_js  = ''                                                                              # Creates legend and colour list for JavaScript Pie Chart
    colours_js = ''
    statistics = '<br><p>Percent composition:</p>'
    for language in sorted(languages.iteritems(), key=lambda (k, v): v['word count'], reverse = True):
        legend_js  += ("\n" + " "*12 + "['" + language[1]['long name'] + "', " + str(language[1]['word count']) + "], ")
        colours_js += ("\n" + " "*12 + "{color: '#" + language[1]['colour'] + "'}, ")  
        percent     = language[1]['word count'] * 100.0 / TotalWordCount
        statistics += ('\n<pre>' + whitespaceNum(percent) + '{:.2f} percent '.format(percent) + language[1]['long name'] + '</pre>')
    
    if stats_marker == 'y':
        markedUp.write(unicode(pieChart(legend_js, colours_js)))
    else:
        markedUp.write(unicode(statistics))
    markedUp.close()

if __name__ == "__main__":
    main()
