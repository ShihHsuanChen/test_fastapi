import uvicorn
import app
config = uvicorn.Config("app:app", port=8000, log_level="info")
server = uvicorn.Server(config)
server.run()
