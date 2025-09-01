from mangum import Mangum
from api import app

# Create a Lambda handler using Mangum
handler = Mangum(app, lifespan="off")
