Start-Process -FilePath "uvicorn" -ArgumentList "app.main:app --reload" -WorkingDirectory "backend"
Start-Process -FilePath "npm" -ArgumentList "run dev" -WorkingDirectory "frontend"
