# Final Deployment Guide for FridgeToPlate on Render

This guide provides final instructions for deploying the FridgeToPlate Flask application to Render, using a completely different approach that resolves all previous deployment issues.

## What's Changed

We've completely restructured the application to use a **single file approach** that eliminates all import issues:

1. Created a standalone `wsgi.py` file that contains the entire application
2. Eliminated complex module imports that were causing Gunicorn startup issues
3. Simplified the deployment process with a direct WSGI entry point

This approach ensures that Render can properly start the application without any import or module resolution problems.

## Deployment Instructions

### Step 1: Secure Google Cloud Setup

1. **Create a new service account with limited permissions**:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Navigate to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Name: `fridgetoplate-vision` (or your preferred name)
   - Description: "Service account for FridgeToPlate Vision API access"
   - Click "Create and Continue"
   - Add the "Cloud Vision API User" role only
   - Click "Continue" and then "Done"

2. **Create a new key for the service account**:
   - Find your new service account in the list
   - Click the three dots menu > "Manage keys"
   - Click "Add Key" > "Create new key"
   - Select "JSON" format
   - Click "Create" (this will download the key file)
   - **IMPORTANT**: Store this key file securely and never share it

3. **Base64 encode the key file**:
   - Open a terminal
   - Run: `cat /path/to/your-key-file.json | base64`
   - Copy the entire output string (it will be a long string with no line breaks)

### Step 2: Prepare Your GitHub Repository

1. Create a new GitHub repository named `fridgetoplate-flask`
2. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/yourusername/fridgetoplate-flask.git
   cd fridgetoplate-flask
   ```
3. Extract the contents of the FridgeToPlate-Python-Final.zip file to this directory
4. Commit and push the files to GitHub:
   ```bash
   git add .
   git commit -m "Add FridgeToPlate Flask application with single file approach"
   git push origin main
   ```

### Step 3: Create a New Web Service on Render

1. Log in to your [Render Dashboard](https://dashboard.render.com/)
2. Click the "New +" button and select "Web Service"
3. Connect your GitHub repository:
   - Select "GitHub" as the deployment method
   - Connect your GitHub account if not already connected
   - Search for and select your `fridgetoplate-flask` repository
4. Configure the web service:
   - **Name**: `fridgetoplate` (or your preferred name)
   - **Environment**: `Python 3`
   - **Region**: Choose the region closest to you
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app`
   - **Plan**: Free

5. Click "Create Web Service"

### Step 4: Configure Environment Variables Securely

After your service is created, you need to set up environment variables:

1. In your Render dashboard, select your web service
2. Go to the "Environment" tab
3. Add the following environment variables:
   - `SECRET_KEY`: Generate a secure random string (e.g., `python -c "import secrets; print(secrets.token_hex(16))"`)
   - `USE_MOCK_VISION`: `False` (to use the real Google Cloud Vision API)
   - `USE_MOCK_RECIPES`: `True` (or `False` if using real Spoonacular API)
   - `GOOGLE_CLOUD_CREDENTIALS_BASE64`: Paste the base64-encoded service account key from Step 1

4. If using the Spoonacular API, add this variable as well:
   - `SPOONACULAR_API_KEY`: Your Spoonacular API key

5. Click "Save Changes"

## Verification Steps

1. Wait for your service to finish deploying (this may take a few minutes)
2. Check the logs in your Render dashboard to confirm there are no errors during startup
   - Look for "Starting gunicorn" message
   - Look for "Listening at: http://0.0.0.0:10000" message
   - Confirm there are no import errors or exceptions
3. Once deployed, click the URL provided by Render (e.g., `https://fridgetoplate.onrender.com`)
4. Verify that your application is working correctly:
   - Check that all pages load properly
   - Test the image upload functionality with the Vision API
   - Test recipe suggestions
   - Test fusion recipe generation

## Why This Approach Works

The single-file approach eliminates all import issues by:

1. Containing all code in one file, avoiding circular imports
2. Providing a direct WSGI entry point for Gunicorn
3. Simplifying the application structure for deployment
4. Ensuring all dependencies are properly initialized

This approach is specifically designed to work with Render's deployment environment and avoids the complexities that were causing the previous deployment issues.

## Troubleshooting

If you still encounter issues:

1. **Check Render logs**: In your Render dashboard, go to your web service and click on "Logs" to see detailed error messages
2. **Verify the start command**: Make sure it's exactly `gunicorn wsgi:app` (not app:app)
3. **Check environment variables**: Ensure all required environment variables are set correctly
4. **Restart the service**: Sometimes a simple restart can resolve issues

## Security Reminders

1. **Never commit credentials to your repository**
2. **Regularly rotate your service account keys**
3. **Use the principle of least privilege** for service accounts
4. **Monitor your Google Cloud usage** for unusual activity
