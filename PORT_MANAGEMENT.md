# Port Management Guide

## Check All Running Ports

### Method 1: List all listening ports
```bash
lsof -i -P -n | grep LISTEN
```

### Method 2: Check specific port (e.g., 8891)
```bash
lsof -i :8891
```

### Method 3: Using netstat (alternative)
```bash
netstat -an | grep LISTEN
```

### Method 4: Using lsof with port range
```bash
lsof -i TCP -s TCP:LISTEN
```

## Shutdown Port / Kill Process

### Method 1: Kill by Port (RECOMMENDED)

**Step 1:** Find the process using the port
```bash
lsof -i :8891
```

**Step 2:** Kill the process (replace PID with actual process ID)
```bash
kill -9 <PID>
```

**One-liner to kill process on port 8891:**
```bash
lsof -ti :8891 | xargs kill -9
```

### Method 2: Using pkill (if you know the process name)

```bash
# Kill by process name
pkill -f "python.*app.py"
# OR
pkill -f uvicorn
```

### Method 3: Graceful shutdown (if process supports it)

```bash
# Send SIGTERM first (graceful)
kill <PID>

# If that doesn't work, force kill
kill -9 <PID>
```

## Common Ports for This Project

- **Port 8891** - Super Receptionist AI Agent (default)
- **Port 8000** - Common FastAPI default

## Quick Commands Reference

### Check if port 8891 is in use
```bash
lsof -i :8891
```

### Kill process on port 8891
```bash
lsof -ti :8891 | xargs kill -9
```

### Kill all Python processes (be careful!)
```bash
pkill -9 python
```

### Kill all uvicorn processes
```bash
pkill -9 uvicorn
```

### Find and kill Super Receptionist specifically
```bash
ps aux | grep "app.py" | grep -v grep | awk '{print $2}' | xargs kill -9
```

## Step-by-Step: Shutdown Port 8891

1. **Check what's running:**
   ```bash
   lsof -i :8891
   ```
   
   Output example:
   ```
   COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
   python3  1234 user   3u  IPv4  0x...      0t0  TCP *:8891 (LISTEN)
   ```

2. **Kill the process:**
   ```bash
   kill -9 1234
   ```
   
   Or use the one-liner:
   ```bash
   lsof -ti :8891 | xargs kill -9
   ```

3. **Verify it's stopped:**
   ```bash
   lsof -i :8891
   ```
   Should return nothing if port is free.

## Alternative: Stop Server Properly

If the server is running in a terminal:
- Press `Ctrl+C` to stop it gracefully

If running in background:
```bash
# Find the process
ps aux | grep "python.*app.py"

# Kill it
kill -9 <PID>
```

## Port Already in Use Error

If you see: `Address already in use` or `Port 8891 is already in use`

**Solution:**
```bash
# Kill the process using port 8891
lsof -ti :8891 | xargs kill -9

# Then restart your server
python3 app.py
```

## Change Port (Alternative Solution)

If you can't kill the process, change the port in `.env`:
```env
PORT=8892
```

Or in `app.py` line 199, change:
```python
port = int(os.getenv("PORT", "8892"))  # Changed from 8891
```

## Safety Tips

⚠️ **Warning:** `kill -9` forces immediate termination. Use it only if:
- Normal `kill` doesn't work
- You're sure about the process ID
- You've saved your work

✅ **Safer approach:**
1. Try `kill <PID>` first (graceful)
2. Wait a few seconds
3. If still running, use `kill -9 <PID>`

