"""Brand Module — Voice, Visual, Guidelines, Performance."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shared.module_app import create_module_app
from shared.config import BaseModuleSettings
from agents import create_agents


class BrandSettings(BaseModuleSettings):
    module_name: str = "brand"
    module_port: int = 8003


settings = BrandSettings()
app = create_module_app("brand", create_agents, settings)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.module_port)
