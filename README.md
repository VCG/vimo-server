# vimo-server
vimo backend microservice






Install locally
```bash
cd vimo-server
virtualenv -p python3.9 venv
source venv/bin/activate
pip install -r requirements.txt
```


Run locally
```bash
python main.py
```

Deploy to Google Cloud Run
```bash
gcloud run deploy vimo-server --source . --allow-unauthenticated
```