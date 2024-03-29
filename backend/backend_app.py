import json
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

app_dir = os.path.dirname(os.path.abspath(__file__))
storage_dir_path = os.path.join(app_dir, 'storage')
data_filename = os.path.join(storage_dir_path, 'data.json')

def get_data():
    with open(data_filename, 'r') as file:
        data = json.loads(file.read())
    return data

def save_to_json(filename, data):
    json_str = json.dumps(data)
    with open(filename, 'w') as file:
        file.write(json_str)


POSTS = get_data()

@app.route('/api/posts', methods=['GET'])
def get_posts():
    return jsonify(POSTS)

@app.errorhandler(400)
def bad_request():
    return f"error: Data is invalid!", 400

@app.errorhandler(404)
def not_found():
    return f"error: Data is not found!", 404

@app.route('/api/posts', methods=['POST'])
def add_post():
    # Retrieve the data from the request body
    data = request.get_json()
    """POST
    note: from postman, paste the url - 
    From Headers: input key="Content-", value="application/json"
    From Body: raw/JSON - create form {
    "title": "Your Post Title",
    "content": "Your Post Content" } ----- SEND
    """
    # Check if 'title' and 'content' are provided in the request body
    if 'title' in data and 'content' in data:
        title = data['title']
        content = data['content']
        author = data['author']
        date = data['date']
        formatted_date = datetime.strptime(date, "%Y-%m-%d")
        # Create a new post with a generated ID
        new_post = {
            'id': len(POSTS) + 1,
            'title': title,
            'content': content,
            'author': author,
            'date': formatted_date
        }
        POSTS.append(new_post)

        save_to_json(data_filename, POSTS)

        return jsonify(new_post), 201
    else:
        return bad_request(400)


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    for line in POSTS:
        if int(line['id']) == post_id:
            POSTS.remove(line)
            result = {"message": f"Post with id {post_id} has been deleted successfully."}
            return jsonify(result), 200

    result = not_found(404)
    return jsonify(result), 404

@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def input_post(post_id):
    data = request.get_json()
    new_title = data.get('title')
    new_content = data.get('content')
    new_author = data.get('author')
    new_date = data.get('date')
    formatted_new_date = datetime.strptime(new_date, "%Y-%m-%d")
    for line in POSTS:
        if int(line['id']) == post_id:
            line['title'] = new_title
            line['content'] = new_content
            line['author'] = new_author
            line['date'] = formatted_new_date
            result = {"message": f"Post with id {post_id} has been updated successfully."}
            return jsonify(result), 200
    result = not_found(404)
    return jsonify(result), 404

@app.route('/api/posts/search/<key_search>', methods=['GET'])
def search_post(key_search):
    search_title = request.args.get(key_search)
    if search_title:
        search_list = []
        for line in POSTS:
            if search_title in line[key_search]:
                search_list.append(line)

        if search_list:
            return jsonify(search_list), 200
        else:
            result = {"message": "Title not found"}
            return jsonify(result), 404

    result = {"message": f"{search_title} not provided"}
    return jsonify(result), 400

@app.route('/api/posts/<key_sort>', methods=['GET'])
def sort_post(key_sort):
    sort_key = request.args.get(key_sort)
    sort_direction = request.args.get('direction')

    if sort_key and sort_direction and (sort_direction.lower() in ['asc', 'desc']):
        if sort_key in ['title', 'content', 'author', 'date']:
            if sort_direction.lower() == 'desc':
                sorted_posts = sorted(POSTS, key=lambda x: x[sort_key], reverse=True)
            else:
                sorted_posts = sorted(POSTS, key=lambda x: x[sort_key])

            return jsonify(sorted_posts), 200

    result = not_found(404)
    return jsonify(result), 404


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5007, debug=True)
