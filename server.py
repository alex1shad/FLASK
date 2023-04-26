from flask import Flask
from app.views import create_db, CreatorView, AdvertisementsView


create_db()

app = Flask('app')

app.add_url_rule('/creator/',
                 view_func=CreatorView.as_view('create_creator'),
                 methods=['POST'])

app.add_url_rule('/creator/<int:creator_id>/',
                 view_func=CreatorView.as_view('other_on_creator'),
                 methods=['GET', 'PATCH', 'DELETE'])

app.add_url_rule('/advertisement/',
                 view_func=AdvertisementsView.as_view('create_advertisement'),
                 methods=['POST'])

app.add_url_rule('/advertisement/<int:advertisement_id>/',
                 view_func=AdvertisementsView.as_view('other_on_advertisement'),
                 methods=['GET', 'PATCH', 'DELETE'])


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
