#!/usr/bin/env python3
"""
Social Media Downloader Pro
"""

from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import os
import uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuration
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/download', methods=['POST'])
def download():
    """Download endpoint"""
    data = request.get_json() or {}
    url = data.get('url', '').strip()
    platform = data.get('platform', 'auto')
    quality = data.get('quality', 'hd')
    
    if not url:
        return jsonify({'success': False, 'error': 'URL is required'}), 400
    
    # Auto-detect platform
    if platform == 'auto':
        if 'tiktok.com' in url:
            platform = 'tiktok'
        elif 'instagram.com' in url:
            platform = 'instagram'
        else:
            return jsonify({'success': False, 'error': 'Unsupported URL'}), 400
    
    try:
        if platform == 'tiktok':
            return handle_tiktok(url, quality)
        else:
            return jsonify({'success': False, 'error': 'Instagram not supported yet'}), 400
            
    except Exception as e:
        error_msg = str(e)
        print(f"Error: {error_msg}")
        return jsonify({'success': False, 'error': error_msg}), 500

def handle_tiktok(url, quality):
    """Handle TikTok downloads without yt-dlp first"""
    import urllib.request
    import json
    
    # Try using savetik API
    try:
        api_url = f"https://api.savetik.co/v1/fetch?url={urllib.parse.quote(url)}"
        
        req = urllib.request.Request(
            api_url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
            
            if data.get('success') and data.get('data', {}).get('play'):
                return jsonify({
                    'success': True,
                    'platform': 'tiktok',
                    'download_url': data['data']['play'],
                    'title': data['data'].get('title', 'TikTok Video'),
                    'author': data['data'].get('author', 'Unknown'),
                    'thumbnail': data['data'].get('cover', '')
                })
    except Exception as e:
        print(f"API error: {e}")
    
    # Fallback: return manual instructions
    return jsonify({
        'success': False,
        'error': 'Auto-download failed. Use manual method.',
        'manual_url': url,
        'instructions': 'Please use https://savetik.co or https://snaptik.app to download this video'
    }), 500

@app.route('/api/file/<filename>')
def serve_file(filename):
    """Serve file"""
    try:
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)