# Azure Deployment Guide for Mutual Fund API

## Prerequisites

- Azure account with active subscription
- Azure CLI installed (or use Azure Portal)
- Git repository pushed to GitHub/Azure Repos

---

## Choosing Your Deployment Strategy

### Development vs Production Deployment

You have **two main options** for deploying this application:

#### Option A: Single Environment (Development Branch)

Deploy directly from the `development` branch for testing and development purposes.

**Pros:**

- ✅ Quick setup (one Azure App Service)
- ✅ Lower cost (~$13/month or free)
- ✅ Perfect for testing before going live

**Cons:**

- ⚠️ No separation between dev and prod
- ⚠️ Changes go live immediately

**Recommended for:** Testing, POC, or low-traffic production

#### Option B: Dual Environment (Best Practice)

Create **two** separate Azure App Services for development and production.

**Setup:**

```
Development Environment
├── App Name: mf-api-dev
├── Branch: development
├── FLASK_ENV: development
├── URL: mf-api-dev.azurewebsites.net
└── Cost: ~$13/month (or Free tier)

Production Environment
├── App Name: mf-api-prod
├── Branch: main (after merging from development)
├── FLASK_ENV: production
├── URL: mf-api-prod.azurewebsites.net
└── Cost: ~$25-70/month (B2 or S1)
```

**Pros:**

- ✅ Complete isolation between dev and prod
- ✅ Test changes safely before production
- ✅ Different configurations for each environment
- ✅ Industry best practice

**Cons:**

- 💰 Higher cost (two apps)
- 🔧 Slightly more setup

**Recommended for:** Production applications with regular updates

---

## Quick Start: Deploy from Development Branch

**For immediate testing**, follow this guide to deploy from the `development` branch:

### Environment Variable Configurations

#### For Development Deployment

```bash
MONGODB_URI = mongodb+srv://anupamsoni27:Mystuff8358%401@india-01.kwer3ek.mongodb.net/
MONGODB_DB_NAME = mf_data
FLASK_ENV = development       # ← Keep development mode
SECRET_KEY = dev-secret-key   # ← Can use simpler key
CORS_ORIGINS = http://localhost:4200,https://dev-angular.com
LOG_LEVEL = DEBUG             # ← More verbose logging
```

#### For Production Deployment

```bash
MONGODB_URI = mongodb+srv://anupamsoni27:Mystuff8358%401@india-01.kwer3ek.mongodb.net/
MONGODB_DB_NAME = mf_data
FLASK_ENV = production              # ← Production mode
SECRET_KEY = <secure-random-key>    # ← Must be strong and random
CORS_ORIGINS = https://your-angular-app.com
LOG_LEVEL = WARNING                 # ← Minimal logging
```

> **Important:** Generate production SECRET_KEY with:
>
> ```bash
> python3 -c "import secrets; print(secrets.token_hex(32))"
> ```

---

## Deployment Options

### Option 1: Azure Portal (Recommended for Beginners)

#### Step 1: Create App Service

1. **Login to Azure Portal**: https://portal.azure.com
2. **Create Resource** → Search for "App Service" → Click **Create**
3. **Configure Basic Settings**:

   - **Subscription**: Choose your subscription
   - **Resource Group**: Create new (e.g., `mf-api-rg`)
   - **Name**: Your app name - will become `your-name.azurewebsites.net`
     - For Development: `mf-api-dev` → `mf-api-dev.azurewebsites.net`
     - For Production: `mf-api-prod` → `mf-api-prod.azurewebsites.net`
   - **Publish**: `Code`
   - **Runtime stack**: `Python 3.11` or `Python 3.12`
   - **Operating System**: `Linux`
   - **Region**: Choose closest to your users
   - **Pricing**:
     - For Development: `F1` (Free) or `B1` (Basic ~$13/month)
     - For Production: `B2` (~$25/month) or `S1` (~$70/month)

4. Click **Review + Create** → **Create**

#### Step 2: Configure Deployment

1. Go to your App Service → **Deployment Center**
2. **Source**: Choose your repository (GitHub, Azure Repos, etc.)
3. **Authorize** Azure to access your repository
4. **Organization**: Your GitHub account
5. **Repository**: `mf-apiv0`
6. **Branch**: Choose based on your strategy:
   - For **Development**: Select `development` ← **Currently available**
   - For **Production**: Select `main` (merge development first)
7. Click **Save**

Azure will automatically:

- Install dependencies from `requirements.txt`
- Run the startup command from `startup.txt`
- Deploy your app
- Auto-redeploy on every push to the selected branch

#### Step 3: Configure Environment Variables

1. Go to **Configuration** → **Application Settings**
2. Click **+ New application setting** and add:

