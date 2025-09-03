import json
import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)

class PropertyInfo(BaseModel):
    """房源信息模型"""
    property_id: str = Field(description="房源ID")
    price: float = Field(description="房源价格")
    area: str = Field(description="房源所在区域")
    size: float = Field(description="房源面积（平方米）")
    bedrooms: int = Field(description="卧室数量")
    bathrooms: int = Field(description="浴室数量")
    school_district: str = Field(description="学区信息")
    commute_time: int = Field(description="到市中心通勤时间（分钟）")
    address: str = Field(description="详细地址")
    listing_date: str = Field(description="挂牌日期")
    property_type: str = Field(description="房产类型（公寓/别墅/联排等）")

class PropertySearchTool(BaseTool):
    """房源搜索工具"""
    name: str = "search_properties"
    description: str = "根据结构化需求搜索匹配的房源信息，包括价格、区域、学区等条件。"
    
    def __init__(self):
        super().__init__()
    
    def _run(self, budget_min: Optional[float] = None, budget_max: Optional[float] = None, 
             area: Optional[str] = None, school_district: Optional[str] = None, 
             max_commute_time: Optional[int] = None) -> str:
        """
        模拟房源搜索功能
        在实际应用中，这里会连接到MLS/贝壳/安居客等数据源
        """
        # 模拟房源数据
        mock_properties = [
            {
                "property_id": "P001",
                "price": 3500000,
                "area": "朝阳区",
                "size": 120.5,
                "bedrooms": 3,
                "bathrooms": 2,
                "school_district": "朝阳实验小学",
                "commute_time": 25,
                "address": "朝阳区建国路88号",
                "listing_date": "2024-01-15",
                "property_type": "公寓"
            },
            {
                "property_id": "P002",
                "price": 4200000,
                "area": "海淀区",
                "size": 95.0,
                "bedrooms": 2,
                "bathrooms": 1,
                "school_district": "中关村第一小学",
                "commute_time": 30,
                "address": "海淀区中关村大街123号",
                "listing_date": "2024-01-20",
                "property_type": "公寓"
            },
            {
                "property_id": "P003",
                "price": 2800000,
                "area": "丰台区",
                "size": 85.0,
                "bedrooms": 2,
                "bathrooms": 1,
                "school_district": "丰台第五小学",
                "commute_time": 35,
                "address": "丰台区南三环西路456号",
                "listing_date": "2024-01-18",
                "property_type": "公寓"
            },
            {
                "property_id": "P004",
                "price": 5800000,
                "area": "西城区",
                "size": 140.0,
                "bedrooms": 3,
                "bathrooms": 2,
                "school_district": "北京第二实验小学",
                "commute_time": 15,
                "address": "西城区金融街789号",
                "listing_date": "2024-01-22",
                "property_type": "公寓"
            },
            {
                "property_id": "P005",
                "price": 3200000,
                "area": "朝阳区",
                "size": 110.0,
                "bedrooms": 3,
                "bathrooms": 2,
                "school_district": "朝阳外国语学校",
                "commute_time": 28,
                "address": "朝阳区望京西路321号",
                "listing_date": "2024-01-25",
                "property_type": "公寓"
            }
        ]
        
        # 根据条件筛选房源
        filtered_properties = []
        for prop in mock_properties:
            # 预算筛选
            if budget_min and prop["price"] < budget_min:
                continue
            if budget_max and prop["price"] > budget_max:
                continue
            
            # 区域筛选
            if area and area not in prop["area"]:
                continue
            
            # 学区筛选
            if school_district and school_district not in prop["school_district"]:
                continue
            
            # 通勤时间筛选
            if max_commute_time and prop["commute_time"] > max_commute_time:
                continue
            
            filtered_properties.append(prop)
        
        return json.dumps({
            "total_count": len(filtered_properties),
            "properties": filtered_properties
        }, ensure_ascii=False, indent=2)

    async def _arun(self, budget_min: Optional[float] = None, budget_max: Optional[float] = None, 
                   area: Optional[str] = None, school_district: Optional[str] = None, 
                   max_commute_time: Optional[int] = None) -> str:
        return self._run(budget_min, budget_max, area, school_district, max_commute_time)

