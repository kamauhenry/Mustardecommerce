<!-- For Development Purposes -->
# **Nginx Load Balancing for Django Project**

## **1️⃣ Install Nginx**
```bash
sudo apt update
sudo apt install nginx -y
```

## **2️⃣ Start and Enable Nginx**
```bash
sudo systemctl start nginx
sudo systemctl enable nginx
```

## **3️⃣ Verify Nginx Installation**
```bash
nginx -v  # Should return the installed version
```

---

## **4️⃣ Start Multiple Django Instances**
Run multiple Django application instances on different ports.

```bash
python manage.py runserver 8000 &
python manage.py runserver 8001 &
python manage.py runserver 8002 &
```

To verify, check:
```bash
curl https://mustardimports.co.ke
curl http://127.0.0.1:8001
curl http://127.0.0.1:8002
```

---

## **5️⃣ Configure Nginx for Load Balancing**
Edit the Nginx configuration file:
```bash
sudo nano /etc/nginx/sites-available/mustard_ecommerce
```

Add the following configuration:
```nginx
upstream django_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://django_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---

## **6️⃣ Enable the Configuration**
```bash
sudo ln -s /etc/nginx/sites-available/mustard_ecommerce /etc/nginx/sites-enabled/
```

Test Nginx configuration:
```bash
sudo nginx -t
```

If successful, restart Nginx:
```bash
sudo systemctl restart nginx
```

---

## **7️⃣ Allow Nginx Through Firewall (If Needed)**
```bash
sudo ufw allow 'Nginx Full'
sudo ufw reload
```

---

## **8️⃣ Test Load Balancing**
Visit your server’s public IP or domain:
```bash
http://yourdomain.com/
```
Or use curl to check:
```bash
curl -I http://yourdomain.com/
```

Nginx will distribute requests among the running Django instances automatically.

---

### **🎯 Summary**
✅ Installed and configured Nginx ✅ Started multiple Django instances ✅ Configured Nginx as a load balancer ✅ Verified functionality

---

🚀 **Your Django app is now load-balanced with Nginx!**
