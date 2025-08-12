# Node-RED Integration Guide

This guide shows how to integrate the Kindle Bookmarks script with Node-RED for automated article processing.

## 🚀 Quick Setup

### 1. Shell Script Ready
The `run_kindle_compilation.sh` script is designed for Node-RED automation:

```bash
# Test the script manually first
./run_kindle_compilation.sh --dry-run

# Run actual compilation
./run_kindle_compilation.sh
```

### 2. Node-RED Flow Configuration

#### Basic Exec Node Setup:
```json
{
    "id": "kindle-bookmarks",
    "type": "exec",
    "command": "/full/path/to/run_kindle_compilation.sh",
    "addpay": false,
    "append": "",
    "useSpawn": "false",
    "timer": "",
    "oldrc": false,
    "name": "Kindle Bookmarks",
    "x": 400,
    "y": 200,
    "wires": [["success-output"], ["error-output"], ["exit-code"]]
}
```

## 📋 Node-RED Flow Examples

### 1. Scheduled Daily Processing

```
[Inject: Daily 8AM] → [Exec: run_kindle_compilation.sh] → [Debug: Results]
```

**Inject Node Configuration:**
- **Repeat:** interval
- **Every:** 1 days at 08:00

### 2. Manual Trigger with Status

```
[Button] → [Exec: Kindle Script] → [Switch: Success/Error] → [Notification]
```

**Flow JSON:**
```json
[
    {
        "id": "manual-trigger",
        "type": "inject",
        "name": "Process Articles",
        "props": [{"p": "payload", "v": "", "vt": "date"}],
        "repeat": "",
        "crontab": "",
        "once": false
    },
    {
        "id": "kindle-exec",
        "type": "exec",
        "command": "/home/user/kindle-bookmarks/run_kindle_compilation.sh",
        "name": "Kindle Compilation"
    },
    {
        "id": "result-switch",
        "type": "switch",
        "property": "payload.code",
        "rules": [
            {"t": "eq", "v": "0", "vt": "num"},
            {"t": "neq", "v": "0", "vt": "num"}
        ]
    }
]
```

### 3. Advanced Flow with Notifications

```
[Schedule] → [Exec] → [Switch] → [Success: Email/Slack] 
                   └→ [Error: Alert/Log]
```

## 🔧 Script Features for Node-RED

### Exit Codes
- **0:** Success - Articles processed and sent
- **1:** Error - Check logs for details

### Output Parsing
The script provides structured output:

```bash
# Success output
[2024-08-12 09:13:45] Starting Kindle bookmarks compilation...
[SUCCESS] Kindle compilation completed successfully

# Error output  
[ERROR] Configuration file not found at /path/config.json
[ERROR] Script failed
```

### Log Integration
- **Log file:** `kindle_bookmarks.log`
- **Recent logs:** Displayed in script output
- **Auto cleanup:** Removes logs older than 7 days

## 📱 Node-RED Integration Patterns

### 1. Simple Automation
```javascript
// Function node to parse results
if (msg.payload.code === 0) {
    msg.payload = {
        success: true,
        message: "Articles sent to Kindle successfully"
    };
} else {
    msg.payload = {
        success: false,
        message: "Failed to process articles",
        error: msg.payload.stderr
    };
}
return msg;
```

### 2. Conditional Processing
```javascript
// Only run if there are unread articles
// Add a pre-check function node
msg.command = "/path/to/run_kindle_compilation.sh --dry-run";
return msg;
```

### 3. Status Dashboard
Create a Node-RED dashboard with:
- **Manual trigger button**
- **Status indicator** (success/error)
- **Last run timestamp**
- **Article count processed**

## 🔔 Notification Examples

### Email Notification (Success)
```javascript
msg.to = "your-email@example.com";
msg.subject = "Kindle Articles Processed";
msg.payload = `Successfully processed and sent articles to Kindle at ${new Date()}`;
return msg;
```

### Slack Notification
```javascript
msg.payload = {
    "text": "📚 Kindle articles processed successfully!",
    "channel": "#notifications"
};
return msg;
```

### Home Assistant Integration
```javascript
msg.payload = {
    "state": "on",
    "attributes": {
        "last_run": new Date().toISOString(),
        "status": "success"
    }
};
msg.topic = "homeassistant/sensor/kindle_bookmarks/state";
return msg;
```

## 🛠 Troubleshooting

### Common Issues

1. **Permission Denied**
   ```bash
   chmod +x /path/to/run_kindle_compilation.sh
   ```

2. **Virtual Environment Not Found**
   - Ensure the `venv` directory exists in the script directory
   - Run the installation script first

3. **Config File Missing**
   - Run `python setup_config.py` to create configuration

