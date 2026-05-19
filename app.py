"""
UTM Processor Web App
Simple Flask app to process HTML with UTM parameters
Deployable on Vercel
"""

from flask import Flask, render_template, request, jsonify, send_file
import re
from urllib.parse import urlencode
from io import BytesIO
import logging

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def build_utm_url(base_url, utm_params):
    """Build UTM-tagged URL."""
    # Filter out empty values
    filtered_params = {k: v for k, v in utm_params.items() if v}
    
    if not filtered_params:
        return base_url
    
    # Add ? or & depending on if URL already has params
    separator = "&" if "?" in base_url else "?"
    query_string = urlencode(filtered_params)
    
    return f"{base_url}{separator}{query_string}"


def inject_utm_in_html(html_content, utm_url):
    """Replace all href links in HTML with UTM URL."""
    if not html_content:
        return ""
    
    # Pattern to match href="...", href='...', href=...
    def replace_href(match):
        quote_char = match.group(1) or match.group(3) or ""
        return f'href={quote_char}{utm_url}{quote_char}'
    
    # Match href with double quotes, single quotes, or no quotes
    pattern = r'href=(["\'])([^"\']*)["\']|href=([^\s>]*)'
    
    modified_html = re.sub(pattern, replace_href, html_content, flags=re.IGNORECASE)
    
    return modified_html


def count_links(html_content):
    """Count how many links were found in HTML."""
    pattern = r'href=(["\'])([^"\']*)["\']|href=([^\s>]*)'
    matches = re.findall(pattern, html_content, re.IGNORECASE)
    return len(matches)


@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')


@app.route('/api/process', methods=['POST'])
def process_html():
    """Process HTML with UTM parameters."""
    try:
        data = request.json
        
        # Validate required fields
        html_content = data.get('html', '').strip()
        base_url = data.get('base_url', '').strip()
        
        if not html_content:
            return jsonify({'error': 'HTML content is required'}), 400
        
        if not base_url:
            return jsonify({'error': 'Base URL is required'}), 400
        
        # Build UTM parameters
        utm_params = {
            'utm_source': data.get('utm_source', '').strip(),
            'utm_medium': data.get('utm_medium', '').strip(),
            'utm_campaign': data.get('utm_campaign', '').strip(),
            'utm_term': data.get('utm_term', '').strip(),
            'utm_content': data.get('utm_content', '').strip(),
        }
        
        # Build UTM URL
        utm_url = build_utm_url(base_url, utm_params)
        
        # Count links before processing
        link_count = count_links(html_content)
        
        # Process HTML
        processed_html = inject_utm_in_html(html_content, utm_url)
        
        # Log success
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
        
        # Sanitize filename
        filename = re.sub(r'[^\w\-\.]', '', filename)
        if not filename.endswith('.html'):
            filename += '.html'
        
        # Create file
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
