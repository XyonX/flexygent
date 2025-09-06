#how to laod env file 

```
from dotenv import load_dotenv
import os

load_dotenv()  # reads .env file and puts values into os.environ
print(os.getenv("A"))  # now works, same as normal env var

```

