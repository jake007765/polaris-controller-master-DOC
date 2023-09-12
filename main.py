from flask import Flask, render_template, request, redirect
#these imports are not currently used
from jinja2 import Environment, FileSystemLoader
from urllib.parse import urlparse, unquote, quote
import requests
import json
import random
import os.path
import pymysql

import secret

app = Flask(__name__)
parsedArticles = []

# Front page loads 27 articles, plus one randomly selected at the top
@app.route("/")
@app.route("/frontpage/")
def index():
    '''This function loads the first page of the Reporter website. 27 articles are 
    loaded as the default. One random article is selected to be featured at the top of this page.'''
    global parsedArticles
    page = request.args.get('page')
    if not page:
        page = 1
    if page == 1:
        # find where loadArticles is defined
        loadArticles(0, 27)
        rand = random.randint(0, 4)
        #what does this do
        while parsedArticles[rand]['title'].startswith('SG'):
            rand = random.randint(0, 4)
        featuredArticle = parsedArticles.pop(rand)
        return render_template("luna-theme/frontend/index.html", advertisementOn=True, articles=parsedArticles, featuredArticle=featuredArticle, urlparse=urlparse)
    else:
        numberOfArticles = 27   # Note: sometimes we will have less than this number
        loadArticles((int(page) - 1) * numberOfArticles, numberOfArticles)
        return render_template("luna-theme/frontend/article-feed.html", pageNumber=int(page), pageTitle="Articles", pageHeading="All Articles", articles=parsedArticles, numberOfArticles=numberOfArticles, urlparse=urlparse, sectionPath="/")

@app.route("/news/<article_path>")
@app.route("/culture/<article_path>")
@app.route("/leisure/<article_path>")
@app.route("/features/<article_path>")
@app.route("/sports/<article_path>")
@app.route("/wellness/<article_path>")
@app.route("/views/<article_path>")
@app.route("/tech/<article_path>")
@app.route("/op-ed/<article_path>")
@app.route("/distorter/<article_path>")
#is article_path a necessary argument? 
def article(article_path):
    '''This function loads a specific article and formats it'''
    articleContent = getArticleContent(request.url)
    print(articleContent)
    #what does it mean if the article is a slideshow
    if 'slideshow' in articleContent and len(articleContent['slideshow']) > 0:
        #find render_template
        return render_template("luna-theme/frontend/article_slideshow.html",
        articleContent = renderArticleToHTML(articleContent),
        title = articleContent['title'],
        date = articleContent['date_format'],
        author = articleContent['authors'][0],
        slideshow = articleContent['slideshow']
    )
    return render_template("luna-theme/frontend/article_dumb.html",
        articleContent = renderArticleToHTML(articleContent),
        title = articleContent['title'],
        date = articleContent['date_format'],
        author = articleContent['authors'][0],
        image = articleContent['imgLink']
    )

@app.route("/sports/")
def redirect_sports():
    '''If the user tries to go to the non-existent sports section, they get redirected to wellness content instead.'''
    return redirect("https://reporter.rit.edu/wellness/", code=301)
    return redirect(request.url.replace("sports", "wellness", 1), code=301)

@app.route("/news/")
@app.route("/leisure/")
@app.route("/culture/")
@app.route("/features/")
@app.route("/wellness/")
@app.route("/views/")
@app.route("/tech/")
@app.route("/op-ed/")
@app.route("/distorter/")
def section():
    '''Loads the section pages for each category, and 24 articles are listed 
    on each page, unless there's fewer than that'''
    page = request.args.get('page')
    if not page:
        page = 1
    path = os.path.dirname(request.url)[1:]
    components = path.split("/")
    print("COMPONENTS: ")
    print(components)
    title = components[3]
    #confused where this comes from
    if title is None:
        title = "Articles"
    if title == "sports":
        title = "Wellness"
    elif title == "leisure":
        title = "Culture"
    numberOfArticles = 24   # Note: sometimes we will have less than this number
    sectionArticles = loadArticlesFromSection(components[len(components) - 1], (int(page) - 1) * numberOfArticles, numberOfArticles)
    return render_template("luna-theme/frontend/article-feed.html", pageNumber=int(page), pageTitle=title, pageHeading=title, articles=sectionArticles, numberOfArticles=numberOfArticles, urlparse=urlparse, sectionPath= "/" + components[3] + "/")


