# Using Neon DB with Fintelligence

[Neon](https://neon.tech) is a serverless, fault-tolerant, and cloud-native PostgreSQL service. It's an excellent choice for Fintelligence as it:

1. Offers a generous free tier
2. Provides serverless scaling
3. Is fully compatible with PostgreSQL
4. Has easy setup and connection

## Setting Up Neon DB

### Step 1: Create a Neon Account

1. Go to [Neon.tech](https://neon.tech) and sign up for a free account
2. Verify your email address

### Step 2: Create a Project

1. After logging in, click "Create New Project"
2. Name your project "Fintelligence" (or any name you prefer)
3. Choose a region closest to you
4. Click "Create Project"

### Step 3: Get Connection String

1. After project creation, you'll see the connection details
2. Click "Connection String" to view the full PostgreSQL connection string
3. It should look like:
   ```
   postgresql://username:password@endpoint.neon.tech/dbname
   ```
4. Copy this connection string

### Step 4: Configure Your Application

1. Create a `.env` file in your Fintelligence project root
2. Add the following line with your Neon connection string:
   ```
   DATABASE_URL=postgresql://username:password@endpoint.neon.tech/dbname
   ```
3. Also add your Gemini API key:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   ```
4. Add a secret key for Flask:
   ```
   SECRET_KEY=your_secret_key_here
   ```

## Running the Application

Once your Neon DB is configured, start the application:

```bash
python run_locally.py
```

The application will automatically:
1. Connect to your Neon PostgreSQL database
2. Create all necessary tables
3. Start the Flask web server

## Troubleshooting

### Connection Issues

If you see connection errors, check the following:

1. Verify your connection string is correct
2. Ensure your IP is allowed in Neon's settings (Project → Settings → Network Access)
3. Check if the database was created in your Neon project

### Database Migration

If you need to reset your database:

1. Go to your Neon dashboard
2. Navigate to the project settings
3. Click on "Branches" and find your main branch
4. You can reset the database from the options menu

## Advantages of Using Neon DB

- No need to install PostgreSQL locally
- Database accessible from anywhere
- Built-in security and backups
- Serverless architecture means you pay only for what you use
- Simple scaling as your needs grow