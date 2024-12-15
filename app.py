from flask import Flask ,request, render_template
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer

# #intializing a Tfidvectorizer
# vector = TfidfVectorizer(stop_words='english',max_df=0.7) 

# #loading the model
# model = pickle.load(open("model_name.pkl",'rb'))

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/main")
def about():
    return render_template("main.html")

# @app.route("/prediction", methods=['GET' , 'POST'])
# def prediction():
#     if request.method == "POST":
#         chatInput = request.form['chatInput']
#         predict = model.predict(vector.transform([chatInput]))
#         print(predict)
#         return render_template("main.html",prediction_text="News Headline is ->{}".format(predict))
#     else:
#         return render_template("main.html")


if __name__ == "__main__":
    app.run()


