# Deploy Backend on Render

Follow these steps to deploy the full backend (with college recommendations) on Render.

## Step 1: Create Render Account & Deploy

1. Go to [https://render.com](https://render.com)
2. Click **"Get Started"** and sign up with GitHub
3. Authorize Render to access your GitHub repositories

## Step 2: Create New Web Service

1. From Render Dashboard, click **"New +"** → **"Web Service"**
2. Click **"Connect a repository"**
3. Find and select **"jee-result-predictor"** repository
4. Click **"Connect"**

## Step 3: Configure the Service

Fill in these settings:

### Basic Settings
- **Name**: `jee-predictor-backend` (or any name you prefer)
- **Region**: Choose closest to you (Oregon is good for US)
- **Branch**: `main`
- **Root Directory**: Leave empty
- **Runtime**: `Python 3`

### Build & Start Commands
- **Build Command**:
  ```
  pip install -r requirements.txt
  ```
- **Start Command**:
  ```
  gunicorn --bind 0.0.0.0:$PORT --chdir backend app:app
  ```

### Plan
- Select **"Free"** plan
- Note: Free tier sleeps after 15 minutes of inactivity (first request after sleep takes ~30 seconds)

### Advanced (Optional)
- **Python Version**: `3.9.0`

## Step 4: Deploy

1. Click **"Create Web Service"**
2. Render will start building and deploying (takes 3-5 minutes)
3. Watch the logs in the dashboard
4. Wait for status to show **"Live"** with a green dot

## Step 5: Copy Your Backend URL

1. Once deployed, you'll see your service URL at the top
2. It will look like: `https://jee-predictor-backend.onrender.com`
3. **Copy this URL** (you'll need it in the next step)

## Step 6: Test the Backend

Open these URLs in your browser to verify:

1. **Health check**:
   ```
   https://your-backend-url.onrender.com/api/health
   ```
   Should return: `{"status":"ok"}`

2. **Test prediction** (use curl or Postman):
   ```bash
   curl -X POST https://your-backend-url.onrender.com/api/predict \
     -H "Content-Type: application/json" \
     -d '{"category":"OPEN","inputType":"marks","inputValue":250}'
   ```

## Step 7: Connect Frontend to Backend

1. Go to your **Vercel Dashboard**
2. Select your **jee-result-predictor** project
3. Go to **Settings** → **Environment Variables**
4. Click **"Add New"**
5. Enter:
   - **Name**: `REACT_APP_API_URL`
   - **Value**: `https://your-backend-url.onrender.com` (paste your Render URL)
   - **Environment**: Check all (Production, Preview, Development)
6. Click **"Save"**

## Step 8: Redeploy Frontend

1. Go to **Deployments** tab in Vercel
2. Click **"..."** (three dots) on the latest deployment
3. Click **"Redeploy"**
4. Wait for deployment to complete (~1 minute)

## Step 9: Test Everything!

Visit your Vercel app: `https://jee-result-and-college-predictor.vercel.app`

Test both features:
1. ✅ **Prediction** - Enter marks and get results
2. ✅ **College Recommendations** - Click the red button, select gender/state, and see colleges!

## Troubleshooting

### "Failed to connect to backend"
- Check that Render service status is "Live" (green)
- Verify the environment variable in Vercel is correct (no trailing slash)
- Try redeploying frontend on Vercel

### "Service Unavailable" or slow first request
- Free tier sleeps after 15 minutes
- First request wakes it up (~30 seconds)
- Subsequent requests are fast

### Build fails on Render
- Check build logs for errors
- Verify `requirements.txt` is in repo root
- Ensure `backend/app.py` exists

### CORS errors
- Backend already has CORS enabled
- Ensure Flask-CORS is in requirements.txt (it is!)

## Cost

- **Render Free Tier**:
  - 750 hours/month free
  - Service sleeps after 15 min inactivity
  - Perfect for this project!

## Upgrade (Optional)

If you want the backend to never sleep:
- Upgrade to **Starter plan**: $7/month
- Service stays awake 24/7
- Faster response times

## Summary

After completing these steps:
- ✅ Backend deployed on Render (with full CSV support)
- ✅ Frontend deployed on Vercel
- ✅ Both features working: Predictions + College Recommendations
- ✅ No "local network" errors
- ✅ Completely cloud-hosted!

---

Need help? Check Render logs at: https://dashboard.render.com
