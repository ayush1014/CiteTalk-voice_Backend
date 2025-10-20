"""
LangGraph orchestration service for AI agent workflow.
"""
from typing import Dict, Any, List, Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from services.rag_service import rag_service


class AgentState(TypedDict):
    """State for the agent workflow."""
    query: str
    intent: str
    context_docs: List[Dict[str, Any]]
    response: str
    session_id: str
    metadata: Dict[str, Any]


class LangGraphService:
    """
    Service for LangGraph workflow orchestration.
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            openai_api_key=settings.openai_api_key,
            temperature=0.7
        )
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow.
        
        Workflow:
        1. Intent Classification Node
        2. RAG Retrieval Node (if needed)
        3. Response Generation Node
        """
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("classify_intent", self.classify_intent)
        workflow.add_node("retrieve_context", self.retrieve_context)
        workflow.add_node("generate_response", self.generate_response)
        
        # Define edges
        workflow.set_entry_point("classify_intent")
        
        # Conditional edge based on intent
        workflow.add_conditional_edges(
            "classify_intent",
            self.route_based_on_intent,
            {
                "rag": "retrieve_context",
                "direct": "generate_response"
            }
        )
        
        workflow.add_edge("retrieve_context", "generate_response")
        workflow.add_edge("generate_response", END)
        
        return workflow.compile()
    
    async def classify_intent(
        self,
        state: AgentState
    ) -> AgentState:
        """
        Classify user intent to determine workflow path.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with intent
        """
        query = state["query"]
        
        prompt = f"""Classify the user's intent for the following query.
Choose one of: 'rag' (needs context retrieval), 'direct' (can answer directly).

Query: {query}

Intent (respond with just 'rag' or 'direct'):"""
        
        response = await self.llm.ainvoke(prompt)
        intent = response.content.strip().lower()
        
        # Default to 'rag' if unclear
        if intent not in ["rag", "direct"]:
            intent = "rag"
        
        state["intent"] = intent
        return state
    
    def route_based_on_intent(self, state: AgentState) -> str:
        """
        Route to next node based on intent.
        
        Args:
            state: Current agent state
            
        Returns:
            Next node name
        """
        intent = state.get("intent", "rag")
        return intent
    
    async def retrieve_context(
        self,
        state: AgentState
    ) -> AgentState:
        """
        Retrieve relevant context using RAG.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with context documents
        """
        # Note: This requires a database session
        # In practice, we'll pass this through metadata
        db = state.get("metadata", {}).get("db")
        
        if db:
            docs = await rag_service.retrieve_relevant_docs(
                state["query"],
                db
            )
            state["context_docs"] = docs
        else:
            state["context_docs"] = []
        
        return state
    
    async def generate_response(
        self,
        state: AgentState
    ) -> AgentState:
        """
        Generate final response using LLM.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with response
        """
        query = state["query"]
        context_docs = state.get("context_docs", [])
        
        if context_docs:
            # Use RAG service to generate response with context
            response = await rag_service.generate_response(query, context_docs)
        else:
            # Generate direct response
            prompt = f"""You are a helpful AI assistant. Answer the user's question naturally and conversationally.

User Question: {query}

Answer:"""
            
            llm_response = await self.llm.ainvoke(prompt)
            response = llm_response.content
        
        state["response"] = response
        return state
    
    async def run(
        self,
        query: str,
        session_id: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Run the complete agent workflow.
        
        Args:
            query: User query
            session_id: Conversation session ID
            db: Database session
            
        Returns:
            Final state with response
        """
        initial_state = {
            "query": query,
            "intent": "",
            "context_docs": [],
            "response": "",
            "session_id": session_id,
            "metadata": {"db": db}
        }
        
        final_state = await self.graph.ainvoke(initial_state)
        return final_state


# Global LangGraph service instance
langgraph_service = LangGraphService()
