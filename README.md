# Kindle Bookmarks - Karakeep to Kindle Converter

This script automatically retrieves your saved articles from Karakeep, converts them to PDF, EPUB, or HTML format, sends them to your Kindle via email, and archives the processed articles.

## ✨ Features

- 📚 **Retrieves unarchived articles** from your Karakeep instance
- 📄 **Multiple output formats**: PDF, EPUB, and HTML with embedded images
- 📖 **Compilation mode**: Create single document with all articles or individual files
- 🖼️ **Complete image support**: Downloads and embeds all images for offline reading
- 📧 **Kindle delivery**: Sends documents to your Kindle via email
- 🗂️ **Auto-archiving**: Marks articles as archived after successful delivery
- 🔧 **Flexible configuration**: Customizable settings and output options
- 📝 **Comprehensive logging**: Detailed tracking of all operations
- 🛡️ **Robust error handling**: Graceful fallbacks and timeout management

## Quick Start

### 1. Run the Installation Script

```bash
./install.sh
```

This will:
- Create a virtual environment
- Install required dependencies
- Install optional PDF/EPUB libraries (if possible)

### 2. Configure Your Settings

```bash
source venv/bin/activate
python setup_config.py
```

This interactive script will help you set up your configuration.

### 3. Test the Setup

```bash
source venv/bin/activate
python kindle_bookmarks.py --dry-run
```

### 4. Run the Script

```bash
source venv/bin/activate
python kindle_bookmarks.py
```

## Manual Setup

### 1. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configuration

Copy the example configuration file and edit it with your settings:

```bash
cp config.json.example config.json
```

Edit `config.json` with your details:

