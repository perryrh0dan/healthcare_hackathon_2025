from .clients.llm import LLM
from .graphs.chatgraph import ChatGraph
from .graphs.questionsgraph import QuestionsGraph
from .graphs.dietgraph import DietGraph
from .config import logger

try:
    llm = LLM()
    graph = ChatGraph(llm.llm)
    questions_graph = QuestionsGraph(llm.llm)
    diet_graph = DietGraph(llm.llm)
    logger.info("API components initialized")
except Exception as e:
    logger.error(f"Failed to initialize API components: {e}")
    raise
