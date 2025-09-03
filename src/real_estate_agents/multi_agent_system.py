import json
import logging
from typing import Dict, Any, List

# 导入各个智能体
from src.real_estate_agents.requirement_agent.agent import RequirementExtractionTool
from src.real_estate_agents.property_agent.agent import PropertyAgent
from src.real_estate_agents.matching_agent.agent import MatchingAgent

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealEstateMultiAgentSystem:
    """房地产多智能体系统 - 整合需求、房源和匹配推荐智能体"""
    
    def __init__(self):
        """初始化多智能体系统"""
        self.requirement_tool = RequirementExtractionTool()
        self.property_agent = PropertyAgent()
        self.matching_agent = MatchingAgent()
        
        logger.info("房地产多智能体系统初始化完成")
    
    def process_user_query(self, user_query: str) -> Dict[str, Any]:
        """
        处理用户查询并返回推荐结果
        
        Args:
            user_query: 用户自然语言查询
            
        Returns:
            推荐结果，包含匹配的房源和解释
        """
        try:
            # 步骤1：使用需求Agent解析用户需求
            logger.info(f"处理用户查询: {user_query}")
            structured_req = self.requirement_tool._run(None, None, None, None)
            requirements = json.loads(structured_req)
            logger.info(f"提取的结构化需求: {requirements}")
            
            # 步骤2：使用房源Agent搜索匹配的房源
            property_results = self.property_agent.search_properties(requirements)
            properties = property_results.get("properties", [])
            logger.info(f"找到 {len(properties)} 个匹配的房源")
            
            # 步骤3：使用匹配推荐Agent计算最佳匹配
            if len(properties) == 0:
                return {"message": "未找到符合您要求的房源", "recommendations": []}
                
            recommendations = self.matching_agent.recommend_properties(
                properties, requirements, top_k=3
            )
            
            # 步骤4：生成总结报告
            summary = self.matching_agent.generate_recommendation_summary(recommendations)
            logger.info(f"生成了 {len(recommendations)} 条推荐")
            
            return summary
        
        except Exception as e:
            logger.error(f"处理查询时出错: {e}")
            return {"error": str(e), "message": "处理您的请求时发生错误"}