**For Development Deployment:**

```
MONGODB_URI = mongodb+srv://anupamsoni27:Mystuff8358%401@india-01.kwer3ek.mongodb.net/
MONGODB_DB_NAME = mf_data
FLASK_ENV = development
SECRET_KEY = dev-secret-key-change-me
CORS_ORIGINS = http://localhost:4200
LOG_LEVEL = DEBUG
```

**For Production Deployment:**

```
MONGODB_URI = mongodb+srv://anupamsoni27:Mystuff8358%401@india-01.kwer3ek.mongodb.net/
MONGODB_DB_NAME = mf_data
FLASK_ENV = production
SECRET_KEY = <generate-strong-random-key>
CORS_ORIGINS = https://your-angular-app.com,https://www.your-angular-app.com
LOG_LEVEL = WARNING
```

3. Click **Save**

#### Step 4: Configure Startup Command

1. Go to **Configuration** → **General settings**
2. **Startup Command**: `gunicorn --config gunicorn.conf.py app:app`
3. Click **Save**

#### Step 5: Verify Deployment

1. Go to **Overview** → Click your app URL
2. Should see: `{"service": "Mutual Fund API", "version": "1.0.0", ...}`
3. Test health endpoint: `https://your-app.azurewebsites.net/health`

---

### Option 2: Azure CLI (Advanced)

```bash
# 1. Login to Azure
az login

# 2. Create resource group
az group create --name mf-api-rg --location eastus

# 3. Create App Service plan
az appservice plan create \
  --name mf-api-plan \
  --resource-group mf-api-rg \
  --sku B1 \
  --is-linux

# 4. Create web app
az webapp create \
  --resource-group mf-api-rg \
  --plan mf-api-plan \
  --name mf-api-prod \
  --runtime "PYTHON:3.11"

# 5. Configure deployment from GitHub
az webapp deployment source config \
  --name mf-api-prod \
  --resource-group mf-api-rg \
  --repo-url https://github.com/Anupamsoni27/mf-apiv0 \
  --branch development \
  --manual-integration

# 6. Set environment variables
az webapp config appsettings set \
  --resource-group mf-api-rg \
  --name mf-api-prod \
  --settings \
    MONGODB_URI="mongodb+srv://..." \
    MONGODB_DB_NAME="mf_data" \
    FLASK_ENV="production" \
    CORS_ORIGINS="https://your-frontend.com"

# 7. Set startup command
az webapp config set \
  --resource-group mf-api-rg \
  --name mf-api-prod \
  --startup-file "gunicorn --config gunicorn.conf.py app:app"

# 8. View logs
az webapp log tail --name mf-api-prod --resource-group mf-api-rg
```

---

## Environment Variables Reference

| Variable          | Description                       | Example                                                                  |
| ----------------- | --------------------------------- | ------------------------------------------------------------------------ |
| `MONGODB_URI`     | MongoDB connection string         | `mongodb+srv://user:pass@cluster.mongodb.net/`                           |
| `MONGODB_DB_NAME` | Database name                     | `mf_data`                                                                |
| `FLASK_ENV`       | Environment                       | `production`                                                             |
| `SECRET_KEY`      | Flask secret key                  | Generate with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `CORS_ORIGINS`    | Allowed origins (comma-separated) | `https://myapp.com,https://www.myapp.com`                                |
| `LOG_LEVEL`       | Logging level                     | `WARNING` or `INFO`                                                      |
| `PORT`            | Port (Azure sets automatically)   | `8000`                                                                   |

---

## Setting Up Dual Environments (Recommended)

If you want both development and production environments, create **two** App Services following the same steps above:

### 1. Development Environment

**App Service Name:** `mf-api-dev`

**Configuration:**

```bash
# Branch: development
# Environment Variables:
FLASK_ENV=development
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:4200
SECRET_KEY=dev-secret-key
```

**Use for:**

- Testing new features
- Integration testing
- Pre-production validation

### 2. Production Environment

**App Service Name:** `mf-api-prod`

**Configuration:**

```bash
# Branch: main (merge from development first)
# Environment Variables:
FLASK_ENV=production
LOG_LEVEL=WARNING
CORS_ORIGINS=https://your-angular-app.com
SECRET_KEY=<strong-random-key>
```

**Use for:**

- Live user traffic
- Stable releases only

### Workflow

```
1. Develop on `development` branch
   ↓
2. Push to GitHub
   ↓
3. Auto-deploys to mf-api-dev.azurewebsites.net
   ↓
4. Test thoroughly
   ↓
5. Merge development → main
   ↓
6. Auto-deploys to mf-api-prod.azurewebsites.net
```

---

## Health Endpoints

