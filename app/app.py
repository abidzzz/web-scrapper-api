from flask import Flask, request, jsonify
import asyncio
from scraper.scraper import search_amazon
import uuid
import threading

app = Flask(__name__)

tasks = {}

def scrape_task(task_id, search_text):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(search_amazon(search_text))
    tasks[task_id]['status'] = 'completed'
    tasks[task_id]['result'] = results
    tasks[task_id]['total_products'] = len(results)

@app.route('/')
async def root():
    url_list = [
        {'path': rule.rule, 'endpoint': rule.endpoint}
        for rule in app.url_map.iter_rules()
    ]
    return jsonify(url_list)

@app.route('/search')
async def search():
    search_text = request.args.get('q') # Query
    if not search_text:
        return jsonify({"error": "Missing query parameter"}), 400
    

    task_id = str(uuid.uuid4())
    tasks[task_id] = {'query':search_text,'status': 'processing', 'result': None, 'total_products':0}
    thread = threading.Thread(target=scrape_task, args=(task_id, search_text))
    thread.start()
    
    return jsonify({'task_id': task_id,
                    'url':f'{request.url_root}status/{task_id}',
                    'query':search_text})

@app.route('/status/<task_id>', methods=['GET'])
def status(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Invalid task ID"}), 404
    
    return jsonify(task)
    

if __name__ == '__main__':
    app.run(debug=True)