# @app.route("/wellness/<article_path>")
# def article_wellness(article_path):
#     new_url = request.url.replace('/wellness/', '/sports/', 1)
#     return new_url
#     articleContent = getArticleContent(new_url)
#     return render_template("luna-theme/article_dumb.html",
#         articleContent = renderArticleToHTML(articleContent),
#         title = articleContent['title'],
#         date = articleContent['date_format'],
#         author = articleContent['authors'][0],
#         slideshow = articleContent['slideshow']
#     )

@app.route("/search/<query>")
def page_search(query):
    #Possible this is the search function 
    global parsedArticles
    page = request.args.get('page')
    if not page:
        page = 1
    numberOfArticles = 24   # Note: sometimes we will have less than this number
    searchArticles = loadArticlesFromSearch(query, (int(page) - 1) * numberOfArticles, numberOfArticles)
    # return searchArticles
    return render_template("luna-theme/frontend/article-feed.html", pageNumber=int(page), pageTitle="Search", pageHeading="Results for '" + query + "'", articles=searchArticles, numberOfArticles=numberOfArticles, urlparse=urlparse, sectionPath="/search/" + query)

#Food for thought: can we change these functions to be adapted to different themes? 
#If a web designer in the future wants to change it
@app.route("/podcast/")
def page_podcast():
    '''Loads the podcast page with the Luna theme'''
    return render_template("luna-theme/frontend/podcast.html")

@app.route("/people/")
def page_people():
    '''Loads the people page with the Luna theme'''
    return render_template("luna-theme/frontend/people.html")

@app.route("/office-hours/")
def page_office_hours():
    '''Loads the office hours page with the Luna theme'''
    #To-Do: office hours on website are not up to date
    return render_template("luna-theme/frontend/office-hours.html")

@app.route("/join-us/")
def page_join_us():
    '''Loads the join us page with the Luna theme'''
    return render_template("luna-theme/frontend/join-us.html")

@app.route("/about/")
def page_about():
    '''Loads the about page with the Luna theme'''
    return render_template("luna-theme/frontend/about.html")

@app.route("/magazine-locations/")
def page_locations():
    '''Loads the map of magazine stands as a page with Luna theme'''
    return render_template("luna-theme/frontend/magazine-locations.html")

@app.route("/advertise/") # Preferred
@app.route("/advertise-reporter/") # Backwards compatibility
def page_advertise():
    '''Loads the advertisement page with the Luna theme'''
    #The data on this page needs to be update 
    #Possibly add a form for people to submit an advertising request 
    return render_template("luna-theme/frontend/advertise.html")

@app.route("/submit-ad/")
def page_submit_ad():
    return render_template("luna-theme/frontend/submit-ad.html")

@app.route("/tipline/") # Preferred
@app.route("/tipline/index.php/851887/") # Backwards compatibility
def page_tipline():
    return render_template("luna-theme/frontend/tipline.html")

@app.route("/beta-user/<user_id>")
def page_user(user_id):
    data = getUserData(user_id)
    profile_pic_url = "https://reporter.rit.edu/sites/pubDir/" + data['uri'][9:]
    return render_template("luna-theme/frontend/user.html", mail=data['mail'], fullname=data['field_fullname_value'], profile_picture=profile_pic_url)

@app.route("/march2022/")
def page_march():
    return render_template("luna-theme/frontend/temporary/march.html")

def getNodeIDFromUrl(url, recurse = True):
    connection = pymysql.connect(
        host =        secret.MYSQL_SERVER_ADDRESS,
        port =        secret.MYSQL_SERVER_PORT,
        user =        secret.MYSQL_USER,
        password =    secret.MYSQL_PASSWORD,
        db =          secret.MYSQL_DATABASE,
        charset =     secret.MYSQL_CHARSET,
        cursorclass = pymysql.cursors.DictCursor
    )

    c = connection.cursor(pymysql.cursors.DictCursor)
    print(url)
    url_path = urlparse(unquote(url)).path[1:]
    print(url_path)
    query = "SELECT source FROM drupal_url_alias WHERE alias=%s AND source LIKE 'node/%%';"
    print(c.mogrify(query,(url_path)))
    c.execute(query, (url_path))
    data = c.fetchone()
    connection.close()
    c.close()
    print(data)
    return int(data['source'][5:])

    global parsedArticles
    print("*************Parsed articles globl: ")
    print(parsedArticles)
    url = urlparse(url).path
    for article in parsedArticles:
        print("Article START")
        print(article)
        print("Article END")
        print("Url: " + url)
        print("other: " + urlparse(unquote(article['articleLink'])).path)
        if url == urlparse(unquote(article['articleLink'])).path:
            print("Returning: %s" % article['nid'])
            return article['nid']
        else:
            print("\n\n...")
            print(article['articleLink'])
            print(url)
            print("\n\n...")
    if recurse:
        loadArticles()
        return getNodeIDFromUrl(url, False)
    print("Critical Error: no NodeID found matching URL.")
    return None

