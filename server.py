from flask import Flask, render_template, url_for, request, redirect, send_file
import csv
import requests
# import mongodb

app = Flask(__name__)


@app.route('/')
def my_home():
    return render_template('index.html')


@app.route('/<string:page_name>')
def html_page(page_name):
    return render_template(page_name)


def write_to_csv(data):
    with open('database.csv', newline='', mode='a') as database2:
        email = data["email"]
        subject = data["subject"]
        message = data["message"]
        csv_writer = csv.writer(database2, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([email, subject, message])
        notify(email, subject, message)


def notify(email, subject, data):
    """this function lets you get push notifications on your Phone"""
    server_name = 'Kaustubh43_WebsiteAlerts'
    data_received = f"You have received a query from {email} regarding {subject}"
    requests.post(f"https://ntfy.sh/{server_name}",
                  data=data_received,
                  headers={
                      "Title": "You have received a new Query! :)",
                      "Priority": "high",
                      "Tags": "tada"
                  })


@app.route('/submit_form', methods=['POST', 'GET'])
def submit_form():
    if request.method == 'POST':
        try:
            data = request.form.to_dict()
            write_to_csv(data)
            # mongodb.insert_into_mongoDB(data)  # Uncomment this when hosting to a new website hosting service
            return redirect('/thankyou.html')
        except:
            return 'did not save to database'
    else:
        return 'something went wrong. Try again!'


@app.route('/download')
def downloadFile():
    path = "./static/assets/docs/Kaustubh_Resume.pdf"
    return send_file(path, as_attachment=True)
