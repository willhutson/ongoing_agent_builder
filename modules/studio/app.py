"""Studio Module — Image, Video, Presentation."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shared.module_app import create_module_app
from shared.config import BaseModuleSettings
from agents import create_agents


class StudioSettings(BaseModuleSettings):
    module_name: str = "studio"
    module_port: int = 8002


settings = StudioSettings()
app = create_module_app("studio", create_agents, settings)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.module_port)
