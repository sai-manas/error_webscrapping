from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import logging
from pymongo.mongo_client import MongoClient

logging.basicConfig(filename="/config/workspace/pw_eng_webscrap/scrapper.log" , level=logging.INFO)

app = Flask(__name__)

@app.route("/", methods = ['GET'])
@cross_origin()
def homepage():
    return render_template("index.html")

@app.route("/review",methods = ['POST','GET'])
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchstring = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchstring
            url_client = urlopen(flipkart_url)
            flipkart_raw_html = url_client.read()
            url_client.close()
            flipkart_html = bs(flipkart_raw_html,"html.parser")
            allboxes = flipkart_html.findAll("div",{"class": "_1AtVbE col-12-12"})
            del allboxes[0:2]
            box = allboxes[0]
            productlink = "https://www.flipkart.com" + box.div.div.div.a['href']
            productreq = requests.get(productlink)
            productreq.encoding = 'utf-8'
            prod_html = bs(productreq.text,'html.parser')
            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})

           
            reviews = []

            for commentbox in commentboxes:
                try:
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                except:
                    logging.info("name")

                try:
                    rating = commentbox.div.div.div.div.text

                except:
                    rating = 'No Rating'
                    logging.info("rating")

                try:
                    commentHead = commentbox.div.div.div.p.text

                except:
                    commentHead = 'No Comment Heading'
                    logging.info(commentHead)
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    custComment = comtag[0].div.text
                except Exception as e:
                    logging.info(e)
                    
                mydict = {"Product": searchstring, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)
            logging.info("log my final result {}".format(reviews))

            uri = "mongodb+srv://saimanas:saimanas@cluster0.ohitfzf.mongodb.net/?retryWrites=true&w=majority"
            # Create a new client and connect to the server
            client = MongoClient(uri)
            db=client['web_scrapper']
            coll_pw_eng=db['scraper_flipkart']
            coll_pw_eng.insert_many(reviews)
            

            return render_template('result.html',reviews = reviews[0:(len(reviews)-1)])
            
        except Exception as e:
            logging.info(e)
            return "something is wrong"

    else:
        render_template("index.html")

if __name__=="__main__":
    app.run(host="0.0.0.0")