class MarketAnalysisTool(BaseTool):
    """市场分析工具"""
    name: str = "analyze_market"
    description: str = "分析指定区域的房地产市场情况，包括平均价格、成交量、价格趋势等。"
    
    def __init__(self):
        super().__init__()
    
    def _run(self, area: str) -> str:
        """
        模拟市场分析功能
        在实际应用中，这里会分析真实的市场数据
        """
        # 模拟市场数据
        market_data = {
            "朝阳区": {
                "average_price_per_sqm": 65000,
                "price_trend": "上涨3.2%",
                "monthly_transactions": 1250,
                "inventory_level": "中等",
                "popular_school_districts": ["朝阳实验小学", "朝阳外国语学校"],
                "average_commute_time": 27
            },
            "海淀区": {
                "average_price_per_sqm": 72000,
                "price_trend": "上涨2.8%",
                "monthly_transactions": 980,
                "inventory_level": "较低",
                "popular_school_districts": ["中关村第一小学", "人大附小"],
                "average_commute_time": 32
            },
            "西城区": {
                "average_price_per_sqm": 85000,
                "price_trend": "上涨1.5%",
                "monthly_transactions": 650,
                "inventory_level": "低",
                "popular_school_districts": ["北京第二实验小学", "西城区师范附小"],
                "average_commute_time": 18
            },
            "丰台区": {
                "average_price_per_sqm": 48000,
                "price_trend": "上涨4.1%",
                "monthly_transactions": 1100,
                "inventory_level": "较高",
                "popular_school_districts": ["丰台第五小学", "丰台实验小学"],
                "average_commute_time": 38
            }
        }
        
        analysis = market_data.get(area, {
            "average_price_per_sqm": 55000,
            "price_trend": "持平",
            "monthly_transactions": 800,
            "inventory_level": "中等",
            "popular_school_districts": ["区域重点小学"],
            "average_commute_time": 35
        })
        
        return json.dumps({
            "area": area,
            "market_analysis": analysis,
            "analysis_date": "2024-01-26"
        }, ensure_ascii=False, indent=2)

    async def _arun(self, area: str) -> str:
        return self._run(area)

class PropertyAgent:
    """房源Agent - 负责抓取和查询房源信息"""
    
    def __init__(self):
        self.tools = [
            PropertySearchTool(),
            MarketAnalysisTool()
        ]
        logger.info("房源Agent初始化完成")
    
    def search_properties(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据需求搜索房源
        
        Args:
            requirements: 结构化需求，包含预算、区域、学区、通勤等信息
            
        Returns:
            搜索结果，包含匹配的房源列表
        """
        try:
            # 解析预算范围
            budget_str = requirements.get("budget", "")
            budget_min, budget_max = None, None
            
            if budget_str:
                # 简单的预算解析逻辑
                if "万" in budget_str:
                    # 处理"300-500万"这样的格式
                    budget_str = budget_str.replace("万", "")
                    if "-" in budget_str:
                        parts = budget_str.split("-")
                        if len(parts) == 2:
                            budget_min = float(parts[0].strip()) * 10000
                            budget_max = float(parts[1].strip()) * 10000
                    else:
                        # 处理"500万以内"这样的格式
                        if "以内" in budget_str:
                            budget_max = float(budget_str.replace("以内", "").strip()) * 10000
            
            # 提取其他条件
            area = requirements.get("area", "")
            school_district = requirements.get("school_district", "")
            
            # 解析通勤要求
            commute_str = requirements.get("commute", "")
            max_commute_time = None
            if commute_str and "分钟" in commute_str:
                # 提取数字
                import re
                numbers = re.findall(r'\d+', commute_str)
                if numbers:
                    max_commute_time = int(numbers[0])
            
            # 搜索房源
            search_tool = PropertySearchTool()
            search_result = search_tool._run(
                budget_min=budget_min,
                budget_max=budget_max,
                area=area,
                school_district=school_district,
                max_commute_time=max_commute_time
            )
            
            return json.loads(search_result)
            
        except Exception as e:
            logger.error(f"房源搜索失败: {e}")
            return {"total_count": 0, "properties": [], "error": str(e)}
    
    def analyze_market(self, area: str) -> Dict[str, Any]:
        """
        分析指定区域的市场情况
        
        Args:
            area: 区域名称
            
        Returns:
            市场分析结果
        """
        try:
            analysis_tool = MarketAnalysisTool()
            analysis_result = analysis_tool._run(area)
            return json.loads(analysis_result)
        except Exception as e:
            logger.error(f"市场分析失败: {e}")
            return {"error": str(e)}
    
    def get_property_details(self, property_id: str) -> Dict[str, Any]:
        """
        获取房源详细信息
        
        Args:
            property_id: 房源ID
            
        Returns:
            房源详细信息
        """
        # 这里可以实现更详细的房源信息获取逻辑
        # 包括历史价格、周边配套、交通情况等
        return {
            "property_id": property_id,
            "detailed_info": "详细信息获取功能待实现"
        }
