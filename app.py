from flask import Flask

app = Flask(__name__)
app.secret = "dasf34sfkjfldskfa9usafkj0898fsdafdsaf"

@app.route('/')
def index():
    return 'Hello World'

@app.route('/<page>')
def main(page):
    return page

if __name__ == "__main__":
    app.run(debug=True, port=9000)