#### Karakeep Settings
- `api_url`: Your Karakeep instance URL (default: https://bookmarks.damianogiorgi.it/api/v1)
- `api_key`: Your Karakeep API key

#### Kindle Settings
- `email`: Your Kindle email address (found in Amazon account settings)
- `smtp_server`: SMTP server for sending emails (Gmail: smtp.gmail.com)
- `smtp_port`: SMTP port (Gmail: 587)
- `smtp_user`: Your email address
- `smtp_password`: Your email password or app-specific password

#### Output Settings
- `format`: Output format ("pdf" or "epub")
- `output_dir`: Directory to save generated files

### 3. Kindle Email Setup

1. Go to Amazon's "Manage Your Content and Devices" page
2. Find your Kindle email address (usually ends with @kindle.com)
3. Add your sending email address to the approved list

### 4. Gmail App Password (if using Gmail)

1. Enable 2-factor authentication on your Google account
2. Generate an app-specific password for this script
3. Use the app password in the configuration, not your regular password

## Usage

### Basic Usage

Process all unarchived articles:
```bash
python kindle_bookmarks.py
```

### Command Line Options

- `--dry-run`: Show what would be processed without actually doing it
- `--format pdf|epub|html`: Override the output format from config
- `--compilation`: Create single document with all articles instead of individual files
- `--cleanup`: Delete generated files after successful email delivery
- `--config path/to/config.json`: Use a different configuration file

### Individual Articles Mode (Default)

Process each article as a separate file:

```bash
# Process all articles as individual files
python kindle_bookmarks.py

# Dry run to see what would be processed
python kindle_bookmarks.py --dry-run

# Force PDF format for individual files
python kindle_bookmarks.py --format pdf
```

### Compilation Mode (Recommended)

Create a single document containing all articles:

```bash
# Create single EPUB with all articles (recommended for Kindle)
python kindle_bookmarks.py --compilation --format epub

# Create single PDF with all articles
python kindle_bookmarks.py --compilation --format pdf

# Create single HTML with all articles
python kindle_bookmarks.py --compilation --format html

# Test compilation mode
python kindle_bookmarks.py --compilation --dry-run

# Clean up files after successful delivery
python kindle_bookmarks.py --compilation --format epub --cleanup
```

### Advanced Examples

```bash
# Use custom config file
python kindle_bookmarks.py --config my-config.json

# Compilation with custom config
python kindle_bookmarks.py --compilation --format epub --config my-config.json
```

## How It Works

### Individual Articles Mode
1. **Fetch Articles**: Retrieves all unarchived articles from your Karakeep instance
2. **Process Each Article**: Converts each article separately with embedded images
3. **Send**: Emails each converted document to your Kindle
4. **Archive**: Marks each article as archived after successful delivery

### Compilation Mode (Recommended)
1. **Fetch Articles**: Retrieves all unarchived articles from your Karakeep instance
2. **Compile**: Creates a single document with all articles as chapters/sections
3. **Embed Images**: Downloads and embeds all images for offline reading
4. **Send**: Emails the single compilation document to your Kindle
5. **Archive**: Marks all articles as archived after successful delivery

## 🖼️ Image Handling

The script provides comprehensive image support for perfect offline reading:

### Supported Image Sources
- **Karakeep Assets**: Downloads images stored in your Karakeep instance via API
- **External Images**: Downloads images from original article sources as fallback
- **Multiple Formats**: JPEG, PNG, WebP, GIF, and other common formats

### Image Processing Features
- **Base64 Embedding**: All images converted to base64 data URLs for offline access
- **Size Optimization**: 5MB limit per image to prevent huge files
- **Smart Fallbacks**: Karakeep assets first, then external URLs
- **Timeout Protection**: 15-second timeout per image to prevent hanging
- **Error Handling**: Graceful handling of failed downloads with detailed logging

### Image Quality
- **Original Resolution**: Maintains original image quality when possible
- **Lossless Encoding**: No quality degradation during base64 conversion
- **Content-Type Detection**: Proper MIME type handling for all formats

## 📄 File Formats (HTML-First Architecture)

The script uses a clean **HTML-first approach**: it generates a high-quality HTML document with embedded images, then converts it to other formats as needed.

### HTML (Base Format)
- **Self-Contained**: Single file with all content and images embedded
- **Professional Styling**: Clean, readable typography and layout
- **Responsive Design**: Works on any device with a web browser
- **Table of Contents**: Clickable navigation between articles
- **Embedded Images**: Base64-encoded images for offline viewing
- **Always Available**: Core format that always works

### PDF (Converted from HTML)
- **High-Quality Generation**: Uses WeasyPrint to convert HTML to professional PDFs
- **Print-Optimized**: A4 page size with proper margins and typography
- **Consistent Layout**: Same styling as HTML, ensuring perfect consistency
- **Page Breaks**: Automatic page breaks for print-friendly reading
- **Embedded Images**: All images properly sized and positioned
- **Fallback**: Returns HTML file if WeasyPrint unavailable

### EPUB (Converted from HTML)
- **E-reader Compatible**: Converts HTML to EPUB format for Kindle, Kobo, etc.
- **Chapter Structure**: Maintains article organization from HTML
- **Embedded Images**: All images included in EPUB package
- **Metadata**: Proper EPUB metadata with title, author, and language
- **Reflowable Text**: Adapts to different screen sizes
- **Fallback**: Returns HTML file if ebooklib unavailable

### Benefits of HTML-First Approach
- ✅ **Consistency**: All formats use the same base HTML, eliminating format-specific bugs
- ✅ **Reliability**: HTML always works, other formats are optional enhancements
- ✅ **Simplicity**: Single image processing pipeline, no duplicate code
- ✅ **Quality**: Professional styling and layout across all formats
- ✅ **Maintainability**: Easier to debug and maintain with unified approach

## 📖 Compilation vs Individual Articles

### Compilation Mode Benefits (Recommended)
- ✅ **Single File**: One document with all articles for easy management
- ✅ **Better Organization**: Professional cover page and table of contents
- ✅ **Kindle Friendly**: Single EPUB file perfect for e-readers
- ✅ **Efficient**: One email delivery instead of multiple
- ✅ **Complete Archive**: All articles archived together after successful delivery

### Individual Articles Mode
- ✅ **Granular Control**: Process articles separately
- ✅ **Selective Reading**: Choose which articles to read
- ✅ **Incremental Processing**: Handle articles one by one
- ✅ **Smaller Files**: Individual files are smaller in size

### File Size Examples
- **Individual Articles**: 200KB - 2MB per article (depending on images)
- **Compilation**: 2MB - 15MB total (depending on number of articles and images)
- **Images Impact**: Articles with many images will be larger but work offline

## 🧹 File Cleanup

The script includes automatic cleanup functionality to keep your system tidy:

### Cleanup Features
- **Automatic Cleanup**: Use `--cleanup` flag to delete files after successful email delivery
- **Smart Cleanup**: Only deletes files after successful Kindle delivery and archiving
- **Error Handling**: Graceful handling of cleanup failures with detailed logging
- **Manual Control**: Cleanup is optional - files are preserved by default

### Cleanup Examples
```bash
# Clean up after successful delivery (recommended for automation)
python kindle_bookmarks.py --compilation --format epub --cleanup

# Keep files for manual review (default behavior)
python kindle_bookmarks.py --compilation --format epub
```

### When to Use Cleanup
- ✅ **Automated Scripts**: Perfect for cron jobs and scheduled runs
- ✅ **Storage Management**: Prevents accumulation of temporary files
- ✅ **Privacy**: Removes local copies after successful delivery
- ❌ **Debugging**: Keep files when troubleshooting issues
- ❌ **Manual Review**: Keep files if you want to review before deletion

## 📊 Performance & Optimization

### Processing Speed
- **Image Downloads**: 15-second timeout per image with smart caching
- **Sequential Processing**: Articles processed one by one to avoid API rate limits
- **Memory Efficient**: Large images are size-limited to prevent memory issues
- **Batch Archiving**: In compilation mode, all articles archived together

### File Size Management
- **Image Size Limits**: 5MB maximum per image to keep files manageable
- **Compression**: Base64 encoding is efficient for embedded images
- **Format Optimization**: PDF/EPUB formats are optimized for e-readers
- **Fallback Strategy**: HTML format available if specialized libraries fail

## 📝 Logging & Monitoring

The script provides comprehensive logging for troubleshooting and monitoring:

### Log Locations
- **Console Output**: Real-time progress and status updates
- **Log File**: Detailed logs saved to `kindle_bookmarks.log`
- **Persistent History**: All operations logged with timestamps

### What Gets Logged
- ✅ **Article Processing**: Title, success/failure, file sizes
- 🖼️ **Image Downloads**: Asset IDs, URLs, file sizes, errors
- 📧 **Email Delivery**: SMTP connection, send status, errors
- 🗂️ **Archiving**: Article IDs, success/failure status
- ⚠️ **Errors & Warnings**: Detailed error messages with context
- 📊 **Performance**: Processing times and file sizes

### Log Example
```
2025-08-11 21:25:24,773 - INFO - Processing article 1/4: Nintil - A jhourney in Costa Rica...
2025-08-11 21:25:26,042 - INFO - Downloaded Karakeep asset: 24af5d24-b12c-4366-85c7-084e46a20736 (105980 bytes)
2025-08-11 21:25:41,055 - INFO - Created compilation EPUB: Karakeep_Articles_20250811_212738.epub (7.8 MB)
2025-08-11 21:25:42,123 - INFO - Successfully sent to Kindle: user@kindle.com
2025-08-11 21:25:43,456 - INFO - Archived 4/4 articles successfully
```

## Troubleshooting

### Common Issues

1. **API Key Invalid**: Check your Karakeep API key in the config
2. **Email Delivery Failed**: 
   - Verify Kindle email address
   - Check that your sending email is approved in Amazon settings
   - For Gmail, ensure you're using an app password
3. **PDF/EPUB Generation Failed**: 
   - Install weasyprint: `pip install weasyprint`
   - Install ebooklib: `pip install ebooklib`
   - Script will fallback to HTML format if libraries are missing

### Dependencies Issues

If you encounter issues with weasyprint installation:

**On Ubuntu/Debian:**
```bash
sudo apt-get install python3-dev python3-pip python3-cffi python3-brotli libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0
```

**On macOS:**
```bash
brew install pango
```

**On Windows:**
- Use the pre-compiled wheels: `pip install weasyprint`

## 🚀 **Quick Start Guide**

### For First-Time Users

1. **Install the script:**
   ```bash
   ./install.sh
   ```

2. **Configure your settings:**
   ```bash
   source venv/bin/activate
   python setup_config.py
   ```

3. **Test with compilation mode (recommended):**
   ```bash
   python kindle_bookmarks.py --compilation --format epub --dry-run
   ```

4. **Send to your Kindle:**
   ```bash
   python kindle_bookmarks.py --compilation --format epub
   ```

### Recommended Workflow

**For Regular Use:**
```bash
# Activate virtual environment
source venv/bin/activate

# Create single EPUB with all articles, send to Kindle, and cleanup
python kindle_bookmarks.py --compilation --format epub --cleanup
```

**For Testing:**
```bash
# See what articles would be processed
python kindle_bookmarks.py --compilation --dry-run
```

## 📋 **Configuration Reference**

### Complete config.json Example
```json
{
  "karakeep": {
    "api_url": "https://your-karakeep-instance.com/api/v1",
    "api_key": "your_api_key_here"
  },
  "kindle": {
    "email": "your_kindle_email@kindle.com",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_user": "your_email@gmail.com",
    "smtp_password": "your_app_password"
  },
  "output": {
    "format": "epub",
    "output_dir": "./output"
  }
}
```

### Environment Variables (Optional)
For enhanced security, you can use environment variables:
```bash
export KARAKEEP_API_KEY="your_api_key"
export KINDLE_EMAIL="your_kindle_email@kindle.com"
export SMTP_PASSWORD="your_app_password"
```

## 🔧 **Advanced Usage**

### Automation with Cron
Set up automatic processing:
```bash
# Edit crontab
crontab -e

# Add line to run daily at 9 AM with cleanup
0 9 * * * cd /path/to/kindle-bookmarks && source venv/bin/activate && python kindle_bookmarks.py --compilation --format epub --cleanup
```

### Custom Scripts
Create wrapper scripts for different use cases:

**daily_kindle.sh:**
```bash
#!/bin/bash
cd /path/to/kindle-bookmarks
source venv/bin/activate
python kindle_bookmarks.py --compilation --format epub --cleanup
```

**test_articles.sh:**
```bash
#!/bin/bash
cd /path/to/kindle-bookmarks
source venv/bin/activate
python kindle_bookmarks.py --compilation --dry-run
```

## 🐳 **Docker & Node-RED Integration**

### Automated Execution with Node-RED

For automated processing in Node-RED environments, especially on Raspberry Pi, use the provided automation scripts:

#### Method 1: Shell Script (Host Environment)
```bash
# Use the Node-RED automation script
./run_kindle_compilation.sh
```

#### Method 2: Portable Bundle (Docker Containers)
For Node-RED running in Docker containers, use the portable Python bundle:

```bash
# Create portable bundle (solves ARM64/compatibility issues)
./compile_static_executable.sh --portable
```

### 🚨 **Raspberry Pi ARM64 Docker Issues**

**Problem:** PyInstaller executables fail in ARM64 Docker containers with errors like:
```
kindle-bookmarks: cannot execute: required file not found
Error loading shared library ld-linux-aarch64.so.1: No such file or directory
Error relocating kindle-bookmarks: __realpath_chk: symbol not found
```

**Root Cause:** 
- PyInstaller creates dynamically linked executables
- ARM64 containers often lack required glibc libraries
- Architecture-specific compilation compatibility issues

**✅ Solution: Use Portable Python Bundle**

The portable bundle approach eliminates all compilation and architecture issues:

### Portable Bundle Setup for Docker

#### 1. Create Portable Bundle
```bash
# On your development machine (any architecture)
./compile_static_executable.sh --portable
```

This creates:
- `dist/kindle-bookmarks-portable/` - Complete portable application
- `kindle-bookmarks-portable-YYYYMMDD-HHMMSS.tar.gz` - Deployment package

#### 2. Deploy to Docker Container
```bash
# Extract deployment package
tar -xzf kindle-bookmarks-portable-*.tar.gz

# Copy to your Node-RED container
docker cp kindle-bookmarks-portable/ nodered_container:/data/

# Create configuration
docker exec nodered_container cp /data/kindle-bookmarks-portable/config.json.example /data/kindle-bookmarks-portable/config.json
# Edit config.json with your settings
```

#### 3. Node-RED Exec Node Configuration
```json
{
    "id": "kindle-docker",
    "type": "exec",
    "command": "/data/kindle-bookmarks-portable/run-portable.sh",
    "addpay": false,
    "append": "",
    "useSpawn": "false",
    "timer": "",
    "oldrc": false,
    "name": "Kindle Bookmarks (Docker)",
    "wires": [["success"], ["error"], ["exit-code"]]
}
```

### Docker Integration Methods

#### Method A: Volume Mount
```yaml
# docker-compose.yml
version: '3.8'
services:
  nodered:
    image: nodered/node-red
    volumes:
      - ./kindle-bookmarks-portable:/data/kindle-bookmarks
    environment:
      - TZ=Europe/Rome
```

#### Method B: Custom Dockerfile
```dockerfile
FROM nodered/node-red
COPY kindle-bookmarks-portable/ /data/kindle-bookmarks/
USER node-red
```

### Portable Bundle Benefits

| Traditional Approach | Portable Bundle |
|---------------------|-----------------|
| ❌ Architecture-specific compilation | ✅ Works on any architecture |
| ❌ glibc/library dependencies | ✅ Only requires Python 3.7+ |
| ❌ Static linking issues | ✅ Pure Python approach |
| ❌ Large binary files (50MB+) | ✅ Lightweight bundle (10KB) |
| ❌ Compilation compatibility problems | ✅ No compilation needed |

### Container Requirements

**Minimal Requirements:**
- Python 3.7+ available in container
- Internet access for initial dependency installation
- Basic Linux utilities (bash, tar, etc.)

**Compatible Base Images:**
- `nodered/node-red` (includes Python)
- `python:3.7-alpine`
- `ubuntu:20.04` + Python
- `debian:bullseye` + Python

### Node-RED Flow Examples

#### Simple Scheduled Processing
```json
[
    {
        "id": "daily-trigger",
        "type": "inject",
        "name": "Daily 8AM",
        "props": [{"p": "payload", "v": "", "vt": "date"}],
        "repeat": "",
        "crontab": "0 8 * * *",
        "once": false
    },
    {
        "id": "kindle-exec",
        "type": "exec",
        "command": "/data/kindle-bookmarks-portable/run-portable.sh",
        "name": "Process Articles"
    },
    {
        "id": "result-debug",
        "type": "debug",
        "name": "Results"
    }
]
```

#### Advanced Flow with Notifications
```json
[
    {
        "id": "manual-button",
        "type": "inject",
        "name": "Process Now",
        "props": [{"p": "payload", "v": "", "vt": "date"}]
    },
    {
        "id": "kindle-exec",
        "type": "exec",
        "command": "/data/kindle-bookmarks-portable/run-portable.sh"
    },
    {
        "id": "success-check",
        "type": "switch",
        "property": "payload.code",
        "rules": [
            {"t": "eq", "v": "0", "vt": "num"},
            {"t": "neq", "v": "0", "vt": "num"}
        ]
    },
    {
        "id": "success-notification",
        "type": "function",
        "name": "Success Message",
        "func": "msg.payload = 'Articles sent to Kindle successfully!'; return msg;"
    },
    {
        "id": "error-notification",
        "type": "function",
        "name": "Error Message", 
        "func": "msg.payload = 'Failed to process articles: ' + msg.payload.stderr; return msg;"
    }
]
```

### Troubleshooting Docker Issues

#### Container Python Check
```bash
# Verify Python availability in container
docker exec container python3 --version
docker exec container which python3
```

#### Permission Issues
```bash
# Fix permissions if needed
docker exec container chmod +x /data/kindle-bookmarks-portable/run-portable.sh
```

#### Config File Issues
```bash
# Check config exists and is readable
docker exec container ls -la /data/kindle-bookmarks-portable/config.json
docker exec container cat /data/kindle-bookmarks-portable/config.json
```

#### Test Execution
```bash
# Test the portable runner directly
docker exec container /data/kindle-bookmarks-portable/run-portable.sh --help
```

### Performance in Containers

**Startup Time:**
- First run: ~30 seconds (creates venv, installs dependencies)
- Subsequent runs: ~5 seconds (uses existing environment)

**Resource Usage:**
- Memory: ~50MB during execution
- Storage: ~20MB for portable environment
- Network: Downloads images and sends email

**Optimization Tips:**
- Use persistent volumes to preserve the portable virtual environment
- Schedule processing during low-traffic periods
- Monitor container logs for performance insights

### Security in Docker

**Configuration Security:**
- Mount config.json as read-only volume
- Use Docker secrets for sensitive values
- Restrict container network access if possible

**File Security:**
- Portable bundle creates temporary files in container
- Files are automatically cleaned up after successful delivery
- No persistent sensitive data stored

This approach completely eliminates the ARM64/glibc compatibility issues while providing a robust, maintainable solution for Docker-based Node-RED automation! 🚀

## 🛠️ **Troubleshooting Guide**

### Common Issues & Solutions

**1. No articles found:**
```bash
# Check if articles are already archived
curl -H "Authorization: Bearer YOUR_API_KEY" "YOUR_KARAKEEP_URL/api/v1/bookmarks"
```

**2. Email delivery fails:**
- Verify Kindle email in Amazon account settings
- Check SMTP credentials and app password
- Ensure sender email is approved in Amazon

**3. Image download timeouts:**
- Check internet connection
- Images will be skipped but articles will still process
- Check logs for specific error details

**4. PDF/EPUB generation fails:**
- Script automatically falls back to HTML format
- Install missing dependencies: `pip install weasyprint ebooklib`
- Check logs for specific library errors

### Debug Mode
Enable verbose logging by checking the log file:
```bash
tail -f kindle_bookmarks.log
```

## 📊 **Performance Tips**

### Optimize Processing Speed
- Use compilation mode for fewer email deliveries
- Ensure stable internet connection for image downloads
- Consider running during off-peak hours for better API response

### Manage File Sizes
- Large compilations (10+ articles with many images) may be 10-20MB
- Individual articles are typically 200KB-2MB each
- Kindle supports files up to 50MB via email

## 🔒 **Security Best Practices**

### API Key Security
- Never commit config.json to version control
- Use environment variables for sensitive data
- Rotate API keys periodically
- Restrict API key permissions if possible

### Email Security
- Use app-specific passwords, not account passwords
- Enable 2-factor authentication on email accounts
- Consider using dedicated email account for automation

### File Security
- Output directory contains your articles - keep secure
- Log files may contain URLs and metadata
- Use `--cleanup` flag to automatically delete files after successful delivery
- Clean up old files periodically if not using `--cleanup`

## 📚 **Additional Resources**

### Documentation Files
- `IMAGE_HANDLING.md` - Detailed image processing documentation
- `config.json.example` - Configuration template
- `kindle_bookmarks.log` - Runtime logs and debugging info

### Karakeep API
- [Official API Documentation](https://docs.karakeep.app/API/karakeep-api/)
- Your Karakeep instance API endpoint: `/api/v1/bookmarks`

### Kindle Email Setup
- [Amazon Kindle Email Documentation](https://www.amazon.com/gp/help/customer/display.html?nodeId=GX9XLEVV8G4DB28H)
- Manage Your Content and Devices page in Amazon account

## 🤝 **Contributing**

We welcome contributions! Please feel free to:
- Report bugs and issues
- Suggest new features
- Submit pull requests
- Improve documentation

## 📄 **License**

This project is open source and available under the MIT License.

---

## 🎉 **Success Stories**

After setup, you should see logs like:
```
2025-08-11 21:25:24,773 - INFO - Creating compilation EPUB with 4 articles...
2025-08-11 21:25:41,055 - INFO - Created compilation EPUB: Karakeep_Articles_20250811_212738.epub (7.8 MB)
2025-08-11 21:25:42,123 - INFO - Successfully sent to Kindle
2025-08-11 21:25:43,456 - INFO - Archived 4/4 articles successfully
```

Your Kindle will receive a professional document with all your articles and embedded images, ready for offline reading! 📖✨