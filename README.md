## Basic instructions
download pfdata.zip, 
add the .env to the project root
and the Model.joblib to root/mlmodel 
> **_NOTE:_** change the .env database credentials  

Run this to install dependencies
```
uv sync
```

Then run this to start the api
```
uv run uvicorn quietsignal_backend.main:app --reload
```