def loadArticles(start=0, results=500):
    try:
        global parsedArticles
        articles = requests.get("https://reporter.rit.edu:8443/api/articles.json?start=%s&results=%s" % (str(start), str(results)), verify=False).content
        parsedArticles = json.loads(articles)
    except:
        print("FATAL ERROR: Failed to load articles from the API.")

def loadArticlesFromSection(section, start=0, results=26):
    query = ("https://reporter.rit.edu:8443/api/articles.json?start=%s&amp;results=%s&amp;section=%s" % (str(start), str(results), section))
    query = ('https://reporter.rit.edu:8443/api/articles.json?start=' + str(start) + '&results=' + str(results) + '&section=' + section)
    print("QUERY: ====================================================")
    print(query)
    sectionArticles = requests.get(query, verify=False).content
    print(sectionArticles)
    return json.loads(sectionArticles)

def loadArticlesFromSearch(searchText, start=0, results=26):
    # query = ("https://reporter.rit.edu:8443/api/articles.json?start=%s&amp;results=%s&amp;search=%s" % (str(start), str(results), searchText))
    query = ('https://reporter.rit.edu:8443/api/articles.json?start=' + str(start) + '&results=' + str(results) + '&search=' + quote(searchText))
    # return query
    searchArticles = requests.get(query, verify=False).content
    return json.loads(searchArticles)


def getArticleContent(url):
    nodeID = getNodeIDFromUrl(url)
    print("NodeID: %s" % nodeID)
    str = 'https://reporter.rit.edu:8443/api/article/%i.json' % nodeID
    print(str)
    article = requests.get(str, verify=False).content
    print(article)
    parsedArticle = json.loads(article)
    return parsedArticle

def renderArticleToHTML(article):
    body = article['body']
    html = ""
    count = 0
    for chunk in body:
        html += renderHelper(chunk, count, len(body))
        count += 1
    return html

def renderHelper(chunk, index = -1, body_len = -1):
    print(chunk)
    if (isinstance(chunk, str)):
        return chunk
    elif (isinstance(chunk, list)):
        value = ""
        for subChunk in chunk:
            value += renderHelper(subChunk)
        return value
    elif ('contents' in chunk):
        print("HERE:")
        print("%s" % chunk['tag'].lower())
        print("%s" % ('tag' in chunk['contents'][0]))
        print("%s" % chunk['contents'][0])
        if (chunk['tag'].lower() == 'p' and
            len(chunk['contents']) == 1 and
            not isinstance(chunk['contents'][0], str) and
            'tag' in chunk['contents'][0] and
            chunk['contents'][0]['tag'].lower() == 'strong'
        ):
            return "<h2>%s</h2>" % renderHelper(chunk['contents'][0]['contents'])
        if (chunk['tag'].lower() == 'span' and
            'class' in chunk and
            (chunk['class'] == 'added' or chunk['class'] == 'removed')
        ):
            return renderHelper(chunk['contents'][0])
        tagAttributes = getTagAttributes(chunk)
        value = "<%s %s>" % (chunk['tag'], tagAttributes)
        content = renderHelper(chunk['contents'])
        # Adds the first letter formatting of article
        if index == 0 and chunk['tag'].lower() == 'p':
            # If first character isnt the start of a tag
            if content[0:1] != '<':
                value += "<span class=\"firstLetter\">"
                value += content[0:1]
                value += "</span>"
                value += content[1:]
            # If the first character IS start of a tag
            else:
                ind = getIndexOfFirstCharacter(content)
                value += content[0:ind]
                value += "<span class=\"firstLetter\">"
                value += content[ind:ind + 1]
                value += "</span>"
                value += content[ind + 1:]
        # Adds the R logo at bottom of article
        elif body_len > 0 and index == body_len - 1:
            value += content
            value += "<img class=\"articleEnd\" ondragstart=\"return false;\" src=\"/static/res/img/main/articleend.png\">"
        else:
            value += content
        value += "</%s>" % chunk['tag']
        return value
    elif (chunk['tag'] == 'img'):
        src = "https://reporter.rit.edu" + chunk['src']
        alt = chunk['alt']
        if (alt is None):
            alt = ""
        value = "<img src=\"%s\" alt=\"%s\">" % (src, alt)
        return value
    else:
        print("OH MY FUCKING FOD WHAT THAT HEL;L!!!!!!!!!!!!!!!!!!!!")
        print(chunk)
        return ""
        return chunk

