import json
import logging
import sys
from typing import Any, Dict, List, Optional

# 添加NeMo-Agent-Toolkit到系统路径
sys.path.append("NeMo-Agent-Toolkit")

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from nat.agent.react_agent.agent import ReActAgentGraph
from nat.agent.react_agent.register import ReActAgentWorkflowConfig
from nat.builder.builder import Builder
from nat.builder.framework_enum import LLMFrameworkEnum
from nat.builder.function_info import FunctionInfo
from nat.cli.register_workflow import register_function
from nat.data_models.api_server import ChatRequest, ChatResponse
from nat.data_models.component_ref import LLMRef
from nat.data_models.function import FunctionBaseConfig
from nat.utils.type_converter import GlobalTypeConverter

logger = logging.getLogger(__name__)

# Define the structured output for the Requirement Agent
class StructuredRequirement(BaseModel):
    budget: Optional[str] = Field(default=None, description="用户预算范围")
    area: Optional[str] = Field(default=None, description="用户期望的区域")
    school_district: Optional[str] = Field(default=None, description="用户对学区的要求")
    commute: Optional[str] = Field(default=None, description="用户对通勤的要求")

class RequirementExtractionTool(BaseTool):
    name: str = "extract_requirements"
    description: str = "从用户自然语言输入中提取购房需求，包括预算、区域、学区和通勤，并以JSON格式返回。"
    
    def __init__(self):
        super().__init__(args_schema=StructuredRequirement)
    
    def _run(self, budget: Optional[str] = None, area: Optional[str] = None, 
             school_district: Optional[str] = None, commute: Optional[str] = None) -> str:
        # This method would typically call an NLP model or a more sophisticated parsing logic
        # For now, we'll just return the extracted information as a JSON string
        extracted_data = {
            "budget": budget or "",
            "area": area or "",
            "school_district": school_district or "",
            "commute": commute or ""
        }
        return json.dumps(extracted_data, ensure_ascii=False)

    async def _arun(self, budget: Optional[str] = None, area: Optional[str] = None, 
                   school_district: Optional[str] = None, commute: Optional[str] = None) -> str:
        return self._run(budget, area, school_district, commute)

class RequirementAgentConfig(FunctionBaseConfig):
    """需求Agent的配置类"""
    llm_name: LLMRef = Field(description="用于需求Agent的LLM模型。")
    verbose: bool = Field(default=False, description="设置需求Agent日志的详细程度。")
    system_prompt: Optional[str] = Field(default=None, description="需求Agent使用的系统提示。")
    additional_instructions: Optional[str] = Field(default=None, description="提供给需求Agent的额外指令。")
    max_history: int = Field(default=15, description="对话历史中保留的最大消息数量。")
    log_response_max_chars: int = Field(default=1000, description="日志中显示工具响应的最大字符数。")
    use_openai_api: bool = Field(default=False, description="是否使用OpenAI API的输入/输出类型。")

@register_function(config_type=RequirementAgentConfig, framework_wrappers=[LLMFrameworkEnum.LANGCHAIN])
async def requirement_agent_workflow(config: RequirementAgentConfig, builder: Builder):
    from langchain.schema import BaseMessage
    from langchain_core.messages import trim_messages
    from langgraph.graph.graph import CompiledGraph

    from nat.agent.base import AGENT_LOG_PREFIX
    from nat.agent.react_agent.agent import ReActGraphState
    from nat.agent.react_agent.agent import create_react_agent_prompt

    # Create a prompt for the Requirement Agent
    # We will use a custom system prompt for this agent
    system_prompt_template = """
    你是一个购房需求解析专家。你的任务是理解用户提供的自然语言购房需求，并从中提取出结构化的信息，包括预算、区域、学区和通勤。
    如果用户没有提供某个信息，请将其留空。
    你需要使用提供的工具来提取这些信息。

    {tools}

    你只能使用以下两种格式之一进行响应。
    使用以下格式精确地要求人类使用工具：

    Question: 你必须回答的输入问题
    Thought: 你应该总是思考要做什么
    Action: 要采取的行动，应该是 [{tool_names}] 中的一个
    Action Input: 行动的输入（如果没有必需的输入，则包含 "Action Input: None"）
    Observation: 等待人类响应工具的结果，不要假设响应

    ... (这个 Thought/Action/Action Input/Observation 可以重复 N 次。如果你不需要使用工具，或者在要求人类使用任何工具并等待人类响应后，你可能知道最终答案。)
    一旦你有了最终答案，请使用以下格式：

    Thought: 我现在知道最终答案了
    Final Answer: 原始输入问题的最终答案
    """

    user_prompt_template = """
    Previous conversation history:
    {chat_history}

    Question: {question}
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt_template),
        ("user", user_prompt_template)
    ])

    # Load LLM
    llm = await builder.get_llm(config.llm_name, wrapper_type=LLMFrameworkEnum.LANGCHAIN)

    # Define tools for this agent
    tools: List[BaseTool] = [RequirementExtractionTool()]

    # Construct the ReAct Agent Graph
    graph: CompiledGraph = await ReActAgentGraph(
        llm=llm,
        prompt=prompt,
        tools=tools,
        use_tool_schema=True, # Always include tool input schema for better extraction
        detailed_logs=config.verbose,
        log_response_max_chars=config.log_response_max_chars,
        retry_agent_response_parsing_errors=True,
        parse_agent_response_max_retries=1,
        tool_call_max_retries=1,
        pass_tool_call_errors_to_agent=True,
        normalize_tool_input_quotes=True
    ).build_graph()

    async def _response_fn(input_message: ChatRequest) -> ChatResponse:
        try:
            messages: List[BaseMessage] = trim_messages(messages=[m.model_dump() for m in input_message.messages],
                                                        max_tokens=config.max_history,
                                                        strategy="last",
                                                        token_counter=len,
                                                        start_on="human",
                                                        include_system=True)

            state = ReActGraphState(messages=messages)
            state = await graph.ainvoke(state, config={'recursion_limit': 15 * 2}) # Allow enough recursion for tool calls

            state = ReActGraphState(**state)
            output_message = state.messages[-1]
            return ChatResponse.from_string(str(output_message.content))

        except Exception as ex:
            logger.exception(f"{AGENT_LOG_PREFIX} Requirement Agent failed with exception: {ex}")
            if config.verbose:
                return ChatResponse.from_string(str(ex))
            return ChatResponse.from_string("需求解析Agent出现问题。")

    if config.use_openai_api:
        yield FunctionInfo.from_fn(_response_fn, description="解析用户购房需求并提取结构化信息。")
    else:
        async def _str_api_fn(input_message: str) -> str:
            oai_input = GlobalTypeConverter.get().try_convert(input_message, to_type=ChatRequest)
            oai_output = await _response_fn(oai_input)
            return GlobalTypeConverter.get().try_convert(oai_output, to_type=str)
        yield FunctionInfo.from_fn(_str_api_fn, description="解析用户购房需求并提取结构化信息。")
