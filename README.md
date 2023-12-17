Co-mentioned is a very simple yet effective tool that helps finding co-mentions of keywords in web pages.

While doing research on entities of interest (companies, people, whatever) you may need to check if two or more of the target entities are mentioned by the same web page at the same time. 

This tool comes in handy if you have multiple keywords/entities and need to quickly assess whether there are interesting co-mentions.

You will first need to install some python modules:

pip install inscriptis
pip install numpy
pip install unidecode

Now you will need a ScaleSerp API: co-mentioned searches Google via a third-party API. Free tokens are available at ScaleSerp and paid ones are fairly cheap too. 

Save your token in the 'token.txt' file.

Now, type your target keywords/entities in the 'entities.txt' file. One line, one entity. No quotes:

alaeddin senguler
trend gyo
hamas

Now you're set and can run the co-mentioned.py file:

python3 co-mentioned.py

The tool will first combine the entities you saved in the entities.txt file generating as many keyword pairs as possible. Then it will search each pair on Google in order to retrieve urls. In our case, it will look up on Google:

"alaeddin senguler" "trend gyo"
"alaeddin senguler" "hamas"
"hamas" "trend gyo"

Quotes are added automatically, so you won't need to enclose keywords in quotes in the entities.txt file. 

You can use non standard characters (è,é, à,ò), etc. It may increase the quality of Google search results but it won't affect the way co-mentioned works, as all text is unidecoded for consistency.

In the previous case, just three keyword pairs can be created. Of course, the more entities you type in entities.txt, the more pairs you will get (this may quickly exhaust your ScaleSerp account).

If your ScaleSerp token has enough API calls to complete the search job, it will search Google for URLs. 
Next, it will start opening each url in order to:

a) detect if at least 2 keywords are on the web page
b) compute the minimum distance between the keywords

If more than 1 keyword are on the same page, co-mentioned computes the minimum distance between the keywords and saves the results in the REPORT.csv file.

Note that co-mentioned *searches* keyword pairs but *detects* all the keywords that you typed in the entities.txt file.

The REPORT.csv file is created automatically in the local directory and contains three columns separated by '|':

URL|Entities|Distance

Last but not least, in the case where three or more entities are matched in the same web page, the "Distance" indicator is about the closest pair of entities.
