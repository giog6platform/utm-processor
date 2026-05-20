"""
UTM Genius Web App
A G6 Platform tool. Flask app that rewrites HTML href links with UTM tracking parameters.
Deployable on Vercel or Render.
"""

from flask import Flask, render_template, request, jsonify, send_file
import re
import os
import json
import threading
import uuid
import time
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

DEFAULT_HISTORY_FILE = Path(__file__).resolve().parent / "data" / "history.json"
HISTORY_FILE = Path(os.environ.get("UTM_HISTORY_PATH", str(DEFAULT_HISTORY_FILE)))
HISTORY_LIMIT = 500

_options_lock = threading.Lock()
_history_lock = threading.Lock()


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


def load_history():
    with _history_lock:
        if not HISTORY_FILE.exists():
            return []
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except (OSError, json.JSONDecodeError) as e:
            logger.warning(f"Could not read history at {HISTORY_FILE}: {e}")
            return []


def _write_history(entries):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = HISTORY_FILE.with_suffix(HISTORY_FILE.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)
    os.replace(tmp, HISTORY_FILE)


def append_history(entry):
    with _history_lock:
        try:
            entries = []
            if HISTORY_FILE.exists():
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, list):
                        entries = loaded
            entries.append(entry)
            if len(entries) > HISTORY_LIMIT:
                entries = entries[-HISTORY_LIMIT:]
            _write_history(entries)
        except OSError as e:
            logger.warning(f"Could not write history to {HISTORY_FILE}: {e}")


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

        entry = {
            'id': uuid.uuid4().hex,
            'timestamp': int(time.time() * 1000),
            'base_url': base_url,
            'utm_params': utm_params,
            'utm_url': utm_url,
            'links_found': link_count,
            'filename': (data.get('filename') or '').strip() or None,
        }
        append_history(entry)

        return jsonify({
            'success': True,
            'processed_html': processed_html,
            'links_found': link_count,
            'utm_url': utm_url,
            'utm_params': utm_params,
            'history_entry': entry,
        })

    except Exception as e:
        logger.error(f"Error processing HTML: {str(e)}")
        return jsonify({'error': f'Processing error: {str(e)}'}), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    entries = load_history()
    entries = sorted(entries, key=lambda e: e.get('timestamp', 0), reverse=True)
    return jsonify({'entries': entries, 'limit': HISTORY_LIMIT})


@app.route('/api/history', methods=['DELETE'])
def clear_history():
    with _history_lock:
        try:
            _write_history([])
        except OSError as e:
            logger.warning(f"Could not clear history at {HISTORY_FILE}: {e}")
            return jsonify({'error': 'Could not clear history'}), 500
    return jsonify({'cleared': True})


@app.route('/api/history/<entry_id>', methods=['DELETE'])
def delete_history_entry(entry_id):
    with _history_lock:
        entries = []
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, list):
                        entries = loaded
            except (OSError, json.JSONDecodeError):
                entries = []
        kept = [e for e in entries if e.get('id') != entry_id]
        removed = len(kept) != len(entries)
        if removed:
            try:
                _write_history(kept)
            except OSError as e:
                logger.warning(f"Could not write history to {HISTORY_FILE}: {e}")
                return jsonify({'error': 'Could not update history'}), 500
    return jsonify({'removed': removed})


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