4. **Path Issues in Node-RED**
   - Use absolute paths in the exec node
   - Set working directory if needed

### Debug Mode
```bash
# Test script manually
./run_kindle_compilation.sh --dry-run

# Check logs
tail -f kindle_bookmarks.log
```

## 📊 Monitoring

### Log Analysis Function Node
```javascript
// Parse log output for statistics
const logLines = msg.payload.split('\n');
const articleCount = logLines
    .filter(line => line.includes('Found'))
    .map(line => line.match(/\d+/))
    .filter(match => match)[0];

msg.payload = {
    timestamp: new Date(),
    articles_processed: parseInt(articleCount) || 0,
    success: msg.payload.code === 0
};

return msg;
```

## 🚀 Advanced Automation

### Multi-Format Processing
Create separate flows for different formats:
- **Morning:** HTML compilation for quick reading
- **Evening:** PDF compilation for offline reading
- **Weekly:** MOBI compilation for Kindle library

### Conditional Logic
```javascript
// Only process if more than 5 articles
if (msg.article_count > 5) {
    msg.command = "/path/to/run_kindle_compilation.sh";
} else {
    msg.command = "/path/to/run_kindle_compilation.sh --dry-run";
}
return msg;
```

This integration makes your Kindle article processing completely automated and monitorable through Node-RED! 🎉

---

## 🐳 Docker Container Integration

### Static Executable for Containers

For Node-RED running in Docker containers, use the static executable approach:

#### 1. Compile Static Executable
```bash
# Install PyInstaller and compile
./compile_static_executable.sh
```

This creates:
- `dist/kindle-bookmarks` - Standalone executable (no dependencies)
- `dist/run-in-docker.sh` - Docker-friendly wrapper
- `kindle-bookmarks-static-YYYYMMDD-HHMMSS.tar.gz` - Deployment package

#### 2. Docker Integration Methods

**Method A: Volume Mount**
```yaml
# docker-compose.yml
version: '3.8'
services:
  nodered:
    image: nodered/node-red
    volumes:
      - ./dist:/data/kindle-bookmarks
    environment:
      - TZ=Europe/Rome
```

**Method B: Copy to Container**
```dockerfile
# Custom Node-RED Dockerfile
FROM nodered/node-red
COPY dist/kindle-bookmarks /data/kindle-bookmarks/
COPY dist/run-in-docker.sh /data/kindle-bookmarks/
COPY config.json /data/kindle-bookmarks/
USER node-red
```

#### 3. Node-RED Exec Node Configuration

**For Docker Container:**
```json
{
    "id": "kindle-docker",
    "type": "exec",
    "command": "/data/kindle-bookmarks/run-in-docker.sh",
    "addpay": false,
    "append": "",
    "useSpawn": "false",
    "timer": "",
    "oldrc": false,
    "name": "Kindle Bookmarks (Docker)",
    "x": 400,
    "y": 200,
    "wires": [["success"], ["error"], ["exit-code"]]
}
```

#### 4. Container Setup Steps

1. **Compile executable** (on host):
   ```bash
   ./compile_static_executable.sh
   ```

2. **Extract deployment package**:
   ```bash
   tar -xzf kindle-bookmarks-static-*.tar.gz
   ```

3. **Create config.json**:
   ```bash
   cd kindle-bookmarks-static/
   cp config.json.example config.json
   # Edit config.json with your settings
   ```

4. **Copy to Node-RED container**:
   ```bash
   docker cp kindle-bookmarks-static/ nodered_container:/data/
   ```

5. **Test in container**:
   ```bash
   docker exec nodered_container /data/kindle-bookmarks-static/run-in-docker.sh
   ```

### Docker Benefits

✅ **No Dependencies** - Single executable with everything bundled  
✅ **No Python Runtime** - No need to install Python in container  
✅ **No Package Management** - No pip, venv, or package conflicts  
✅ **Smaller Containers** - No additional layers needed  
✅ **Faster Startup** - No dependency resolution  
✅ **Consistent Execution** - Same behavior across all environments  

### Container Troubleshooting

**Permission Issues:**
```bash
# In container
chmod +x /data/kindle-bookmarks-static/kindle-bookmarks
chmod +x /data/kindle-bookmarks-static/run-in-docker.sh
```

**Config File Missing:**
```bash
# Check config exists
docker exec container ls -la /data/kindle-bookmarks-static/config.json
```

**Testing Executable:**
```bash
# Test help command
docker exec container /data/kindle-bookmarks-static/kindle-bookmarks --help

# Test dry run
docker exec container /data/kindle-bookmarks-static/kindle-bookmarks --dry-run --compilation
```

This approach eliminates all dependency management headaches in Docker environments! 🚀