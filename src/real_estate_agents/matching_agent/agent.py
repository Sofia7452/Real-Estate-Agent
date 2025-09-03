import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class MatchingScore(BaseModel):
    """匹配分数模型"""
    property_id: str = Field(description="房源ID")
    total_score: float = Field(description="总匹配分数")
    budget_score: float = Field(description="预算匹配分数")
    area_score: float = Field(description="区域匹配分数")
    school_score: float = Field(description="学区匹配分数")
    commute_score: float = Field(description="通勤匹配分数")
    recommendation_reason: str = Field(description="推荐理由")

class PropertyRecommendation(BaseModel):
    """房源推荐模型"""
    property_info: Dict[str, Any] = Field(description="房源信息")
    matching_score: MatchingScore = Field(description="匹配分数详情")
    rank: int = Field(description="推荐排名")

class MatchingAgent:
    """匹配和推荐Agent - 负责计算匹配度并推荐房源"""
    
    def __init__(self, budget_weight: float = 0.4, area_weight: float = 0.2, 
                 school_weight: float = 0.3, commute_weight: float = 0.3):
        """
        初始化匹配Agent
        
        Args:
            budget_weight: 预算权重 (默认40%)
            area_weight: 区域权重 (默认20%)
            school_weight: 学区权重 (默认30%)
            commute_weight: 通勤权重 (默认30%)
        """
        # 确保权重总和为1.0
        total_weight = budget_weight + area_weight + school_weight + commute_weight
        self.budget_weight = budget_weight / total_weight
        self.area_weight = area_weight / total_weight
        self.school_weight = school_weight / total_weight
        self.commute_weight = commute_weight / total_weight
        
        logger.info(f"匹配Agent初始化完成 - 权重配置: 预算{self.budget_weight:.1%}, "
                   f"区域{self.area_weight:.1%}, 学区{self.school_weight:.1%}, "
                   f"通勤{self.commute_weight:.1%}")
    
    def calculate_budget_score(self, property_price: float, budget_min: Optional[float], 
                              budget_max: Optional[float]) -> float:
        """
        计算预算匹配分数
        
        Args:
            property_price: 房源价格
            budget_min: 预算下限
            budget_max: 预算上限
            
        Returns:
            预算匹配分数 (0-1)
        """
        if budget_min is None and budget_max is None:
            return 0.5  # 没有预算要求时给中等分数
        
        if budget_max is None:
            # 只有下限
            if property_price >= budget_min:
                return 1.0
            else:
                return max(0.0, property_price / budget_min)
        
        if budget_min is None:
            # 只有上限
            if property_price <= budget_max:
                return 1.0
            else:
                return max(0.0, 1.0 - (property_price - budget_max) / budget_max)
        
        # 有上下限
        if budget_min <= property_price <= budget_max:
            return 1.0
        elif property_price < budget_min:
            return max(0.0, property_price / budget_min)
        else:
            return max(0.0, 1.0 - (property_price - budget_max) / budget_max)
    
    def calculate_area_score(self, property_area: str, required_area: str) -> float:
        """
        计算区域匹配分数
        
        Args:
            property_area: 房源所在区域
            required_area: 用户要求的区域
            
        Returns:
            区域匹配分数 (0-1)
        """
        if not required_area:
            return 0.5  # 没有区域要求时给中等分数
        
        if required_area in property_area or property_area in required_area:
            return 1.0
        
        # 可以添加更复杂的区域相似度计算
        # 比如相邻区域给较高分数等
        area_similarity_map = {
            "朝阳区": ["海淀区", "东城区"],
            "海淀区": ["朝阳区", "西城区"],
            "西城区": ["海淀区", "东城区"],
            "东城区": ["西城区", "朝阳区"],
            "丰台区": ["朝阳区", "西城区"]
        }
        
        similar_areas = area_similarity_map.get(required_area, [])
        if property_area in similar_areas:
            return 0.7
        
        return 0.2  # 不相关区域给低分
    
    def calculate_school_score(self, property_school: str, required_school: str) -> float:
        """
        计算学区匹配分数
        
        Args:
            property_school: 房源学区
            required_school: 用户要求的学区
            
        Returns:
            学区匹配分数 (0-1)
        """
        if not required_school:
            return 0.5  # 没有学区要求时给中等分数
        
        if required_school in property_school or property_school in required_school:
            return 1.0
        
        # 学区质量评分（模拟数据）
        school_quality_map = {
            "北京第二实验小学": 0.95,
            "中关村第一小学": 0.90,
            "朝阳实验小学": 0.85,
            "朝阳外国语学校": 0.88,
            "丰台第五小学": 0.75,
            "丰台实验小学": 0.78
        }
        
        property_quality = school_quality_map.get(property_school, 0.6)
        required_quality = school_quality_map.get(required_school, 0.6)
        
        # 基于学区质量相似度计算分数
        quality_diff = abs(property_quality - required_quality)
        return max(0.0, 1.0 - quality_diff * 2)
    
    def calculate_commute_score(self, property_commute: int, required_commute: Optional[int]) -> float:
        """
        计算通勤匹配分数
        
        Args:
            property_commute: 房源通勤时间（分钟）
            required_commute: 用户要求的最大通勤时间（分钟）
            
        Returns:
            通勤匹配分数 (0-1)
        """
        if required_commute is None:
            # 没有通勤要求时，通勤时间越短分数越高
            return max(0.0, 1.0 - property_commute / 60.0)
        
        if property_commute <= required_commute:
            return 1.0
        else:
            # 超出要求时，根据超出程度降分
            excess_ratio = (property_commute - required_commute) / required_commute
            return max(0.0, 1.0 - excess_ratio)
    
    def calculate_matching_score(self, property_info: Dict[str, Any], 
                               requirements: Dict[str, Any]) -> MatchingScore:
        """
        计算单个房源的匹配分数
        
        Args:
            property_info: 房源信息
            requirements: 用户需求
            
        Returns:
            匹配分数详情
        """
        # 解析预算要求
        budget_str = requirements.get("budget", "")
        budget_min, budget_max = None, None
        
        if budget_str and "万" in budget_str:
            budget_str = budget_str.replace("万", "")
            if "-" in budget_str:
                parts = budget_str.split("-")
                if len(parts) == 2:
                    budget_min = float(parts[0].strip()) * 10000
                    budget_max = float(parts[1].strip()) * 10000
            elif "以内" in budget_str:
                budget_max = float(budget_str.replace("以内", "").strip()) * 10000
        
        # 解析通勤要求
        commute_str = requirements.get("commute", "")
        max_commute_time = None
        if commute_str and "分钟" in commute_str:
            numbers = re.findall(r'\d+', commute_str)
            if numbers:
                max_commute_time = int(numbers[0])
        
        # 计算各项分数
        budget_score = self.calculate_budget_score(
            property_info["price"], budget_min, budget_max
        )
        
        area_score = self.calculate_area_score(
            property_info["area"], requirements.get("area", "")
        )
        
        school_score = self.calculate_school_score(
            property_info["school_district"], requirements.get("school_district", "")
        )
        
        commute_score = self.calculate_commute_score(
            property_info["commute_time"], max_commute_time
        )
        
        # 计算总分
        total_score = (
            budget_score * self.budget_weight +
            area_score * self.area_weight +
            school_score * self.school_weight +
            commute_score * self.commute_weight
        )
        
        # 生成推荐理由
        reason_parts = []
        if budget_score >= 0.8:
            reason_parts.append("价格符合预算")
        elif budget_score >= 0.6:
            reason_parts.append("价格基本符合预算")
        
        if area_score >= 0.8:
            reason_parts.append("位置优越")
        elif area_score >= 0.6:
            reason_parts.append("位置较好")
        
        if school_score >= 0.8:
            reason_parts.append("学区优质")
        elif school_score >= 0.6:
            reason_parts.append("学区不错")
        
        if commute_score >= 0.8:
            reason_parts.append("通勤便利")
        elif commute_score >= 0.6:
            reason_parts.append("通勤较为便利")
        
        if not reason_parts:
            reason_parts.append("综合条件一般")
        
        recommendation_reason = "，".join(reason_parts)
        
        return MatchingScore(
            property_id=property_info["property_id"],
            total_score=total_score,
            budget_score=budget_score,
            area_score=area_score,
            school_score=school_score,
            commute_score=commute_score,
            recommendation_reason=recommendation_reason
        )
    
    def recommend_properties(self, properties: List[Dict[str, Any]], 
                           requirements: Dict[str, Any], 
                           top_k: int = 5) -> List[PropertyRecommendation]:
        """
        推荐房源
        
        Args:
            properties: 候选房源列表
            requirements: 用户需求
            top_k: 推荐房源数量
            
        Returns:
            推荐房源列表，按匹配度排序
        """
        try:
            # 计算每个房源的匹配分数
            scored_properties = []
            for prop in properties:
                matching_score = self.calculate_matching_score(prop, requirements)
                scored_properties.append((prop, matching_score))
            
            # 按总分排序
            scored_properties.sort(key=lambda x: x[1].total_score, reverse=True)
            
            # 生成推荐列表
            recommendations = []
            for rank, (prop, score) in enumerate(scored_properties[:top_k], 1):
                recommendation = PropertyRecommendation(
                    property_info=prop,
                    matching_score=score,
                    rank=rank
                )
                recommendations.append(recommendation)
            
            logger.info(f"成功生成{len(recommendations)}个房源推荐")
            return recommendations
            
        except Exception as e:
            logger.error(f"房源推荐失败: {e}")
            return []
    
    def generate_recommendation_summary(self, recommendations: List[PropertyRecommendation]) -> Dict[str, Any]:
        """
        生成推荐总结
        
        Args:
            recommendations: 推荐房源列表
            
        Returns:
            推荐总结信息
        """
        if not recommendations:
            return {"message": "未找到合适的房源推荐"}
        
        # 计算统计信息
        total_count = len(recommendations)
        avg_score = sum(rec.matching_score.total_score for rec in recommendations) / total_count
        price_range = {
            "min": min(rec.property_info["price"] for rec in recommendations),
            "max": max(rec.property_info["price"] for rec in recommendations)
        }
        
        # 生成推荐总结
        summary = {
            "total_recommendations": total_count,
            "average_matching_score": round(avg_score, 2),
            "price_range": price_range,
            "top_recommendation": {
                "property_id": recommendations[0].property_info["property_id"],
                "address": recommendations[0].property_info["address"],
                "price": recommendations[0].property_info["price"],
                "matching_score": round(recommendations[0].matching_score.total_score, 2),
                "reason": recommendations[0].matching_score.recommendation_reason
            },
            "recommendations": [
                {
                    "rank": rec.rank,
                    "property_id": rec.property_info["property_id"],
                    "address": rec.property_info["address"],
                    "price": rec.property_info["price"],
                    "area": rec.property_info["area"],
                    "school_district": rec.property_info["school_district"],
                    "commute_time": rec.property_info["commute_time"],
                    "matching_score": round(rec.matching_score.total_score, 2),
                    "score_breakdown": {
                        "budget": round(rec.matching_score.budget_score, 2),
                        "area": round(rec.matching_score.area_score, 2),
                        "school": round(rec.matching_score.school_score, 2),
                        "commute": round(rec.matching_score.commute_score, 2)
                    },
                    "reason": rec.matching_score.recommendation_reason
                }
                for rec in recommendations
            ]
        }
        
        return summary
