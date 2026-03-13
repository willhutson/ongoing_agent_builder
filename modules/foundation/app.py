"""Foundation Module — Brief, Content, Copy, PromptHelper."""

import sys
import os

# Add modules root to path for shared imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shared.module_app import create_module_app
from shared.config import BaseModuleSettings
from agents import create_agents


class FoundationSettings(BaseModuleSettings):
    module_name: str = "foundation"
    module_port: int = 8001


settings = FoundationSettings()
app = create_module_app("foundation", create_agents, settings)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.module_port)
