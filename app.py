"""
UTM Agent Web App
Simple Flask app to process HTML with UTM parameters
Deployable on Vercel or Render
"""

from flask import Flask, render_template, request, jsonify, send_file
import re
import os
import json
import threading
from pathlib import Path
from urllib.parse import urlencode
from io import BytesIO
import logging

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

VALID_FIELDS = ("utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content")
VALUE_PATTERN = re.compile(r"^[A-Za-z0-9_.\- ]+$")
MAX_VALUE_LEN = 100

DEFAULT_DATA_FILE = Path(__file__).resolve().parent / "data" / "options.json"
DATA_FILE = Path(os.environ.get("UTM_OPTIONS_PATH", str(DEFAULT_DATA_FILE)))

_options_lock = threading.Lock()


def _seed_options():
    """Read the bundled default options.json (shipped with the app)."""
    with open(DEFAULT_DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_options():
    with _options_lock:
        if not DATA_FILE.exists():
            data = _seed_options()
            try:
                DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
                with open(DATA_FILE, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
            except OSError as e:
                logger.warning(f"Could not write seed options to {DATA_FILE}: {e}")
            return data
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)


def save_options(data):
    with _options_lock:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = DATA_FILE.with_suffix(DATA_FILE.suffix + ".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, DATA_FILE)


def build_utm_url(base_url, utm_params):
    """Build UTM-tagged URL."""
    filtered_params = {k: v for k, v in utm_params.items() if v}

    if not filtered_params:
        return base_url

    separator = "&" if "?" in base_url else "?"
    query_string = urlencode(filtered_params)

    return f"{base_url}{separator}{query_string}"


def inject_utm_in_html(html_content, utm_url):
    """Replace all href links in HTML with UTM URL."""
    if not html_content:
        return ""

    def replace_href(match):
        quote_char = match.group(1) or match.group(3) or ""
        return f'href={quote_char}{utm_url}{quote_char}'

    pattern = r'href=(["\'])([^"\']*)["\']|href=([^\s>]*)'

    return re.sub(pattern, replace_href, html_content, flags=re.IGNORECASE)


def count_links(html_content):
    """Count how many links were found in HTML."""
    pattern = r'href=(["\'])([^"\']*)["\']|href=([^\s>]*)'
    matches = re.findall(pattern, html_content, re.IGNORECASE)
    return len(matches)


@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')


@app.route('/api/options', methods=['GET'])
def get_options():
    return jsonify(load_options())


@app.route('/api/options/<field>', methods=['POST'])
def add_option(field):
    if field not in VALID_FIELDS:
        return jsonify({'error': 'Invalid field'}), 400

    data = request.get_json(silent=True) or {}
    value = (data.get('value') or '').strip()

    if not value:
        return jsonify({'error': 'Value is required'}), 400
    if len(value) > MAX_VALUE_LEN:
        return jsonify({'error': f'Value must be {MAX_VALUE_LEN} characters or fewer'}), 400
    if not VALUE_PATTERN.match(value):
        return jsonify({'error': 'Use letters, digits, underscores, hyphens, dots, or spaces only'}), 400

    options = load_options()
    field_options = options.get(field, [])
    added = value not in field_options
    if added:
        field_options.append(value)
        options[field] = field_options
        save_options(options)
        logger.info(f"Added option to {field}: {value}")

    return jsonify({'options': field_options, 'added': added})


@app.route('/api/options/<field>', methods=['DELETE'])
def delete_option(field):
    if field not in VALID_FIELDS:
        return jsonify({'error': 'Invalid field'}), 400

    data = request.get_json(silent=True) or {}
    value = (data.get('value') or '').strip()

    if not value:
        return jsonify({'error': 'Value is required'}), 400

    options = load_options()
    field_options = options.get(field, [])
    removed = value in field_options
    if removed:
        field_options = [v for v in field_options if v != value]
        options[field] = field_options
        save_options(options)
        logger.info(f"Removed option from {field}: {value}")

    return jsonify({'options': field_options, 'removed': removed})


@app.route('/api/process', methods=['POST'])
def process_html():
    """Process HTML with UTM parameters."""
    try:
        data = request.json

        html_content = data.get('html', '').strip()
        base_url = data.get('base_url', '').strip()

        if not html_content:
            return jsonify({'error': 'HTML content is required'}), 400

        if not base_url:
            return jsonify({'error': 'Base URL is required'}), 400

        utm_params = {
            'utm_source': data.get('utm_source', '').strip(),
            'utm_medium': data.get('utm_medium', '').strip(),
            'utm_campaign': data.get('utm_campaign', '').strip(),
            'utm_term': data.get('utm_term', '').strip(),
            'utm_content': data.get('utm_content', '').strip(),
        }

        utm_url = build_utm_url(base_url, utm_params)
        link_count = count_links(html_content)
        processed_html = inject_utm_in_html(html_content, utm_url)

        logger.info(f"Processed HTML: {link_count} links found, UTM source: {utm_params.get('utm_source')}")

        return jsonify({
            'success': True,
            'processed_html': processed_html,
            'links_found': link_count,
            'utm_url': utm_url,
            'utm_params': utm_params
        })

    except Exception as e:
        logger.error(f"Error processing HTML: {str(e)}")
        return jsonify({'error': f'Processing error: {str(e)}'}), 500


@app.route('/api/download', methods=['POST'])
def download_file():
    """Download processed HTML as file."""
    try:
        data = request.json
        html_content = data.get('html', '')
        filename = data.get('filename', 'processed.html').strip()

        filename = re.sub(r'[^\w\-\.]', '', filename)
        if not filename.endswith('.html'):
            filename += '.html'

        file_bytes = BytesIO(html_content.encode('utf-8'))

        return send_file(
            file_bytes,
            mimetype='text/html',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        return jsonify({'error': f'Download error: {str(e)}'}), 500


@app.route('/health')
def health():
    """Health check for Vercel."""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(debug=False, port=5000)
