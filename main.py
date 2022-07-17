from pathlib import Path
from time import sleep
import signal
import sys
import os

from tkinter import filedialog
from gtts import gTTS
import PyPDF2

def loadBar(currentIteration, iterationsTotal, prefix = '', suffix = '', decimals = 1, barLength = 20, fill = '>', isMinBarShown = True):
  percent = ('{0:.' + str(decimals) + 'f}').format(100 * (currentIteration/float(iterationsTotal)))
  terminalSize = os.get_terminal_size()
  terminalWidth = terminalSize.columns
  prefixLength = len(prefix)
  suffixLength = len(suffix)
  updatedBarLength = terminalWidth - prefixLength - suffixLength

  if (isMinBarShown):
    updatedBarLength = barLength

  charsToFill = int(updatedBarLength * currentIteration // iterationsTotal)
  bar = fill * charsToFill + '-' * (updatedBarLength - charsToFill)
  barChars = f'\r{prefix} |{bar}| {percent}% {suffix}'

  print(barChars, end = '\r', flush = True)
  print(barChars, end="", flush = True)

  if currentIteration == iterationsTotal:
    print('\n')

def signalHandler(sig, frame):
    print('\n\nGoodbye.\n')
    sys.exit(0)

pdfLocation = filedialog.askopenfilename()
pdfContent = ""
firstPageNumber = int(input("Enter the first page number: "))
pdfBasename = os.path.basename(pdfLocation)
pdfName = Path(pdfBasename).stem
audioFileName = pdfName + ' - audio.mp3'
speechSentences = list()

signal.signal(signal.SIGINT, signalHandler)

with open(pdfLocation, 'rb') as book:
  try:
    reader = PyPDF2.PdfFileReader(book)
    pagesTotal = reader.numPages
    totalPagesToRead = pagesTotal - firstPageNumber + 1
    barPrefix = 'Loading speech progress'
    barSuffix = 'Complete'

    print('\nPDF location: ' + pdfLocation)
    print('PDF name: ' + pdfName)
    print('Audio file name: ' + audioFileName)
    print('Total (pages): ' + str(totalPagesToRead) + ' of ' + str(pagesTotal) + '\n')

    loadBar(0, pagesTotal, prefix = barPrefix, suffix = barSuffix)

    currentPageNumber = 0
    try:
      for page in range(firstPageNumber-1, pagesTotal):
        currentPage = reader.getPage(page)
        pageContent = currentPage.extractText()
        pdfContent = str(pageContent)
        pageSpeech = gTTS(text = pdfContent)
        speechSentences.append(pageSpeech)
        currentPageNumber += 1

        sleep(0.2)
        loadBar(currentPageNumber, pagesTotal, prefix = barPrefix, suffix = barSuffix)

      loadBar(pagesTotal, pagesTotal, prefix = barPrefix, suffix = barSuffix)

    except Exception as error:
      print('\n\nERROR: Failed to read PDF page')
      print(str(error) + '\n')
      
  except Exception as error:
    print('n\nERROR: Invalid PDF')
    print(str(error) + '\n')

sentencesTotal = len(speechSentences)
barPrefix = 'Saving mp3 progress'
barSuffix = 'Complete'

with open(audioFileName, 'wb') as fp:
  loadBar(0, sentencesTotal, prefix = barPrefix, suffix = barSuffix)

  currentSentenceNumber = 0
  try:
    for speech in speechSentences:
      speech.write_to_fp(fp)

      currentSentenceNumber += 1
      sleep(0.2)
      loadBar(currentSentenceNumber, sentencesTotal, prefix = barPrefix, suffix = barSuffix)

    print('\nPress Ctrl+C to exit\n\n')

  except Exception as error:
    print('\n\nERROR: Unable to save mp3')
    print(str(error) + '\n')
