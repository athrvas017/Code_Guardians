import multiprocessing

# Worker configuration
# For Free Tier Render (512MB RAM), use only 1 worker to save memory
workers = 1 

# Timeout configuration
# Machine Learning models can take time to process or load, giving it more breathing room
timeout = 120

# Preload application
# This loads the application code before the worker processes are forked.
# This allows memory to be shared between workers (if we had more than 1)
# and ensures models are loaded at startup, not on the first request.
preload_app = True

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