def getTagAttributes(chunk):
    attrs = ""
    if ("href" in chunk):
        attrs += " href=\"%s\" " % chunk["href"]
    return attrs

def getIndexOfFirstCharacter(text):
    returnValue = 0
    if text[0:1] != '<' and text[0:1] != '>':
        returnValue = 0
    elif text[0:1] == '<':
        ind = text.index('>')
        returnValue = ind + 1 + getIndexOfFirstCharacter(text[ind + 1:])
    return returnValue

def getUserData(user_id):
    connection = pymysql.connect(
        host =        secret.MYSQL_SERVER_ADDRESS,
        port =        secret.MYSQL_SERVER_PORT,
        user =        secret.MYSQL_USER,
        password =    secret.MYSQL_PASSWORD,
        db =          secret.MYSQL_DATABASE,
        charset =     secret.MYSQL_CHARSET,
        cursorclass = pymysql.cursors.DictCursor
    )

    c = connection.cursor(pymysql.cursors.DictCursor)
    query = ("SELECT * FROM drupal_users "
             "INNER JOIN drupal_field_data_field_fullname "
             "ON drupal_users.uid = drupal_field_data_field_fullname.entity_id "
             "INNER JOIN drupal_file_managed "
             "ON drupal_users.picture = drupal_file_managed.fid "
             "WHERE drupal_users.name=%s "
             ";")
    print(c.mogrify(query, (user_id)))
    c.execute(query, (user_id))
    data = c.fetchone()
    connection.close()
    c.close()
    print(data)
    return (data)

# Backend routes -----------------------------------------------------------------

@app.route("/admin/dashboard")
def admin_page_dashboard():
    return render_template("luna-theme/backend/dashboard.html")

@app.route("/admin/articles")
def admin_page_articles():
    articles_raw = requests.get(secret.STRAPI_SERVER_ADDRESS + "/articles/").content
    articles = json.loads(articles_raw)

    my_articles_raw = requests.get(secret.STRAPI_SERVER_ADDRESS + "/articles?authorDisplay=Efe%20Ozturkoglu").content
    my_articles = json.loads(my_articles_raw)
    return render_template("luna-theme/backend/articles/articles.html", articles = articles, my_articles = my_articles)

@app.route("/admin/articles/<article_id>/overview")
def admin_page_article_overview(article_id):
    return render_template("luna-theme/backend/dashboard.html")

@app.route("/admin/articles/<article_id>/notes")
def admin_page_article_notes(article_id):
    return render_template("luna-theme/backend/dashboard.html")

@app.route("/admin/articles/<article_id>/edit")
def admin_page_article_edit(article_id):
    article_raw = requests.get(secret.STRAPI_SERVER_ADDRESS + "/articles/" + article_id).content
    article_json = json.loads(article_raw)
    article = article_json['article_revisions'][0]
    return render_template("luna-theme/backend/dashboard.html", article = article)

@app.route("/admin/articles/<article_id>/history")
def admin_page_article_history(article_id):
    return render_template("luna-theme/backend/dashboard.html")

@app.route("/admin/podcasts")
def admin_page_podcasts():
    podcasts_raw = requests.get(secret.STRAPI_SERVER_ADDRESS + "/podcasts/").content
    podcasts = json.loads(podcasts_raw)
    return render_template("luna-theme/backend/podcast/podcasts.html", podcasts = podcasts)

@app.route("/admin/podcasts/<podcast_id>")
def admin_page_podcast_edit(podcast_id):
    return render_template("luna-theme/backend/dashboard.html")
    
@app.route("/admin/ads")
def admin_page_ads():
    return render_template("luna-theme/backend/dashboard.html")
    
@app.route("/admin/ads/<ad_id>")
def admin_page_ad_edit(ad_id):
    return render_template("luna-theme/backend/dashboard.html")
    
@app.route("/admin/preferences")
def admin_page_preferences():
    return render_template("luna-theme/backend/dashboard.html")
    
@app.route("/admin/staff")
def admin_page_staff():
    return render_template("luna-theme/backend/dashboard.html")
    
@app.route("/admin/staff/<user_id>")
def admin_page_staff_edit(user_id):
    return render_template("luna-theme/backend/dashboard.html")
    
@app.route("/admin/profile")
def admin_page_profile():
    return render_template("luna-theme/backend/dashboard.html")


# Public Api -----------------------------------------------------------------
@app.route("/public-api/ad-request", methods=['POST'])
def public_api_ad_request():
    content = request.json
    req = requests.post(secret.STRAPI_SERVER_ADDRESS + "/ad-requests", json = content)
    # req.
    return req.text