### `/health` - Basic health check

```bash
curl https://your-app.azurewebsites.net/health
```

Response:

```json
{
  "status": "healthy",
  "service": "mf-api",
  "version": "1.0.0"
}
```

### `/ready` - Readiness check (with DB verification)

```bash
curl https://your-app.azurewebsites.net/ready
```

Response:

```json
{
  "status": "ready",
  "database": "connected"
}
```

### `/` - Root endpoint

```bash
curl https://your-app.azurewebsites.net/
```

---

## Production Checklist

### Before Deployment

- [x] Gunicorn added to requirements.txt
- [x] Production configuration created
- [x] Health check endpoints added
- [x] Startup command configured
- [ ] Generate production SECRET_KEY
- [ ] Update CORS_ORIGINS with production domain
- [ ] Set FLASK_ENV=production

### After Deployment

- [ ] Test all API endpoints
- [ ] Verify database connectivity
- [ ] Check health endpoints
- [ ] Monitor logs for errors
- [ ] Test from Angular frontend
- [ ] Set up monitoring/alerts (optional)

---

## Monitoring & Logs

### View Logs in Portal

1. Go to App Service → **Log stream**
2. See real-time logs

### View Logs via CLI

```bash
az webapp log tail --name mf-api-prod --resource-group mf-api-rg
```

### Enable Application Insights (Optional)

1. Go to App Service → **Application Insights**
2. Click **Turn on Application Insights**
3. Creates automatic monitoring and alerts

---

## Scaling

### Vertical Scaling (More CPU/RAM)

1. Go to **Scale up (App Service plan)**
2. Choose higher tier (B2, B3, S1, P1V2, etc.)

### Horizontal Scaling (More Instances)

1. Go to **Scale out (App Service plan)**
2. Set instance count or enable auto-scaling

### Worker Configuration

Edit `gunicorn.conf.py`:

```python
# More workers = more concurrent requests
workers = 4  # Adjust based on your plan
```

---

## Troubleshooting

### App won't start

1. Check **Log stream** for errors
2. Verify startup command is correct
3. Ensure all dependencies in requirements.txt
4. Check environment variables are set

### Database connection fails

1. Verify MONGODB_URI is correct
2. Check MongoDB Atlas allows Azure IPs (usually add `0.0.0.0/0` in Network Access)
3. Test `/ready` endpoint

### CORS errors from Angular

1. Add your Angular domain to CORS_ORIGINS
2. Restart app after changing settings
3. Format: `https://myapp.com` (no trailing slash)

### 502 Bad Gateway

1. App is starting (wait 30-60 seconds)
2. Check logs for Python errors
3. Verify gunicorn is running

---

## Cost Optimization

| Tier               | Price/Month | Use Case                     |
| ------------------ | ----------- | ---------------------------- |
| **F1 (Free)**      | $0          | Testing only (limited hours) |
| **B1 (Basic)**     | ~$13        | Development/staging          |
| **B2 (Basic)**     | ~$25        | Small production             |
| **S1 (Standard)**  | ~$70        | Production with auto-scaling |
| **P1V2 (Premium)** | ~$100       | High traffic production      |

Start with **B1** for production testing, scale up as needed.

---

## Updating the App

### Automatic (Recommended)

Push to your `development` branch - Azure auto-deploys

```bash
git add .
git commit -m "Update feature"
git push origin development
```

### Manual

1. Go to **Deployment Center**
2. Click **Sync** to pull latest code

---

## Production URL Structure

After deployment:

- **API Base**: `https://mf-api-prod.azurewebsites.net`
- **Health**: `https://mf-api-prod.azurewebsites.net/health`
- **Get Stocks**: `https://mf-api-prod.azurewebsites.net/getAllStocks`
- **Get Funds**: `https://mf-api-prod.azurewebsites.net/getAllFunds`

Update your Angular services to use this URL!

---

## Security Best Practices

1. **Generate strong SECRET_KEY**:

   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Restrict MongoDB access**:

   - Go to MongoDB Atlas → Network Access
   - Add Azure IP ranges or use connection string with user/pass

3. **Set CORS properly**:

   - Only allow your actual domain
   - Don't use `*` in production

4. **Enable HTTPS**:

   - Azure provides free SSL
   - Redirect HTTP → HTTPS in Azure settings

5. **Monitor logs**:
   - Set LOG_LEVEL=WARNING in production
   - Review logs regularly

---

## Next Steps

1. Deploy to Azure following steps above
2. Test all endpoints
3. Update Angular app with new API URL
4. Monitor for 24 hours
5. Set up alerts (optional)

Need help? Check Azure's extensive documentation or App Service diagnostics in the portal!
