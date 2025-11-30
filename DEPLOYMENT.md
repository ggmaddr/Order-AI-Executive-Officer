# Deployment Guide

Quick deployment instructions for Super Receptionist AI Agent.

## 🚀 Quick Deploy Options

### 1. Render.com (Easiest - Free Tier)

**Steps:**
1. Go to [render.com](https://render.com) and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `super-receptionist`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: `/` (leave empty)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
5. Add Environment Variables:
   ```
   PORT=8000
   MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/dbname
   MONGODB_DB_NAME=super_receptionist
   OPENAI_API_KEY=sk-your-key-here
   OPENAI_MODEL=gpt-4o-mini
   AI_PROVIDER=openai
   ```
6. Click "Create Web Service"
7. Wait for deployment (5-10 minutes)
8. Your app will be live at: `https://super-receptionist.onrender.com`

**Free Tier Limits:**
- 750 hours/month free
- Spins down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds

---

### 2. Railway.app (Fast & Simple)

**Steps:**
1. Go to [railway.app](https://railway.app) and sign up
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway auto-detects Python and deploys
5. Go to "Variables" tab and add:
   ```
   MONGODB_URL=mongodb+srv://...
   MONGODB_DB_NAME=super_receptionist
   OPENAI_API_KEY=sk-...
   OPENAI_MODEL=gpt-4o-mini
   AI_PROVIDER=openai
   PORT=8000
   ```
6. Railway automatically redeploys with new variables
7. Your app will be live at: `https://your-app-name.railway.app`

**Pricing:**
- $5/month for hobby plan
- Always-on, no spin-down

---

### 3. Fly.io (Docker-based)

**Steps:**
1. Install Fly CLI:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```
2. Login:
   ```bash
   fly auth login
   ```
3. Launch app:
   ```bash
   fly launch
   ```
   - Choose app name
   - Select region
   - Don't deploy yet (we'll set secrets first)
4. Set secrets:
   ```bash
   fly secrets set MONGODB_URL="mongodb+srv://..."
   fly secrets set MONGODB_DB_NAME="super_receptionist"
   fly secrets set OPENAI_API_KEY="sk-..."
   fly secrets set OPENAI_MODEL="gpt-4o-mini"
   fly secrets set AI_PROVIDER="openai"
   ```
5. Deploy:
   ```bash
   fly deploy
   ```
6. Your app will be live at: `https://your-app-name.fly.dev`

**Pricing:**
- Free tier: 3 shared VMs
- $1.94/month per VM after

---

### 4. Docker (Any Platform)

**Build and Run:**
```bash
# Build image
docker build -t super-receptionist .

# Run container
docker run -d \
  --name super-receptionist \
  -p 8000:8000 \
  -e MONGODB_URL="mongodb+srv://..." \
  -e MONGODB_DB_NAME="super_receptionist" \
  -e OPENAI_API_KEY="sk-..." \
  -e OPENAI_MODEL="gpt-4o-mini" \
  -e AI_PROVIDER="openai" \
  super-receptionist
```

**Or use docker-compose:**
```bash
# Create .env file with your variables
docker-compose up -d
```

---

## 📋 Pre-Deployment Checklist

- [ ] MongoDB Atlas cluster created (or local MongoDB running)
- [ ] MongoDB connection string ready
- [ ] OpenAI API key obtained
- [ ] GitHub repository pushed
- [ ] Environment variables documented

---

## 🔧 Post-Deployment

1. **Test the deployment:**
   - Visit your app URL
   - Check MongoDB connection in logs
   - Test chat functionality

2. **Monitor logs:**
   - Render: Dashboard → Logs
   - Railway: Deployments → View Logs
   - Fly.io: `fly logs`

3. **Set up custom domain (optional):**
   - Render: Settings → Custom Domain
   - Railway: Settings → Generate Domain
   - Fly.io: `fly certs add yourdomain.com`

---

## 🐛 Troubleshooting

### App won't start
- Check environment variables are set correctly
- Verify MongoDB connection string format
- Check logs for specific errors

### MongoDB connection fails
- Verify MongoDB Atlas network access (allow all IPs: 0.0.0.0/0)
- Check username/password in connection string
- Ensure database name is correct

### Port issues
- Render/Railway set PORT automatically
- For Docker, ensure port mapping is correct

### DNS errors
- The DNS patching in `database.py` should handle this
- If issues persist, check MongoDB Atlas SRV record format

---

## 💡 Tips

1. **Use MongoDB Atlas** for production (free tier available)
2. **Set up monitoring** on your chosen platform
3. **Enable auto-deploy** from main branch
4. **Use environment variables** - never commit secrets
5. **Test locally** before deploying

---

## 📞 Support

If deployment fails:
1. Check platform-specific documentation
2. Review application logs
3. Verify all environment variables
4. Test MongoDB connection separately

