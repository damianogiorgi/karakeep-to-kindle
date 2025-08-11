#!/usr/bin/env python3
"""
Kindle Bookmarks Script
Retrieves articles from Karakeep, converts to PDF/EPUB, sends to Kindle, and archives articles.
"""

import requests
import json
import smtplib
import os
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
import argparse
from pathlib import Path
import logging
import re
import base64
from urllib.parse import urlparse
import mimetypes

# Configuration
CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "karakeep": {
        "api_url": "https://bookmarks.damianogiorgi.it/api/v1",
        "api_key": ""
    },
    "kindle": {
        "email": "",
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "smtp_user": "",
        "smtp_password": ""
    },
    "output": {
        "format": "pdf",  # pdf or epub
        "output_dir": "./output"
    }
}

class KindleBookmarksProcessor:
    def __init__(self, config_path=CONFIG_FILE):
        self.config = self.load_config(config_path)
        self.setup_logging()
        # Class-level image cache to avoid downloading the same image multiple times
        self.image_cache = {}
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('kindle_bookmarks.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_config(self, config_path):
        """Load configuration from JSON file"""
        if not os.path.exists(config_path):
            self.create_default_config(config_path)
            print(f"Created default config file: {config_path}")
            print("Please edit the config file with your settings and run again.")
            sys.exit(1)
        
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def create_default_config(self, config_path):
        """Create default configuration file"""
        with open(config_path, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
    
    def get_unarchived_articles(self):
        """Retrieve unarchived articles from Karakeep, sorted newest to oldest"""
        headers = {
            'Authorization': f'Bearer {self.config["karakeep"]["api_key"]}',
            'Content-Type': 'application/json'
        }
        
        # Use API's built-in sorting - desc for newest first
        params = {
            'sortOrder': 'desc'
        }
        
        try:
            response = requests.get(
                f'{self.config["karakeep"]["api_url"]}/bookmarks',
                headers=headers,
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            # Filter for unarchived articles (API sorting is preserved)
            unarchived = [article for article in data.get('bookmarks', []) if not article.get('archived', False)]
            
            self.logger.info(f"Found {len(unarchived)} unarchived articles (sorted newest to oldest)")
            return unarchived
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching articles: {e}")
            return []
    
    def convert_to_document(self, article, format_type="html"):
        """Convert article to requested format (HTML first, then convert)"""
        output_dir = Path(self.config["output"]["output_dir"])
        output_dir.mkdir(exist_ok=True)
        
        # Always create HTML first
        html_content = self.create_html_content(article)
        
        # Generate descriptive and safe filename
        content = article.get('content', {})
        title = content.get('title', 'Untitled Article')
        author = content.get('author', '')
        publisher = content.get('publisher', '')
        
        # Create a nice filename with author and publisher if available
        filename_parts = []
        
        # Clean and truncate title
        clean_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_', '.')).strip()
        clean_title = re.sub(r'\s+', ' ', clean_title)  # Normalize whitespace
        filename_parts.append(clean_title[:60])  # Longer title limit
        
        # Add author if available
        if author and author != 'Unknown Author':
            clean_author = "".join(c for c in author if c.isalnum() or c in (' ', '-', '_')).strip()
            clean_author = re.sub(r'\s+', ' ', clean_author)
            if clean_author:
                filename_parts.append(f"by {clean_author[:30]}")
        
        # Add publisher if available and different from author
        if publisher and publisher != author:
            clean_publisher = "".join(c for c in publisher if c.isalnum() or c in (' ', '-', '_')).strip()
            clean_publisher = re.sub(r'\s+', ' ', clean_publisher)
            if clean_publisher and len(clean_publisher) > 2:
                filename_parts.append(f"({clean_publisher[:25]})")
        
        # Combine parts
        safe_title = " - ".join(filename_parts)
        
        # Final cleanup and length check
        safe_title = safe_title[:120]  # Reasonable filename length limit
        
        # Save HTML file
        html_filepath = self.save_as_html(html_content, safe_title, output_dir)
        
        # Convert to requested format if not HTML
        if format_type.lower() == "pdf":
            return self.convert_html_to_pdf(html_filepath)
        elif format_type.lower() == "epub":
            return self.convert_html_to_epub(html_filepath)
        elif format_type.lower() == "mobi":
            return self.convert_html_to_mobi(html_filepath)
        else:
            return html_filepath
    
    def download_image(self, url, asset_id=None):
        """Download image from URL or Karakeep asset and return base64 data"""
        # Create cache key - prefer asset_id if available, otherwise use URL
        cache_key = asset_id if asset_id else url
        
        # Check class-level cache first
        if cache_key in self.image_cache:
            self.logger.debug(f"Using cached image: {cache_key}")
            return self.image_cache[cache_key]
        
        try:
            headers = {
                'Authorization': f'Bearer {self.config["karakeep"]["api_key"]}',
                'User-Agent': 'Mozilla/5.0 (compatible; KindleBookmarks/1.0)'
            }
            
            # Try Karakeep asset first if asset_id is provided
            if asset_id:
                try:
                    asset_url = f'{self.config["karakeep"]["api_url"]}/assets/{asset_id}'
                    response = requests.get(asset_url, headers=headers, timeout=15)
                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', 'image/jpeg')
                        # Limit image size to avoid huge files (max 5MB)
                        if len(response.content) > 5 * 1024 * 1024:
                            self.logger.warning(f"Karakeep asset {asset_id} too large ({len(response.content)} bytes), skipping")
                            self.image_cache[cache_key] = None
                            return None
                        image_data = base64.b64encode(response.content).decode('utf-8')
                        result = f"data:{content_type};base64,{image_data}"
                        self.image_cache[cache_key] = result
                        self.logger.info(f"Downloaded Karakeep asset: {asset_id} ({len(response.content)} bytes)")
                        return result
                except Exception as e:
                    self.logger.warning(f"Failed to download Karakeep asset {asset_id}: {e}")
            
            # Fallback to external URL
            if url:
                response = requests.get(url, headers={'User-Agent': headers['User-Agent']}, timeout=15)
                response.raise_for_status()
                
                # Limit image size to avoid huge files (max 5MB)
                if len(response.content) > 5 * 1024 * 1024:
                    self.logger.warning(f"External image {url} too large ({len(response.content)} bytes), skipping")
                    self.image_cache[cache_key] = None
                    return None
                
                # Determine content type
                content_type = response.headers.get('content-type')
                if not content_type or not content_type.startswith('image/'):
                    # Try to guess from URL extension
                    parsed_url = urlparse(url)
                    content_type, _ = mimetypes.guess_type(parsed_url.path)
                    if not content_type or not content_type.startswith('image/'):
                        content_type = 'image/jpeg'  # Default fallback
                
                image_data = base64.b64encode(response.content).decode('utf-8')
                result = f"data:{content_type};base64,{image_data}"
                self.image_cache[cache_key] = result
                self.logger.info(f"Downloaded external image: {url} ({len(response.content)} bytes)")
                return result
                
        except Exception as e:
            self.logger.warning(f"Failed to download image {url}: {e}")
            self.image_cache[cache_key] = None
            return None
    
    def process_images_in_html(self, html_content, article):
        """Process and embed images in HTML content"""
        if not html_content:
            return html_content
        
        # Find all img tags
        img_pattern = r'<img[^>]*src=["\']([^"\']+)["\'][^>]*>'
        
        def replace_image(match):
            img_tag = match.group(0)
            img_url = match.group(1)
            
            # Skip if already a data URL
            if img_url.startswith('data:'):
                return img_tag
            
            # Download the image using only the URL (no asset_id confusion)
            # The download_image method will handle caching properly
            embedded_url = self.download_image(img_url, asset_id=None)
            
            if embedded_url:
                # Replace the src attribute with the embedded data
                new_img_tag = re.sub(r'src=["\'][^"\']+["\']', f'src="{embedded_url}"', img_tag)
                return new_img_tag
            else:
                # Keep original if download failed
                return img_tag
        
        # Process all images
        processed_html = re.sub(img_pattern, replace_image, html_content)
        
        return processed_html
    
    def create_html_content(self, article):
        """Create HTML content from article data with embedded images"""
        content = article.get('content', {})
        title = content.get('title', 'Untitled Article')
        author = content.get('author', 'Unknown Author')
        publisher = content.get('publisher', '')
        html_content = content.get('htmlContent', '')
        url = content.get('url', '')
        
        # Process and embed images
        self.logger.info("Processing images for embedding...")
        processed_html_content = self.process_images_in_html(html_content, article)
        
        html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; max-width: 800px; }}
        h1 {{ color: #333; border-bottom: 2px solid #333; }}
        .meta {{ color: #666; font-style: italic; margin-bottom: 20px; }}
        .content {{ margin-top: 20px; }}
        .main-image {{ text-align: center; margin: 20px 0; }}
        img {{ max-width: 100%; height: auto; display: block; margin: 10px auto; }}
        a {{ color: #0066cc; }}
        figure {{ margin: 20px 0; text-align: center; }}
        figcaption {{ font-style: italic; color: #666; margin-top: 5px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        blockquote {{ border-left: 4px solid #ccc; margin: 20px 0; padding-left: 20px; font-style: italic; }}
        pre {{ background-color: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        code {{ background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="meta">
        <p><strong>Author:</strong> {author}</p>
        <p><strong>Publisher:</strong> {publisher}</p>
        <p><strong>Source:</strong> <a href="{url}">{url}</a></p>
        <p><strong>Retrieved:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    <div class="content">
        {processed_html_content}
    </div>
</body>
</html>"""
        return html_template
    
    def convert_html_to_pdf(self, html_filepath):
        """Convert existing HTML file to PDF using weasyprint"""
        try:
            from weasyprint import HTML
            
            pdf_filepath = html_filepath.with_suffix('.pdf')
            HTML(filename=str(html_filepath)).write_pdf(pdf_filepath)
            self.logger.info(f"Converted HTML to PDF: {pdf_filepath.name}")
            return pdf_filepath
            
        except ImportError:
            self.logger.warning("weasyprint not available, cannot convert to PDF")
            return html_filepath
        except Exception as e:
            self.logger.error(f"Error converting HTML to PDF: {e}")
            return html_filepath
    
    def convert_html_to_epub(self, html_filepath):
        """Convert existing HTML file to EPUB using ebooklib"""
        try:
            from ebooklib import epub
            
            # Read the HTML content
            with open(html_filepath, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Extract title from HTML
            title_match = re.search(r'<title>(.*?)</title>', html_content)
            title = title_match.group(1) if title_match else html_filepath.stem
            
            # Create EPUB
            book = epub.EpubBook()
            book.set_identifier(f'karakeep_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
            book.set_title(title)
            book.set_language('en')
            
            # Create chapter from HTML
            chapter = epub.EpubHtml(title=title, file_name='article.xhtml', lang='en')
            chapter.content = html_content
            book.add_item(chapter)
            
            # Add navigation
            book.toc = (epub.Link("article.xhtml", title, "article"),)
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())
            
            # Create spine
            book.spine = ['nav', chapter]
            
            # Generate EPUB file
            epub_filepath = html_filepath.with_suffix('.epub')
            epub.write_epub(str(epub_filepath), book, {})
            self.logger.info(f"Converted HTML to EPUB: {epub_filepath.name}")
            return epub_filepath
            
        except ImportError:
            self.logger.warning("ebooklib not available, cannot convert to EPUB")
            return html_filepath
        except Exception as e:
            self.logger.error(f"Error converting HTML to EPUB: {e}")
            return html_filepath
    
    def convert_html_to_mobi(self, html_filepath):
        """Convert existing HTML file to MOBI using kindlegen or ebook-convert"""
        try:
            import subprocess
            
            mobi_filepath = html_filepath.with_suffix('.mobi')
            
            # Try ebook-convert from Calibre first (more reliable)
            try:
                result = subprocess.run([
                    'ebook-convert', 
                    str(html_filepath), 
                    str(mobi_filepath),
                    '--output-profile', 'kindle',
                    '--mobi-file-type', 'new'
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    self.logger.info(f"Converted HTML to MOBI using ebook-convert: {mobi_filepath.name}")
                    return mobi_filepath
                else:
                    self.logger.warning(f"ebook-convert failed: {result.stderr}")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                self.logger.warning("ebook-convert not available or timed out")
            
            # Fallback to kindlegen (deprecated but might still work)
            try:
                result = subprocess.run([
                    'kindlegen', 
                    str(html_filepath),
                    '-o', mobi_filepath.name
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode in [0, 1]:  # kindlegen returns 1 for warnings
                    self.logger.info(f"Converted HTML to MOBI using kindlegen: {mobi_filepath.name}")
                    return mobi_filepath
                else:
                    self.logger.warning(f"kindlegen failed: {result.stderr}")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                self.logger.warning("kindlegen not available or timed out")
            
            # If both fail, try converting via EPUB first
            self.logger.info("Trying MOBI conversion via EPUB...")
            epub_filepath = self.convert_html_to_epub(html_filepath)
            if epub_filepath != html_filepath:
                try:
                    result = subprocess.run([
                        'ebook-convert', 
                        str(epub_filepath), 
                        str(mobi_filepath),
                        '--output-profile', 'kindle'
                    ], capture_output=True, text=True, timeout=300)
                    
                    if result.returncode == 0:
                        self.logger.info(f"Converted EPUB to MOBI: {mobi_filepath.name}")
                        # Clean up intermediate EPUB
                        epub_filepath.unlink()
                        return mobi_filepath
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass
            
            self.logger.warning("All MOBI conversion methods failed, returning HTML")
            return html_filepath
            
        except Exception as e:
            self.logger.error(f"Error converting HTML to MOBI: {e}")
            return html_filepath
    

    
    def create_compilation_epub(self, articles, output_dir):
        """Create a single EPUB with all articles as chapters (HTML-first approach)"""
        # First create HTML compilation
        html_filepath = self.create_compilation_html(articles, output_dir)
        
        # Then convert to EPUB
        return self.convert_html_to_epub(html_filepath)
    
    def create_compilation_pdf(self, articles, output_dir):
        """Create a single PDF with all articles (HTML-first approach)"""
        # First create HTML compilation
        html_filepath = self.create_compilation_html(articles, output_dir)
        
        # Then convert to PDF
        return self.convert_html_to_pdf(html_filepath)
    
    def create_compilation_mobi(self, articles, output_dir):
        """Create a single MOBI with all articles (HTML-first approach)"""
        # First create HTML compilation
        html_filepath = self.create_compilation_html(articles, output_dir)
        
        # Then convert to MOBI
        return self.convert_html_to_mobi(html_filepath)
    
    def create_compilation_html(self, articles, output_dir):
        """Create a single HTML file with all articles (fallback)"""
        self.logger.info(f"Creating compilation HTML with {len(articles)} articles...")
        
        html_parts = []
        html_parts.append("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Karakeep Articles Collection</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 40px;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
        }
        .cover {
            text-align: center;
            margin-bottom: 3em;
            padding: 2em;
            border-bottom: 3px solid #333;
        }
        .cover h1 {
            font-size: 2.5em;
            color: #333;
            margin-bottom: 0.5em;
        }
        .cover p {
            color: #666;
            font-size: 1.1em;
        }
        .article {
            margin-bottom: 3em;
            padding-bottom: 2em;
            border-bottom: 1px solid #eee;
        }
        .article-title {
            font-size: 1.8em;
            color: #333;
            border-bottom: 2px solid #333;
            padding-bottom: 0.5em;
            margin-bottom: 1em;
        }
        .article-meta {
            background-color: #f9f9f9;
            padding: 1em;
            margin-bottom: 1.5em;
            border-left: 4px solid #ccc;
            color: #666;
        }
        .article-content {
            margin-top: 1em;
        }
        img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1em auto;
        }
        figure {
            margin: 1.5em 0;
            text-align: center;
        }
        figcaption {
            font-style: italic;
            color: #666;
            margin-top: 0.5em;
        }
        blockquote {
            border-left: 4px solid #ccc;
            margin: 1.5em 0;
            padding-left: 1em;
            font-style: italic;
        }
        pre {
            background-color: #f4f4f4;
            padding: 1em;
            border-radius: 5px;
            overflow-x: auto;
        }
        code {
            background-color: #f4f4f4;
            padding: 0.2em 0.4em;
            border-radius: 3px;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 0.5em;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        .toc {
            background-color: #f9f9f9;
            padding: 1.5em;
            margin-bottom: 2em;
            border-radius: 5px;
        }
        .toc h2 {
            margin-top: 0;
            color: #333;
        }
        .toc ul {
            list-style-type: none;
            padding-left: 0;
        }
        .toc li {
            margin-bottom: 0.5em;
        }
        .toc a {
            color: #0066cc;
            text-decoration: none;
        }
        .toc a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="cover">
        <h1>Karakeep Articles</h1>
        <p>Collection of saved articles</p>
        <p>Generated on """ + datetime.now().strftime('%B %d, %Y') + """</p>
        <p>""" + str(len(articles)) + """ articles</p>
    </div>
    
    <div class="toc">
        <h2>Table of Contents</h2>
        <ul>""")
        
        # Add table of contents
        for i, article in enumerate(articles, 1):
            title = article.get('content', {}).get('title', f'Article {i}')
            html_parts.append(f'            <li><a href="#article-{i}">{i}. {title}</a></li>')
        
        html_parts.append("""        </ul>
    </div>
""")
        
        # Add articles
        for i, article in enumerate(articles, 1):
            content = article.get('content', {})
            title = content.get('title', f'Article {i}')
            author = content.get('author', 'Unknown Author')
            publisher = content.get('publisher', '')
            url = content.get('url', '')
            
            self.logger.info(f"Processing article {i}/{len(articles)}: {title[:50]}...")
            
            # Process images for this article
            html_content = content.get('htmlContent', '')
            processed_html_content = self.process_images_in_html(html_content, article)
            
            html_parts.append(f"""
    <div class="article" id="article-{i}">
        <h1 class="article-title">{title}</h1>
        <div class="article-meta">
            <p><strong>Author:</strong> {author}</p>
            <p><strong>Publisher:</strong> {publisher}</p>
            <p><strong>Source:</strong> <a href="{url}">{url}</a></p>
        </div>
        <div class="article-content">
            {processed_html_content}
        </div>
    </div>
""")
        
        html_parts.append("</body></html>")
        
        # Combine all HTML
        full_html = "".join(html_parts)
        
        # Generate descriptive filename
        date_str = datetime.now().strftime('%Y-%m-%d')
        time_str = datetime.now().strftime('%H%M')
        article_count = len(articles)
        
        # Create a nice compilation filename
        filename = f"Karakeep {date_str} at {time_str} - {article_count} Articles -.html"
        filepath = output_dir / filename
        
        # Write HTML file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        self.logger.info(f"Created compilation HTML: {filepath} ({len(articles)} articles)")
        return filepath
    
    def save_as_html(self, html_content, title, output_dir):
        """Save content as HTML file (fallback)"""
        filename = f"{title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"Created HTML file: {filepath}")
        return filepath
    
    def send_to_kindle(self, filepath):
        """Send document to Kindle via email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config["kindle"]["smtp_user"]
            msg['To'] = self.config["kindle"]["email"]
            msg['Subject'] = f"Article from Karakeep - {filepath.stem}"
            
            # Add body
            body = "Article sent from Karakeep to Kindle converter"
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachment
            with open(filepath, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {filepath.name}'
            )
            msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(self.config["kindle"]["smtp_server"], self.config["kindle"]["smtp_port"])
            server.starttls()
            server.login(self.config["kindle"]["smtp_user"], self.config["kindle"]["smtp_password"])
            text = msg.as_string()
            server.sendmail(self.config["kindle"]["smtp_user"], self.config["kindle"]["email"], text)
            server.quit()
            
            self.logger.info(f"Successfully sent {filepath.name} to Kindle")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending to Kindle: {e}")
            return False
    
    def archive_article(self, article_id):
        """Archive article in Karakeep"""
        headers = {
            'Authorization': f'Bearer {self.config["karakeep"]["api_key"]}',
            'Content-Type': 'application/json'
        }
        
        try:
            # Update article to set archived=true
            response = requests.patch(
                f'{self.config["karakeep"]["api_url"]}/bookmarks/{article_id}',
                headers=headers,
                json={'archived': True}
            )
            response.raise_for_status()
            
            self.logger.info(f"Successfully archived article {article_id}")
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error archiving article {article_id}: {e}")
            return False
    
    def cleanup_file(self, filepath):
        """Delete a single file with error handling"""
        try:
            if filepath and filepath.exists():
                filepath.unlink()
                self.logger.info(f"Cleaned up file: {filepath.name}")
                return True
            return False
        except Exception as e:
            self.logger.warning(f"Failed to cleanup file {filepath}: {e}")
            return False
    
    def cleanup_output_directory(self, keep_recent=False):
        """Clean up all files in output directory"""
        try:
            output_dir = Path(self.config["output"]["output_dir"])
            if not output_dir.exists():
                return 0
            
            cleaned_count = 0
            current_time = datetime.now()
            
            for file_path in output_dir.glob("*"):
                if file_path.is_file():
                    # If keep_recent is True, only delete files older than 1 hour
                    if keep_recent:
                        file_age = current_time.timestamp() - file_path.stat().st_mtime
                        if file_age < 3600:  # Less than 1 hour old
                            continue
                    
                    if self.cleanup_file(file_path):
                        cleaned_count += 1
            
            if cleaned_count > 0:
                self.logger.info(f"Cleaned up {cleaned_count} files from output directory")
            
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            return 0
    
    def process_articles(self, dry_run=False, compilation_mode=False, cleanup_files=False):
        """Main processing function"""
        self.logger.info("Starting article processing...")
        
        # Get unarchived articles
        articles = self.get_unarchived_articles()
        
        if not articles:
            self.logger.info("No unarchived articles found")
            return
        
        if compilation_mode:
            self.logger.info(f"COMPILATION MODE: Creating single document with {len(articles)} articles")
            
            if dry_run:
                self.logger.info(f"DRY RUN: Would create compilation document with {len(articles)} articles")
                return
            
            try:
                output_dir = Path(self.config["output"]["output_dir"])
                output_dir.mkdir(exist_ok=True)
                
                # Create compilation document based on format
                format_type = self.config["output"]["format"].lower()
                
                if format_type == "pdf":
                    filepath = self.create_compilation_pdf(articles, output_dir)
                elif format_type == "epub":
                    filepath = self.create_compilation_epub(articles, output_dir)
                elif format_type == "mobi":
                    filepath = self.create_compilation_mobi(articles, output_dir)
                else:
                    filepath = self.create_compilation_html(articles, output_dir)
                
                if filepath and filepath.exists():
                    # Send to Kindle
                    if self.send_to_kindle(filepath):
                        # Archive all articles if successfully sent
                        archived_count = 0
                        for article in articles:
                            if self.archive_article(article.get('id')):
                                archived_count += 1
                        
                        self.logger.info(f"Successfully processed compilation with {len(articles)} articles")
                        self.logger.info(f"Archived {archived_count}/{len(articles)} articles")
                        
                        # Cleanup file if requested
                        if cleanup_files:
                            self.cleanup_file(filepath)
                    else:
                        self.logger.error("Failed to send compilation document")
                else:
                    self.logger.error("Failed to create compilation document")
                    
            except Exception as e:
                self.logger.error(f"Error creating compilation: {e}")
        
        else:
            # Individual article processing (original behavior)
            processed_count = 0
            
            for article in articles:
                article_id = article.get('id')
                title = article.get('content', {}).get('title', 'Untitled')
                
                self.logger.info(f"Processing article: {title}")
                
                if dry_run:
                    self.logger.info(f"DRY RUN: Would process article {article_id}")
                    continue
                
                try:
                    # Convert to document
                    filepath = self.convert_to_document(article, self.config["output"]["format"])
                    
                    if filepath and filepath.exists():
                        # Send to Kindle
                        if self.send_to_kindle(filepath):
                            # Archive article if successfully sent
                            if self.archive_article(article_id):
                                processed_count += 1
                                self.logger.info(f"Successfully processed article: {title}")
                                
                                # Cleanup file if requested
                                if cleanup_files:
                                    self.cleanup_file(filepath)
                            else:
                                self.logger.warning(f"Article sent but not archived: {title}")
                        else:
                            self.logger.error(f"Failed to send article: {title}")
                    else:
                        self.logger.error(f"Failed to create document for: {title}")
                        
                except Exception as e:
                    self.logger.error(f"Error processing article {title}: {e}")
            
            self.logger.info(f"Processing complete. Successfully processed {processed_count} articles.")

def main():
    parser = argparse.ArgumentParser(description='Process Karakeep articles for Kindle')
    parser.add_argument('--config', default=CONFIG_FILE, help='Configuration file path')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without actually doing it')
    parser.add_argument('--format', choices=['pdf', 'epub', 'html', 'mobi'], help='Output format (overrides config)')
    parser.add_argument('--compilation', action='store_true', help='Create single document with all articles instead of individual files')
    parser.add_argument('--cleanup', action='store_true', help='Delete generated files after successful email delivery')
    parser.add_argument('--send-email', metavar='FILE', help='Send specified file to Kindle via email (bypasses article processing)')
    
    args = parser.parse_args()
    
    try:
        processor = KindleBookmarksProcessor(args.config)
        
        # Handle send-email mode (bypasses article processing)
        if args.send_email:
            filepath = Path(args.send_email)
            if not filepath.exists():
                print(f"Error: File '{filepath}' does not exist")
                sys.exit(1)
            
            if args.dry_run:
                print(f"DRY RUN: Would send file '{filepath}' to Kindle")
                return
            
            print(f"Sending file '{filepath}' to Kindle...")
            if processor.send_to_kindle(filepath):
                print(f"Successfully sent '{filepath.name}' to Kindle")
                
                # Cleanup file if requested
                if args.cleanup:
                    processor.cleanup_file(filepath)
            else:
                print(f"Failed to send '{filepath.name}' to Kindle")
                sys.exit(1)
            return
        
        # Override format if specified
        if args.format:
            processor.config["output"]["format"] = args.format
        
        processor.process_articles(dry_run=args.dry_run, compilation_mode=args.compilation, cleanup_files=args.cleanup)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()