import sys
sys.path.insert(0, '.')

from shared.config import BaseModuleSettings
from shared.openrouter import OpenRouterClient
from shared.base_agent import BaseAgent, AgentContext, AgentResult

from foundation.agents import create_agents as f
print('foundation OK')
from studio.agents import create_agents as f
print('studio OK')
from brand.agents import create_agents as f
print('brand OK')
from research.agents import create_agents as f
print('research OK')
from strategy.agents import create_agents as f
print('strategy OK')
from operations.agents import create_agents as f
print('operations OK')
from client.agents import create_agents as f
print('client OK')
from distribution.agents import create_agents as f
print('distribution OK')
from wizard.agent import create_wizard
print('wizard OK')

print('All modules imported successfully')
