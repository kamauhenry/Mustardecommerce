# **Mustard Imports**

This project integrates Django REST Framework for the backend and Vue.js with Vite for the frontend.

## **Installation and Setup**

### **Backend (Django REST Framework)**

1.**Clone the repository**

```bash
git clone <repo-url>
cd mustard-imports
```

2.**Create and activate a virtual environment**

```bash
python -m venv venv
```

3.**Activate the environment:**

```text
On Windows
venv\Scripts\activate

On Mac/Linux
source venv/bin/activate
```

4.**Install dependencies:**

```python
pip install -r requirements.txt
```

5.**Set up environment variables (if needed):**
Create a `.env` file and add necessary environment variables.

6.**Run database migrations:**

```python
python manage.py makemigrations
python manage.py migrate
```

7.**Create a superuser (for admin access):**

```python
python manage.py createsuperuser
```

8.**Run the Django development server:**

```python
python manage.py runserver
```

### **Frontend (Vue.js with Vite)**

#### Navigate to the frontend directory:

```bash
cd frontend/vue-project
```

#### Install dependencies:

```bash
npm install
```

#### Start the development server:

```bash
npm run dev
```

This will run Vue at `http://localhost:5173/`.

Build for production:

```bash
npm run build
```

The built files will be located in `frontend/vue-project/dist`.

### **Serving Vue with Django**

To serve the built Vue app with Django:

- Ensure `vite.config.js` outputs to `dist`.
- Update Django settings:

```python
STATICFILES_DIRS = [BASE_DIR.parent / 'frontend' / 'vue-project' / 'dist']
```

- Run collectstatic:

```python
python manage.py collectstatic
```

- Serve the app using Django’s static handling.

### **API Testing with Django REST Framework**

You can access the API endpoints at:
<https://mustardimports.co.ke/api/>

Use Postman or Django’s browsable API to interact with the backend.

### **Deployment Notes**

- Ensure that `ALLOWED_HOSTS` is configured properly in `settings.py`.
- Use Gunicorn for running Django in production.
- Use Nginx or another web server to serve static files efficiently.

Now you’re ready to develop with both Django REST and Vue! 🚀


### **Mpesa Integrated sandbpxing we will change to live in production
**


## Environment Configuration and Ngrok Setup

### `.env` Configuration
Add the following to your `.env` file to configure the M-Pesa integration:

MPESA_BASE_URL=https://sandbox.safaricom.co.ke  # Use https://api.safaricom.co.ke for production

- **Note**: Ensure the `MPESA_BASE_URL` includes the `https://` scheme to avoid URL errors in your application.

### Running Ngrok
To expose your local development server (e.g., `http://localhost:5173`) to the internet for testing, use ngrok. Below is an example of running ngrok and its output:

#### Steps
1. **Start your local server**: Run `npm run dev` to start your Vue.js app (default port: `5173`).
2. **Run ngrok**: In a terminal, navigate to the ngrok executable folder and run:

   ./ngrok http 5173

3. **Output**: You’ll see something like this:

   ngrok by @inconshreveable

   Session Status   online
   Account          Your Name (Plan: Free)
   Version          3.6.0
   Region           United States (us)
   Web Interface    http://127.0.0.1:4040
   Forwarding       https://abcd-123-456-789.ngrok-free.app -> http://localhost:5173

#### Details
- **Forwarding URL**: Use `https://abcd-123-456-789.ngrok-free.app` (replace with your actual ngrok URL) as the `CALLBACK_URL` in your `.env` for M-Pesa testing:

  CALLBACK_URL=https://abcd-123-456-789.ngrok-free.app/mpesa-callback/

- **Web Interface**: Visit `http://127.0.0.1:4040` to inspect HTTP traffic and debug requests.

