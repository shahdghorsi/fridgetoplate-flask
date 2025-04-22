# Deploying FridgeToPlate to Render

This guide provides detailed instructions for deploying the FridgeToPlate Flask application to Render.

## Prerequisites

- A [Render](https://render.com/) account (free tier is sufficient)
- A GitHub account
- Git installed on your computer

## Step 1: Prepare Your GitHub Repository

1. Create a new GitHub repository named `fridgetoplate-flask`
2. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/yourusername/fridgetoplate-flask.git
   cd fridgetoplate-flask
   ```
3. Extract the contents of the FridgeToPlate-Python.zip file to this directory
4. Commit and push the files to GitHub:
   ```bash
   git add .
   git commit -m "Initial commit of FridgeToPlate Flask application"
   git push origin main
   ```

## Step 2: Create a New Web Service on Render

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
   - **Start Command**: `gunicorn -c gunicorn.conf.py app:app`
   - **Plan**: Free

5. Click "Create Web Service"

## Step 3: Configure Environment Variables

After your service is created, you need to set up environment variables:

1. In your Render dashboard, select your web service
2. Go to the "Environment" tab
3. Add the following environment variables:
   - `FLASK_CONFIG`: `production`
   - `SECRET_KEY`: Generate a secure random string (e.g., `python -c "import secrets; print(secrets.token_hex(16))"`)
   - `USE_MOCK_VISION`: `True` (set to `False` if using real Google Cloud Vision API)
   - `USE_MOCK_RECIPES`: `True` (set to `False` if using real Spoonacular API)

4. If using real APIs, add these variables as well:
   - `GOOGLE_CLOUD_VISION_API_KEY`: Your Google Cloud Vision API key
   - `SPOONACULAR_API_KEY`: Your Spoonacular API key

5. Click "Save Changes"

## Step 4: Set Up a Database (Optional)

For a more robust solution, you can set up a PostgreSQL database:

1. In your Render dashboard, click "New +" and select "PostgreSQL"
2. Configure your database:
   - **Name**: `fridgetoplate-db`
   - **Database**: `fridgetoplate`
   - **User**: Leave as default
   - **Region**: Same as your web service
   - **Plan**: Free

3. After creation, go to your web service's "Environment" tab
4. Add a new environment variable:
   - `DATABASE_URL`: Copy the Internal Database URL from your PostgreSQL service
5. Click "Save Changes"

## Step 5: Verify Deployment

1. Wait for your service to finish deploying (this may take a few minutes)
2. Once deployed, click the URL provided by Render (e.g., `https://fridgetoplate.onrender.com`)
3. Verify that your application is working correctly:
   - Check that all pages load properly
   - Test the image upload functionality
   - Test recipe suggestions
   - Test fusion recipe generation

## Troubleshooting

If you encounter issues:

1. **Application Error**: Check the logs in your Render dashboard for error messages
2. **Database Connection Issues**: Verify your DATABASE_URL environment variable
3. **Missing Static Files**: Make sure your static files are properly referenced
4. **API Issues**: Check your API keys and environment variables

## Updating Your Application

To update your application:

1. Make changes to your local repository
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update application"
   git push origin main
   ```
3. Render will automatically detect the changes and redeploy your application

## Important Notes

- The free tier of Render has some limitations:
  - Your service will spin down after 15 minutes of inactivity
  - The first request after inactivity may take up to 30 seconds to respond
  - There are monthly usage limits

- For a production application, consider upgrading to a paid plan for better performance and reliability
